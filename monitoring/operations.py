#!/usr/bin/env python3
"""Phase 2B operations. Public outputs contain controlled labels and hashes only.

Remote text is untrusted data, never instructions, shell input, or publishable prose.
Raw responses live only in process memory; no private archaeology is uploaded.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
import tempfile
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect requires separate source approval')


API_OPEN = urllib.request.build_opener(NoRedirect()).open
import monitor as m
import state_schema as schema
from eligibility import https_provenance_url

REPO = m.ROOT.parent
STATE_SCHEMA = schema.SCHEMA


def atomic_json(path, value):
    path = m.safe_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix='.state-', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(value, stream, sort_keys=True, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)



def diagnostic(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return {403: 'http_403_access_or_terms', 404: 'metadata_not_found',
                429: 'rate_limited'}.get(exc.code, 'http_server_error' if exc.code >= 500 else 'http_client_error')
    if '403' in str(exc):
        return 'proxy_403'
    return 'network_or_invalid_response'


def crossref_contact():
    config = json.loads((m.ROOT/'contact.json').read_text())
    if set(config) != {'schema', 'institutional_contact_email', 'institutional_contact_url', 'approval_reference'} or config['schema'] != 1:
        raise ValueError('Invalid institutional contact configuration')
    email = config['institutional_contact_email']
    if email is not None and (not isinstance(email, str) or not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', email) or not config['approval_reference']):
        raise ValueError('Institutional email requires reviewed configuration')
    if config['institutional_contact_url'] != 'https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries':
        raise ValueError('Unreviewed institutional contact URL')
    return config


def transport(address, attempts=3, sleep=time.sleep, opener=API_OPEN):
    parsed = urllib.parse.urlsplit(address)
    if parsed.scheme != 'https' or parsed.hostname not in {'api.crossref.org', 'api.openalex.org'}:
        raise ValueError('Unregistered metadata host')
    contact = crossref_contact()
    agent = 'UBC-Archaeology-Discovery-Monitor/2B (' + contact['institutional_contact_url'] + ')'
    if parsed.hostname == 'api.crossref.org' and contact['institutional_contact_email']:
        address += ('&' if parsed.query else '?') + urllib.parse.urlencode({'mailto': contact['institutional_contact_email']})
        agent += ' mailto:' + contact['institutional_contact_email']
    request = urllib.request.Request(address, headers={
        'User-Agent': agent,
        'Accept': 'application/json'})
    # Do not automatically follow redirects to arbitrary hosts or persist secrets/errors.
    for attempt in range(attempts):
        try:
            with opener(request, timeout=25) as response:
                body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise ValueError('Response exceeds bound')
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
            delay = min(30, 2 ** attempt)
            retry = exc.headers.get('Retry-After', '') if exc.headers else ''
            if retry.isdigit():
                delay = min(30, max(delay, int(retry)))
            sleep(delay)
        except (OSError, ValueError) as exc:
            if diagnostic(exc) == 'proxy_403' or attempt == attempts - 1:
                raise
            sleep(2 ** attempt)


def empty_state():
    return {'schema': STATE_SCHEMA, 'observation_projection': schema.OBSERVATION_PROJECTION, 'taxonomy_sha256': schema.taxonomy_hash(json.loads((m.ROOT/'config.json').read_text())),
            'sources': {}, 'observations': {}, 'runs': {}}


def state_inputs():
    return (json.loads((m.ROOT/'sources.json').read_text()),
            json.loads((m.ROOT/'config.json').read_text()))


def validate_state(state):
    return schema.validate(state, *state_inputs())


def load_state(path):
    if not path.exists():
        return empty_state()
    if path.stat().st_size > schema.MAX_BYTES:
        raise ValueError('State exceeds size bound')
    return schema.decode(path.read_bytes(), *state_inputs())


def collect(registry, config, state, as_of, full=False, fetch=transport):
    """Resume capped windows; complete watermarks only. Monday starts backfill after
    any unfinished window completes, so a weekly reset cannot starve pagination.
    """
    observations, access = [], []
    for source in registry['sources']:
        if not source.get('enabled') or source['adapter'] != 'crossref':
            continue
        sid = source['id']
        prior = state['sources'].get(sid, {})
        pending = prior.get('pending')
        start = config['start_date'] if full or not prior.get('watermark') else max(config['start_date'],
            (m.date.fromisoformat(prior['watermark']) - m.timedelta(days=config['overlap_days'])).isoformat())
        window = pending or {'since': start, 'until': as_of, 'cursor': '*'}
        # Failed sources cannot advance; successful pages can resume after the last durable page.
        next_state = dict(prior)
        pages, complete = 0, False
        category = None
        try:
            while pages < config['max_pages_per_source']:
                params = {'rows': config['page_size'], 'cursor': window['cursor'],
                          'filter': f"from-index-date:{window['since']},until-index-date:{window['until']}"}
                endpoint = 'https://api.crossref.org/works'
                if source.get('issn'):
                    endpoint = f"https://api.crossref.org/journals/{source['issn']}/works"
                else:
                    params['query'] = config['query']
                payload = fetch(endpoint + '?' + urllib.parse.urlencode(params))['message']
                items = payload['items']
                if not isinstance(items, list):
                    raise ValueError('Invalid API page')
                observations.extend(m.crossref(item, sid, as_of) for item in items)
                pages += 1
                cursor = payload.get('next-cursor')
                if not items or len(items) < config['page_size']:
                    complete = True
                    break
                if not cursor or cursor == window['cursor']:
                    category = 'cursor_missing_or_repeated'
                    break
                window = {**window, 'cursor': cursor}
            if complete:
                next_state = {'watermark': max(prior.get('watermark', config['start_date']), window['until'])}
            else:
                next_state['pending'] = window
        except (OSError, ValueError, KeyError, TypeError) as exc:
            category = diagnostic(exc)
            next_state['pending'] = window
        state['sources'][sid] = next_state
        access.append({'source': sid, 'status': 'complete' if complete else 'incomplete',
                       'diagnostic': category, 'pages': pages, 'watermark_advanced': complete,
                       'since': window['since'], 'until': window['until']})
    return observations, access


def safe_tags(record, config):
    proposed, _ = m.tags(record, config)
    # Only local dictionary labels; never source-provided tags in public artifacts.
    return {dim: sorted(set(values) & set(config['tag_rules'][dim])) for dim, values in proposed.items()}


def scholarly_projection(record):
    """Versioned scholarly fields only. Provider indexing/citation/score counters,
    deposit timestamps, affiliation-only edits and fetch/source bookkeeping are not scholarly revisions.
    Retraction/correction relations, authors, claims and dates ARE revisions.
    """
    provider = record.get('provider_record') or {}
    return {
        'projection_version': schema.OBSERVATION_PROJECTION,
        'doi': m.doi(record.get('doi')), 'url': m.url(record.get('url')),
        'title': ' '.join((record.get('title') or '').split()),
        'authors': [{k: author[k] for k in ('given', 'family', 'name', 'ORCID', 'sequence') if k in author}
                    for author in record.get('authors', [])],
        'container': record.get('container', []), 'claims': record.get('claims', {}),
        'publication_dates': {k: v for k, v in record.get('source_dates', {}).items()
                              if k in ('published', 'published-online', 'published-print')},
        'publication_date': record.get('publication_date'), 'announcement_date': record.get('announcement_date'),
        'earlier_history': record.get('earlier_history', []),
        'type': provider.get('type'), 'relations': provider.get('relation', {}),
        'updates': provider.get('update-to', []),
    }


def update_ledger(state, records, config, as_of):
    for record in records:
        identity = m.digest(scholarly_projection(record))
        previous = state['observations'].get(identity)
        sources = set(previous['source_ids']) if previous else set()
        sources.add(record['source_id'])
        state['observations'][identity] = {
            'first_seen': previous['first_seen'] if previous else as_of,
            'last_seen': as_of, 'source_ids': sorted(sources),
            'tags': safe_tags(record, config), 'classification': 'Unresolved',
            'identity_keys': [m.digest([kind, value]) for kind, value in (
                ('doi', m.doi(record.get('doi'))), ('url', m.url(record.get('url'))),
                ('title', m.norm(record.get('title', '')))) if value]}


def identity_groups(observations):
    # Transitive hashed DOI/URL/title grouping; no raw identifiers leave the runner.
    parents = {key: key for key in observations}
    def root(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key
    seen = {}
    for key, row in observations.items():
        for identity in row['identity_keys']:
            if identity in seen:
                parents[root(key)] = root(seen[identity])
            else:
                seen[identity] = key
    groups = {}
    for key, row in observations.items():
        groups.setdefault(root(key), []).append(row)
    return [{'tags': {dim: sorted({tag for row in rows for tag in row['tags'][dim]})
                      for dim in ('geographic', 'chronological', 'discovery_type', 'evidence_type')}}
            for rows in groups.values()]


def counts(rows):
    return {dim: dict(sorted(Counter(label for row in rows for label in (row['tags'][dim] or ['unknown'])).items()))
            for dim in ('geographic', 'chronological', 'discovery_type', 'evidence_type')}


def archive_classification(project):
    """Preserve established Reanalysis; a proposal cannot authorize its reversal."""
    classification = project.get('research_type')
    proposed = classification if classification in schema.CATEGORIES else None
    existing_reanalysis = project.get('reanalysis') is True
    if existing_reanalysis and proposed not in (None, 'Reanalysis'):
        return {'category': 'Reanalysis', 'classification_conflict': True,
                'proposed_category': proposed, 'review_required': True}
    provenance = project.get('research_type_provenance')
    if (proposed is not None and isinstance(provenance, dict) and
        set(provenance) == {'editor', 'approval_reference', 'source_references'} and
        isinstance(provenance['editor'], str) and provenance['editor'].strip() and
        https_provenance_url(provenance['approval_reference']) and
        isinstance(provenance['source_references'], list) and provenance['source_references'] and
        all(https_provenance_url(u) for u in provenance['source_references'])):
        return {'category': proposed, 'classification_conflict': False,
                'proposed_category': proposed, 'review_required': False}
    return {'category': 'Reanalysis' if existing_reanalysis else 'Unresolved',
            'classification_conflict': False, 'proposed_category': proposed,
            'review_required': proposed is not None}


def archive_category(project):
    return archive_classification(project)['category']


def archive_audit(config):
    """Read actual formal table, join inventory by stable ID; retain source columns.
    Heuristic tags are screening only. No inference that non-Reanalysis means field.
    """
    inventory = json.loads((REPO/'editorial/inventory.json').read_text())['projects']
    by_id = {str(row['key']): row for row in inventory}
    rows = []
    for line in (REPO/'discoveries.qmd').read_text().splitlines():
        if not re.match(r'^\| \d+ \|', line):
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        identity = cells[0]
        project = by_id[identity]
        page = REPO/project['page']
        text = page.read_text()
        record = {'title': cells[1], 'claims': {'en': text},
                  'geographic_context': cells[2], 'chronological_context': cells[3]}
        classification = archive_classification(project)
        rows.append({'id': identity, 'region_column': cells[2], 'period_column': cells[3],
                     'source_sha256': m.digest(text), 'tags': {
                         **safe_tags(record, config),
                         'geographic': safe_tags({'title': cells[2]}, config)['geographic'],
                         'chronological': safe_tags({'title': cells[3]}, config)['chronological']},
                     'field_reanalysis': classification['category'],
                     'classification_conflict': classification['classification_conflict'],
                     'proposed_field_reanalysis': classification['proposed_category'],
                     'classification_review_required': classification['review_required']})
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Missing/duplicate formal membership')
    return {'formal_entries': len(rows), 'ranking_positions': len(inventory),
            'source': 'discoveries.qmd + discovery pages + editorial/inventory.json',
            'table_sha256': m.digest((REPO/'discoveries.qmd').read_text()),
            'region_columns': dict(Counter(r['region_column'] for r in rows)),
            'period_columns': dict(Counter(r['period_column'] for r in rows)),
            'coverage': counts(rows), 'field_reanalysis': {category: sum(r['field_reanalysis'] == category for r in rows) for category in schema.CATEGORIES},
            'classification_conflicts': [r['id'] for r in rows if r['classification_conflict']],
            'rows': rows, 'interpretation': 'Heuristic multi-label screening; unknowns explicit. No quotas, grades or ranking decisions.'}


def run(mode, state_path, output, as_of, full=False, fetch=transport):
    config = json.loads((m.ROOT/'config.json').read_text())
    registry = json.loads((m.ROOT/'sources.json').read_text())
    state = load_state(state_path)
    access = []
    if mode == 'monitor':
        records, access = collect(registry, config, state, as_of, full, fetch)
        update_ledger(state, records, config, as_of)
        state['last_monitor_access'] = access
        state['last_monitor_date'] = as_of
    else:
        access = state.get('last_monitor_access', [])
    audit = archive_audit(config)
    report = {'schema': 1, 'mode': mode, 'as_of': as_of, 'timezone': 'America/Vancouver',
              'label': 'Provisional / Under evaluation / 暂定／待评估',
              'observation_count': len(state['observations']), 'source_access': access,
              'last_monitor_date': state.get('last_monitor_date'),
              'identity_groups': len(identity_groups(state['observations'])),
              'candidate_coverage': counts(identity_groups(state['observations'])), 'formal_archive': audit,
              'outages': [a['source'] for a in access if a['diagnostic']],
              'incomplete_sources': [a['source'] for a in access if a['status'] != 'complete'],
              'formal_publication': 'disabled',
              'queue': [{'observation_sha256': key, **row} for key, row in sorted(state['observations'].items())],
              'review_instructions': 'Human verification required; hashes are observations, not unique discoveries. Retrieve primary evidence in a controlled review environment; metadata alone cannot be promoted.',
              'coverage_gaps': [r for r in config['priority_regions'] if not counts(state['observations'].values())['geographic'].get(r)]}
    # One durable transaction includes source cursors AND observation ledger AND report.
    run_key = f'{as_of}:{mode}'
    state['runs'][run_key] = {'report_sha256': m.digest(report), 'outages': report['outages']}
    validate_state(state)
    atomic_json(state_path, state)
    atomic_json(output/'report.json', report)
    output.mkdir(parents=True, exist_ok=True)
    (output/'summary.md').write_text('\n'.join([
        '# Provisional / Under evaluation — 暂定／待评估', '',
        f"Mode: {mode}; Vancouver date: {as_of}",
        f"Observations (not discoveries): {len(state['observations'])}",
        f"Formal archive: {audit['formal_entries']}; ranking positions: {audit['ranking_positions']}",
        f"Outages: {len(report['outages'])}; incomplete sources: {len(report['incomplete_sources'])}",
        'Formal publication: DISABLED / 正式发布：关闭', '',
        'Human review: verify primary evidence, dates/history, duplicates, significance, bilingual text and community permissions.',
        '人工审阅：核实一手证据、日期和既有历史、重复项目、学术意义、双语表述及社群许可。',
        'Public queue contains hashes and controlled screening labels only. Source text is withheld pending privacy review.',
        '公开队列仅含哈希及受控筛查标签；来源原文须先经隐私审查。', '']))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['monitor', 'review', 'audit'], required=True)
    parser.add_argument('--state', type=Path, default=m.ROOT/'runs/durable/state.json')
    parser.add_argument('--output', type=Path, default=m.ROOT/'runs/phase2b')
    parser.add_argument('--as-of', default=None)
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    from zoneinfo import ZoneInfo
    as_of = args.as_of or datetime.now(ZoneInfo('America/Vancouver')).date().isoformat()
    m.date.fromisoformat(as_of)
    report = run(args.mode, m.safe_output(args.state), m.safe_output(args.output), as_of, args.full)
    print(json.dumps({k: report[k] for k in ('mode', 'observation_count', 'outages', 'incomplete_sources', 'formal_publication')}))


if __name__ == '__main__':
    main()
