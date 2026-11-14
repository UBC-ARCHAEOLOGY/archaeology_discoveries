#!/usr/bin/env python3
"""Read-only evidence intake. Standard library; never writes editorial content."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = 1


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def doi(value):
    value = re.sub(r'^https?://(?:dx\.)?doi\.org/|^doi:\s*', '', value or '', flags=re.I).strip().lower()
    return value if re.fullmatch(r'10\.\d{4,9}/\S+', value) else None


def url(value):
    p = urllib.parse.urlsplit(value or '')
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        return None
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith('utm_') and k not in ('fbclid', 'gclid')]
    return urllib.parse.urlunsplit(('https', p.netloc.lower(), p.path.rstrip('/'), urllib.parse.urlencode(sorted(query)), ''))


def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def year(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2})?(?:-\d{2})?', value):
        return None
    try:
        date.fromisoformat(value + ('-01-01' if len(value) == 4 else '-01' if len(value) == 7 else ''))
        return int(value[:4])
    except ValueError:
        return None


def parts_date(value):
    p = (value or {}).get('date-parts', [[]])[0]
    return '-'.join(str(x).zfill(4 if i == 0 else 2) for i, x in enumerate(p)) or None


def get_json(address):
    # API-only transport: institutional pages are not fetched by this implementation.
    p = urllib.parse.urlsplit(address)
    if p.scheme != 'https' or p.hostname not in ('api.crossref.org', 'api.openalex.org'):
        raise ValueError('Only registered metadata API hosts are enabled')
    request = urllib.request.Request(address, headers={'User-Agent': 'archaeology-monitor-phase2a/1.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def crossref(item, source, observed):
    dates = {k: parts_date(item.get(k)) for k in ('published-online', 'published-print', 'published', 'created', 'indexed')}
    pubs = [v for k, v in dates.items() if k.startswith('published') and v]
    return {'source_id': source, 'title': ' '.join(item.get('title', [])), 'doi': item.get('DOI'),
            'url': item.get('URL'), 'publication_date': min(pubs) if pubs else None,
            'announcement_date': None, 'source_dates': dates,
            'authors': item.get('author', []), 'container': item.get('container-title', []),
            'retrieved_at': observed, 'claims': {'en': re.sub('<[^>]+>', '', item.get('abstract', ''))},
            'metadata_provider': 'crossref', 'provider_record': item}


def openalex(item, source, observed):
    return {'source_id': source, 'title': item.get('title') or '', 'doi': item.get('doi'),
            'url': (item.get('primary_location') or {}).get('landing_page_url') or item.get('id'),
            'publication_date': item.get('publication_date'), 'announcement_date': None,
            'retrieved_at': observed, 'metadata_provider': 'openalex', 'provider_record': item,
            'claims': {'en': ''}}


def parse_feed(body, source, observed):
    """Offline/permitted feed adapter. Raw timestamps retained, never equated with first announcement."""
    tree = ET.fromstring(body)
    result = []
    for item in list(tree.findall('.//item')) + list(tree.findall('{http://www.w3.org/2005/Atom}entry')):
        def field(name):
            node = item.find(name)
            if node is None:
                node = item.find('{http://www.w3.org/2005/Atom}' + name)
            return node
        def content(name):
            node = field(name)
            return ''.join(node.itertext()).strip() if node is not None else ''
        link = field('link')
        result.append({'source_id': source, 'title': content('title'),
                       'url': (link.get('href') or link.text) if link is not None else None,
                       'announcement_date': None, 'feed_timestamp': content('pubDate') or content('published'),
                       'retrieved_at': observed, 'claims': {'en': content('description') or content('summary')}})
    return result


def retrieve(registry, config, state, as_of, fetch=get_json):
    records, access = [], []
    new_state = dict(state)
    for source in registry['sources']:
        sid = source['id']
        if not source.get('enabled') or source['adapter'] not in ('crossref', 'openalex'):
            access.append({'source': sid, 'status': 'not_fetched', 'reason': source['access_note']})
            continue
        previous = state.get(sid)
        start = max(config['start_date'], (date.fromisoformat(previous) - timedelta(days=config['overlap_days'])).isoformat()) if previous else config['start_date']
        page, count, complete = '*', 0, False
        try:
            while count < config['max_pages_per_source']:
                params = {'rows': config['page_size'], 'cursor': page,
                          'filter': f'from-index-date:{start},until-index-date:{as_of}',
                          'query': config['query']}
                endpoint = 'https://api.crossref.org/works'
                if source['adapter'] == 'crossref' and source.get('issn'):
                    endpoint = 'https://api.crossref.org/journals/' + source['issn'] + '/works'
                    params.pop('query')
                if source['adapter'] == 'openalex':
                    endpoint = 'https://api.openalex.org/works'
                    params = {'per-page': config['page_size'], 'cursor': page, 'search': config['query'],
                              'filter': f'from_publication_date:{config["start_date"]},to_publication_date:{as_of}'}
                    if config.get('openalex_api_key'):
                        raise ValueError('Supply OpenAlex credentials via a custom transport; never persist secrets')
                data = fetch(endpoint + '?' + urllib.parse.urlencode(params))
                message = data.get('message', {}) if source['adapter'] == 'crossref' else data
                items = message.get('items', []) if source['adapter'] == 'crossref' else message.get('results', [])
                adapter = crossref if source['adapter'] == 'crossref' else openalex
                records.extend(adapter(i, sid, as_of) for i in items)
                count += 1
                next_page = message.get('next-cursor') if source['adapter'] == 'crossref' else message.get('meta', {}).get('next_cursor')
                if not items or not next_page or len(items) < config['page_size']:
                    complete = True
                    break
                if next_page == page:
                    break
                page = next_page
            # Advance only on a fully exhausted interval; a capped/failed source must be retried.
            if complete and source['adapter'] == 'crossref':
                new_state[sid] = as_of
            access.append({'source': sid, 'status': 'complete' if complete else 'bounded_incomplete', 'pages': count,
                           'since': start, 'until': as_of, 'watermark_advanced': complete and source['adapter'] == 'crossref'})
        except (OSError, ValueError, KeyError) as exc:
            access.append({'source': sid, 'status': 'unavailable', 'error': str(exc)[:250], 'watermark_advanced': False})
    return records, access, new_state


def classify(r, target_year):
    history = r.get('earlier_history', [])
    if r.get('legacy_material') and year(r.get('publication_date')) == target_year:
        return 'Reanalysis', ['verify_major_interpretive_gain']
    if r.get('first_announcement_claim') and year(r.get('announcement_date')) == target_year:
        return 'first_public_announcement', ['verify_no_earlier_announcement']
    if r.get('substantive_publication_claim') and year(r.get('publication_date')) == target_year:
        return 'first_substantive_publication', ['verify_substantive_increment', 'verify_earlier_history' if history else 'earlier_history_missing']
    return 'unresolved', ['2026_date_alone_does_not_establish_eligibility']


def tags(r, config):
    text = ' '.join([r.get('title', ''), r.get('claims', {}).get('en', ''), r.get('geographic_context', ''), r.get('chronological_context', ''), r.get('importance_context', {}).get('en', '')]).casefold()
    result = {k: list(r.get('tags', {}).get(k, [])) for k in ('geographic', 'chronological', 'discovery_type', 'evidence_type')}
    matches = []
    for dimension, rules in config['tag_rules'].items():
        for label, terms in rules.items():
            terms_found = [term for term in terms if (re.search(r'(?<!\w)' + re.escape(term.casefold()) + r'(?!\w)', text) if dimension == 'geographic' else term.casefold() in text)]
            if terms_found and label not in result[dimension]:
                result[dimension].append(label)
                matches.append({'dimension': dimension, 'tag': label, 'matched_terms': terms_found})
    return result, matches


def prepare(raw, config, verification=None):
    r = json.loads(json.dumps(raw))
    r['doi_normalized'], r['url_normalized'] = doi(r.get('doi')), url(r.get('url'))
    r['uncertainty_flags'] = ['classification_is_proposal', 'importance_requires_human_review']
    for field in ('publication_date', 'announcement_date'):
        if r.get(field) and year(r[field]) is None:
            r['uncertainty_flags'].append('invalid_' + field)
    if not any(r.get('claims', {}).values()):
        r['uncertainty_flags'].append('discovery_claims_missing_metadata_only')
    if not r.get('fieldwork_status'):
        r['uncertainty_flags'].append('fieldwork_status_unresolved')
    if r.get('doi') and not r['doi_normalized']:
        r['uncertainty_flags'].append('invalid_doi_syntax')
    if not r['doi_normalized']:
        r['uncertainty_flags'].append('doi_missing_or_invalid')
    if not r['url_normalized']:
        r['uncertainty_flags'].append('url_missing_or_invalid')
    v = (verification or {}).get(r['doi_normalized'])
    r['independent_metadata'] = v or None
    if v and r.get('metadata_provider') == 'crossref':
        r['uncertainty_flags'].append('verification_same_provider_not_independent')
    r['metadata_status'] = 'unverified'
    if v:
        conflicts = []
        if doi(v.get('DOI')) != r['doi_normalized']:
            conflicts.append('doi_mismatch')
        if norm(' '.join(v.get('title', []))) != norm(r.get('publication_title') or r.get('title', '')):
            conflicts.append('title_mismatch')
        verified_dates = [parts_date(v.get(k)) for k in ('published', 'published-online', 'published-print')]
        verified_years = {year(d) for d in verified_dates if d}
        if year(r.get('publication_date')) not in verified_years:
            conflicts.append('publication_date_mismatch')
        r['uncertainty_flags'].extend(conflicts)
        r['metadata_status'] = 'conflicting' if conflicts else 'metadata_matched'
    else:
        r['uncertainty_flags'].append('independent_metadata_unavailable')
    r['url_status'] = 'syntax_only_not_resolved'
    if v and r['url_normalized']:
        if doi(urllib.parse.unquote(urllib.parse.urlsplit(r['url_normalized']).path.lstrip('/'))) == r['doi_normalized'] or r['url_normalized'] == url(v.get('URL')):
            r['url_status'] = 'metadata_link_matched_not_http_resolved'
        else:
            r['uncertainty_flags'].append('url_not_matched_to_verified_metadata')
    r['classification_proposal'], flags = classify(r, config['target_year'])
    r['uncertainty_flags'].extend(flags)
    if not r.get('earlier_history'):
        r['uncertainty_flags'].append('earlier_history_not_documented')
    r['tags'], r['tag_rule_matches'] = tags(r, config)
    r['editorial_review'] = 'provisional_requires_human_review'
    r['importance_proposal'] = {
        'en': 'Assess whether these contextual findings change an archaeological question; remove record claims and method prestige before judging long-term value.',
        'zh': '拟议评估：核查情境证据是否改变重要考古问题；不以纪录、方法或期刊声望代替长期学术价值判断。'}
    if not r.get('claims', {}).get('zh'):
        r.setdefault('claims', {})['zh'] = '尚无人工核对的中文发现摘要；请参阅所引原文。'
        r['uncertainty_flags'].append('chinese_summary_pending')
    years = [year(r.get(k)) for k in ('publication_date', 'announcement_date')]
    r['screening'] = 'possible_2026' if config['target_year'] in years else 'outside_year_or_undated'
    if not any(r['tags'].values()):
        r['uncertainty_flags'].append('possible_non_archaeology_false_positive')
    r['intake_priority'] = 'field_context_first' if any(x in r['tags']['evidence_type'] for x in ('excavation', 'survey', 'stratigraphy')) else 'context_review'
    # No prestige, citation count, impact factor or molecular-method score.
    r['record_id'] = digest({k: raw.get(k) for k in ('source_id', 'title', 'doi', 'url')})[:16]
    return r


def deduplicate(records):
    """Connected components; preserve all evidence and conflict flags, never silently merge claims."""
    parents = list(range(len(records)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    seen, edges = {}, []
    for i, r in enumerate(records):
        keys = [('doi', r.get('doi_normalized')), ('url', r.get('url_normalized')),
                ('title', norm(r.get('publication_title') or r.get('title', '')))]
        # Explicit curated project keys only. Site proximity alone is unsafe.
        keys.append(('project', norm(r.get('project_key', ''))))
        for kind, key in keys:
            if not key:
                continue
            if (kind, key) in seen:
                j = seen[kind, key]
                parents[find(i)] = find(j)
                edges.append({'left': records[j]['record_id'], 'right': r['record_id'], 'basis': kind,
                              'needs_review': kind in ('title', 'project')})
            else:
                seen[kind, key] = i
    groups = {}
    for i, r in enumerate(records):
        groups.setdefault(find(i), []).append(r)
    output = []
    for rows in groups.values():
        dois = {r['doi_normalized'] for r in rows if r['doi_normalized']}
        output.append({'candidate_id': digest(sorted(r['record_id'] for r in rows))[:16], 'records': rows,
                       'duplicate_count': len(rows)-1, 'identity_conflict': len(dois) > 1,
                       'review_required': True})
    return output, edges


def report(raw, config, access, verification=None):
    records = [prepare(r, config, verification) for r in raw]
    groups, edges = deduplicate(records)
    counts = {dim: dict(Counter(t for g in groups for t in set(t for r in g['records'] for t in r['tags'][dim])))
              for dim in ('geographic', 'chronological', 'discovery_type', 'evidence_type')}
    return {'schema_version': SCHEMA, 'target_year': config['target_year'], 'input_sha256': digest(raw),
            'config_sha256': digest(config), 'raw_records': len(raw), 'candidates': groups, 'duplicate_edges': edges,
            'source_access': access, 'coverage': counts,
            'coverage_gaps': [r for r in config['priority_regions'] if not counts['geographic'].get(r)],
            'screened_out_or_undated': [r['record_id'] for r in records if r['screening'] != 'possible_2026'],
            'warning': 'Proposals only. Retrieved claims are not independent verification or editorial decisions.'}


def write_reports(data, destination):
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'candidates.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    fields = ['candidate_id', 'record_id', 'title', 'doi', 'url', 'publication_date', 'announcement_date',
              'classification_proposal', 'metadata_status', 'screening', 'editorial_review', 'tags', 'uncertainty_flags', 'source_id', 'claims', 'earlier_history']
    with (destination/'candidates.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for g in data['candidates']:
            for r in g['records']:
                row = {k: r.get(k) for k in fields}
                row['candidate_id'] = g['candidate_id']
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    for language in ('en', 'zh'):
        lines = ['# Monitoring candidates / 监测候选提案', '',
                 '> Proposals only; no academic approval. / 仅供编辑审阅，不代表学术核实或批准。', '',
                 f"Input records: {data['raw_records']}; identity groups: {len(data['candidates'])}; duplicate edges: {len(data['duplicate_edges'])}.", '',
                 'Coverage gaps / 覆盖缺口: ' + ', '.join(data['coverage_gaps']), '',
                 'Check source access and provenance before treating this run as coverage. / 请先核查来源访问状态与出处，再评估本次覆盖范围。', '']
        for g in data['candidates']:
            r = g['records'][0]
            lines += [f"## {r.get('title')} ({g['candidate_id']})", '',
                      f"- Provisional editorial review / 暂定编辑审阅: `{r['editorial_review']}`",
                      f"- Classification proposal / 分类提案: {r['classification_proposal']}",
                      f"- Date screening / 日期筛查: {r['screening']}",
                      f"- Publication / 发表: {r.get('publication_date')}; announcement / 公布: {r.get('announcement_date')}; fieldwork / 田野: {r.get('fieldwork_status', 'Unknown / 未核实')}",
                      '- Tags / 标签: ' + json.dumps(r['tags'], ensure_ascii=False),
                      '- Retrieved discovery claims / 检索所得发现陈述: ' + r.get('claims', {}).get(language, ''),
                      '- Reported importance assessment (repository claim) / 原仓库所述意义（待核查）: ' + r.get('importance_context', {}).get(language, 'Pending source review / 待来源核查'),
                      '- Intellectual importance proposal / 学术意义提案: ' + r['importance_proposal'][language],
                      '- Earlier history / 既有历史: ' + json.dumps(r.get('earlier_history', []), ensure_ascii=False),
                      f"- Metadata / 元数据: {r['metadata_status']}; URL: {r['url_status']}",
                      '- Caveats / 保留意见: ' + '; '.join(r['uncertainty_flags']),
                      f"- Duplicate observations / 重复观测: {g['duplicate_count']}; identity conflict / 身份冲突: {g['identity_conflict']}",
                      '- Evidence / 证据:']
            for evidence in g['records']:
                lines += [f"  - {evidence['source_id']}: {evidence.get('url') or 'URL missing'}; DOI {evidence.get('doi')}; provenance {evidence.get('provenance', 'API record in JSON')}"]
            lines += ['']
        lines += ['## Source access / 来源访问', '', '```json', json.dumps(data['source_access'], ensure_ascii=False, indent=2), '```', '']
        (destination/f'candidates.{language}.md').write_text('\n'.join(lines))


def safe_output(path):
    # Keep every write inside monitoring; reject symlinks escaping it.
    path = path.resolve()
    if not path.is_relative_to(ROOT) or path == ROOT:
        raise ValueError('Output/state must be a subpath of monitoring/')
    return path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=['offline', 'live'], default='offline')
    p.add_argument('--input', type=Path, default=ROOT/'fixtures/sample.json')
    p.add_argument('--config', type=Path, default=ROOT/'config.json')
    p.add_argument('--registry', type=Path, default=ROOT/'sources.json')
    p.add_argument('--output', type=Path, default=ROOT/'runs/latest')
    p.add_argument('--state', type=Path, default=ROOT/'runs/state.json')
    p.add_argument('--as-of', default=date.today().isoformat())
    p.add_argument('--verify-dois', action='store_true')
    args = p.parse_args(argv)
    date.fromisoformat(args.as_of)
    destination, state_path = safe_output(args.output), safe_output(args.state)
    config, registry = json.loads(args.config.read_text()), json.loads(args.registry.read_text())
    verification = {}
    if args.as_of < config['start_date']:
        raise ValueError('as-of precedes configured retrieval start')
    if args.mode == 'offline':
        payload = json.loads(args.input.read_text())
        raw, access = payload['records'], payload['source_access']
        verification = payload.get('verification', {})
    else:
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        previous_replay = json.loads((destination/'replay.json').read_text()) if (destination/'replay.json').exists() else {}
        if state and not previous_replay:
            raise ValueError('Incremental state requires the previous output replay evidence; reuse the same output directory or start without state')
        raw, access, state = retrieve(registry, config, state, args.as_of)
        # Preserve previous evidence; deduplicate exact observations, not revised claims.
        raw = list({digest(r): r for r in previous_replay.get('records', []) + raw}.values())
        verification = previous_replay.get('verification', {})
        if args.verify_dois:
            for identifier in sorted({doi(r.get('doi')) for r in raw} - {None}):
                try:
                    verification[identifier] = get_json('https://api.crossref.org/works/' + urllib.parse.quote(identifier, safe=''))['message']
                except (OSError, ValueError, KeyError) as exc:
                    access.append({'source': 'doi_verification', 'doi': identifier, 'status': 'unavailable', 'error': str(exc)[:250]})
        # Raw evidence is persisted before any watermark advancement.
        destination.mkdir(parents=True, exist_ok=True)
        (destination/'replay.json').write_text(json.dumps({'records': raw, 'source_access': access, 'verification': verification}, ensure_ascii=False, indent=2))
    data = report(raw, config, access, verification)
    write_reports(data, destination)
    if args.mode == 'live':
        state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, sort_keys=True, indent=2))
        temporary.replace(state_path)
    print(f"{len(raw)} observations; {len(data['candidates'])} proposed identity groups; {len(data['duplicate_edges'])} duplicate edges")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
