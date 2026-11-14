#!/usr/bin/env python3
"""Validate and render the editorial update registry; never edit academic sources.

Standard library only. Quarto calls render through a fixed-argument Lua filter.
Monitoring may write separate proposals, never the canonical registry or site.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date, datetime, timedelta
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
UPDATE_TIMEZONE = 'Asia/Shanghai'
CATEGORIES = {
    'discovery_added': ('新收录条目', 'Archive entry added'),
    'publication_added': ('新添文献', 'Reference added'),
    'research_update': ('研究更新', 'Research update'),
    'ranking_changed': ('暂定排名调整', 'Provisional ranking change'),
    'site_updated': ('其他网站更新', 'Other website update'),
}
BASELINE_CATEGORIES = {
    'discovery_added': ('既有发现条目', 'Existing archive entry'),
    'publication_added': ('既有文献记录', 'Existing publication reference'),
    'research_update': ('既有研究记录', 'Existing research note'),
}
BASELINE_IDS = frozenset(('baseline-huitzo-entry', 'baseline-widgingarri-entry',
    'baseline-bongal-publication', 'baseline-jars-publication',
    'baseline-font-major-history', 'baseline-stonehenge-research'))
BASELINE_RECORDED_ON = '2026-11-14'
RECORD_FIELDS = {'id', 'state', 'category', 'title', 'description', 'page', 'source_url',
                 'recorded_on', 'website_updated_on', 'website_date_evidence',
                 'discovery_date', 'announcement_date', 'publication_date', 'evidence', 'review'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def today():
    return datetime.now(ZoneInfo(UPDATE_TIMEZONE)).date()


def exact_day(value, as_of):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'Expected exact ISO date')
    parsed = date.fromisoformat(value)
    require(parsed <= as_of, 'Future dates cannot be published')
    return parsed


def bilingual(value):
    require(isinstance(value, dict) and set(value) == {'zh', 'en'}, 'Bilingual zh/en fields required')
    require(all(isinstance(v, str) and v.strip() for v in value.values()), 'Empty bilingual text')
    require(Counter(re.findall(r'\d+(?:\.\d+)?', value['zh'])) ==
            Counter(re.findall(r'\d+(?:\.\d+)?', value['en'])), 'Bilingual numeric mismatch')


def local_page(value, root, suffixes=('.qmd', '.md')):
    require(isinstance(value, str) and not urlsplit(value).scheme and not value.startswith('/') and
            not urlsplit(value).query and not urlsplit(value).fragment and '\\' not in value,
            'Expected local source path without query/fragment')
    path = (root/value).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file() and path.suffix in suffixes, 'Missing/unsafe local link: '+value)
    return path


def https_url(value):
    require(isinstance(value, str) and not any(c.isspace() or ord(c) < 32 for c in value), 'Invalid source URL')
    parsed = urlsplit(value)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password and
            parsed.port in (None, 443), 'Original source must be HTTPS without credentials')
    return value


def canonical_url(value):
    if value is None:
        return None
    parsed = urlsplit(value)
    path = parsed.path.rstrip('/')
    if parsed.hostname == 'doi.org':
        path = path.lower()
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), path, parsed.query, ''))


def baseline_check(record, registry, root):
    """A bootstrap exception is frozen, not an alternate future approval lane."""
    require(record['id'] in BASELINE_IDS, 'Baseline is restricted to six bootstrap IDs')
    require(record['recorded_on'] == BASELINE_RECORDED_ON and registry['registry_created_on'] == BASELINE_RECORDED_ON,
            'Baseline recording day is fixed')
    manifest = json.loads((root/'editorial/updates/baseline-manifest.json').read_text())
    require(manifest.get('schema_version') == 1 and manifest.get('registry_created_on') == BASELINE_RECORDED_ON and
            isinstance(manifest.get('records'), dict) and set(manifest['records']) == BASELINE_IDS,
            'Invalid bootstrap manifest')
    digest = hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    require(manifest['records'][record['id']] == digest, 'Frozen baseline content changed; explicit reviewed workflow required')


def date_value(field, root, as_of):
    require(isinstance(field, dict) and set(field) == {'value', 'precision', 'evidence'}, 'Date structure invalid')
    value, precision, evidence = field['value'], field['precision'], field['evidence']
    if value is None:
        require(precision == 'unknown' and evidence is None, 'Unknown dates must remain explicitly unknown')
        return
    require(precision in ('year', 'month', 'day') and isinstance(value, str), 'Invalid date precision')
    pattern = {'year':r'\d{4}', 'month':r'\d{4}-\d{2}', 'day':r'\d{4}-\d{2}-\d{2}'}[precision]
    require(re.fullmatch(pattern, value), 'Date precision does not match value')
    parsed = date.fromisoformat(value + ('-01-01' if precision == 'year' else '-01' if precision == 'month' else ''))
    require(parsed <= as_of, 'Future source date')
    require(isinstance(evidence, dict) and set(evidence) == {'path', 'quote'}, 'Dated source evidence required')
    content = local_page(evidence['path'], root).read_text()
    quote = evidence['quote']
    require(isinstance(quote, str) and quote.strip() and quote in content, 'Date quotation not found in source')
    candidates = [value]
    if precision == 'year':
        candidates = [value]
    elif precision == 'month':
        candidates += [f'{parsed.year}年{parsed.month}月', parsed.strftime('%B %Y')]
    else:
        candidates += [f'{parsed.year}年{parsed.month}月{parsed.day}日',
                       f'{parsed.day} '+parsed.strftime('%B %Y'),
                       parsed.strftime('%B ')+f'{parsed.day}, {parsed.year}']
    require(any(v in quote for v in candidates), 'Date value unsupported by quotation')


def validate(registry, root=ROOT, as_of=None):
    as_of = as_of or today()
    require(isinstance(registry, dict) and set(registry) == {'schema_version', 'registry_created_on', 'homepage_limit', 'records'}, 'Registry schema invalid')
    require(type(registry['schema_version']) is int and registry['schema_version'] == 1, 'Unsupported registry schema')
    created = exact_day(registry['registry_created_on'], as_of)
    require(type(registry['homepage_limit']) is int and 5 <= registry['homepage_limit'] <= 8, 'Homepage limit must be 5–8')
    require(isinstance(registry['records'], list), 'Record list required')
    ids, identities, titles = set(), set(), set()
    for record in registry['records']:
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS, 'Unknown/missing update fields')
        identity = record['id']
        require(isinstance(identity, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identity) and identity not in ids, 'Invalid/duplicate update ID')
        ids.add(identity)
        require(record['state'] in ('baseline', 'reviewed', 'proposed'), 'Invalid editorial state')
        require(record['category'] in CATEGORIES, 'Invalid update category')
        if record['state'] == 'proposed':
            for field in ('title', 'description'):
                value = record[field]
                require(isinstance(value, dict) and set(value) == {'zh', 'en'} and
                        all(isinstance(v, str) for v in value.values()) and any(v.strip() for v in value.values()),
                        'Proposal needs attributed draft text in at least one language')
        else:
            bilingual(record['title']); bilingual(record['description'])
        title_key = tuple(re.sub(r'\W', '', record['title'][lang]).casefold() for lang in ('zh', 'en'))
        require(title_key not in titles, 'Duplicate update title')
        titles.add(title_key)
        page = local_page(record['page'], root, ('.qmd',))
        if record['source_url'] is not None:
            https_url(record['source_url'])
            if record['state'] != 'proposed':
                require(record['source_url'] in page.read_text(), 'Original source link missing from referenced page')
        require(record['category'] != 'publication_added' or record['source_url'] is not None, 'Publication/report needs original source')
        key = (record['page'], canonical_url(record['source_url']))
        require(key not in identities, 'Duplicate substantive update')
        identities.add(key)
        recorded = exact_day(record['recorded_on'], as_of)
        require(recorded >= created, 'Record precedes registry inception')
        for field in ('discovery_date', 'announcement_date', 'publication_date'):
            date_value(record[field], root, as_of)
        require(isinstance(record['evidence'], list) and (record['evidence'] or record['state'] == 'proposed'), 'Historical/editorial evidence required')
        for proof in record['evidence']:
            require(isinstance(proof, dict) and set(proof) == {'path', 'quote', 'sha256'}, 'Evidence structure invalid')
            content = local_page(proof['path'], root).read_text()
            quote = proof['quote']
            require(isinstance(quote, str) and quote.strip() and quote in content, 'Evidence quotation missing from source')
            require(hashlib.sha256(quote.encode()).hexdigest() == proof['sha256'], 'Evidence changed: independent review required')
        if record['state'] == 'reviewed':
            exact_day(record['website_updated_on'], as_of)
            proof = record['website_date_evidence']
            require(isinstance(proof, dict) and set(proof) in ({'reference', 'description'}, {'reference', 'description', 'published_at'}), 'Verified website-date evidence required')
            if 'published_at' in proof:
                stamp = proof['published_at']
                require(isinstance(stamp, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', stamp), 'Exact UTC deployment timestamp required')
                published = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
                require(published.astimezone(ZoneInfo(UPDATE_TIMEZONE)).date().isoformat() == record['website_updated_on'],
                        'Website date must match deployment timestamp in Beijing time')
            https_url(proof['reference']); bilingual(proof['description'])
            review = record['review']
            require(isinstance(review, dict) and set(review) == {'editor', 'reference'} and
                    isinstance(review['editor'], str) and review['editor'].strip(), 'Named academic/editorial review required')
            https_url(review['reference'])
        else:
            require(record['website_updated_on'] is None and record['website_date_evidence'] is None and record['review'] is None,
                    'Baseline/proposal cannot assert website dates or approval')
            if record['state'] == 'baseline':
                baseline_check(record, registry, root)
    return registry


def load(root=ROOT):
    def unique(pairs):
        data = {}
        for k, v in pairs:
            require(k not in data, 'Duplicate JSON key')
            data[k] = v
        return data
    return validate(json.loads((root/'updates.json').read_text(), object_pairs_hook=unique), root)


def ordered(registry):
    reviewed = sorted((r for r in registry['records'] if r['state'] == 'reviewed'), key=lambda r:(r['website_updated_on'], r['id']), reverse=True)
    # Bootstrap order has no historical chronology or scholarly-rank meaning.
    baseline = [r for r in registry['records'] if r['state'] == 'baseline']
    return reviewed, baseline


def displayed_date(field):
    if field['value'] is None:
        return '未核实 / Unverified'
    precision = {'year':'仅年 / year only', 'month':'仅月 / month only', 'day':'日期 / exact date'}[field['precision']]
    return escape(field['value']) + ' <span class="update-precision">('+precision+')</span>'


def card(record, compact=False):
    r = record
    page = str(Path(r['page']).with_suffix('.html'))
    baseline = r['state'] == 'baseline'
    zh, en = (BASELINE_CATEGORIES if baseline else CATEGORIES)[r['category']]
    when = r['website_updated_on']
    website_date = '未核实 / Unverified' if baseline else escape(when)
    anchor = 'update-' + r['id']
    classes = 'update-card update-card-compact' if compact else 'update-card'
    h = [f'<article id="{anchor}" class="{classes}" data-update-id="{escape(r["id"], quote=True)}" data-update-category="{r["category"]}" data-update-state="{r["state"]}">',
         '<div class="update-meta">']
    if not baseline:
        h.append(f'<span class="update-date"><time datetime="{when}">{when}</time> · 网页更新 / Website update</span>')
    h += [f'<span class="update-category">{zh} / {en}</span></div>',
          f'<h3 class="no-anchor"><a href="{escape(page, quote=True)}"><span lang="zh">{escape(r["title"]["zh"])}</span><span lang="en">{escape(r["title"]["en"])}</span></a></h3>',
          f'<p class="update-summary" lang="zh">{escape(r["description"]["zh"])}</p>',
          f'<p class="update-summary update-summary-en" lang="en">{escape(r["description"]["en"])}</p>']
    if not compact:
        h += ['<dl class="update-dates">',
              f'<div><dt>网页更新 / Website update</dt><dd>{website_date}</dd></div>',
              f'<div><dt>发现／调查 / Discovery/investigation</dt><dd>{displayed_date(r["discovery_date"])}</dd></div>',
              f'<div><dt>公开公布 / Announcement</dt><dd>{displayed_date(r["announcement_date"])}</dd></div>',
              f'<div><dt>发表／报道 / Publication/report</dt><dd>{displayed_date(r["publication_date"])}</dd></div>',
              '</dl>']
        if baseline:
            h.append(f'<p class="update-recorded-date">登记于本日志 / Entered in this registry: <time datetime="{r["recorded_on"]}">{r["recorded_on"]}</time> · 非原网页更新日 / Not the original website-update date.</p>')
    elif baseline:
        h.append(f'<p class="update-recorded-note">历史记录；原网页日期未核实。<br>Retrospective record; original website date unverified. <a href="update-history.html#{anchor}">完整日期 / Full dates</a></p>')
    else:
        h.append(f'<p class="update-recorded-note"><a href="update-history.html#{anchor}">完整日期与记录 / Full dates and record</a></p>')
    h += ['<div class="update-links">', f'<a href="{escape(page, quote=True)}">相关页面 / Details</a>']
    if r['source_url']:
        h.append(f'<a href="{escape(r["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer">原始来源 / Original source <span aria-hidden="true">↗</span></a>')
    h += ['</div></article>']
    return '\n'.join(h)


def recent(registry, as_of=None):
    """Seven Beijing calendar dates, inclusive; never use recording/source dates."""
    end = as_of or today()
    start = end - timedelta(days=6)
    return [r for r in ordered(registry)[0]
            if start <= date.fromisoformat(r['website_updated_on']) <= end]


def render(registry, view, as_of=None):
    reviewed, baseline = ordered(registry)
    h = ['<div class="updates-panel">']
    if view == 'latest':
        end = as_of or today()
        start = end - timedelta(days=6)
        h.append(f'<p class="updates-window">统计区间 / Window: {start.isoformat()} – {end.isoformat()} · 北京时间 / Beijing time (Asia/Shanghai)</p>')
        rows = recent(registry, end)
        for category, (zh, en) in CATEGORIES.items():
            group = [r for r in rows if r['category'] == category]
            h.append(f'<h3 class="updates-group-title">{zh} / {en}</h3>')
            h += ['<div class="latest-updates-grid">', *[card(r, True) for r in group], '</div>']
            hidden = ' hidden' if group else ''
            h.append(f'<p class="updates-empty"{hidden}>本周暂无已核实登记 / No verified records logged this week.</p>')
    else:
        if reviewed:
            h += ['<p class="updates-group-title">网站更新 / Website updates</p>',
                  '<div class="latest-updates-grid">', *[card(r) for r in reviewed], '</div>']
        if baseline:
            h += ['<p class="updates-baseline-label">历史记录整理 / Retrospective archive baseline</p>',
                  '<div class="latest-updates-grid">', *[card(r) for r in baseline], '</div>']
    h.append('</div>')
    return '\n'.join(h)


def propose(record, destination, root=ROOT):
    """A proposal is never a publishing/approval signal. Output restricted to scratch."""
    destination = destination.resolve()
    root = root.resolve()
    allowed = [root/p for p in ('monitoring/runs', 'work')]
    require(any(path.resolve() == path and destination.is_relative_to(path) for path in allowed),
            'Proposal output must stay in monitoring/runs/ or work/; never updates.json')
    proposal = json.loads(json.dumps(record))
    for field in ('title', 'description'):
        value = proposal.get(field, {})
        proposal[field] = {lang:value.get(lang, '') for lang in ('zh', 'en')}
    proposal.update(state='proposed', website_updated_on=None, website_date_evidence=None, review=None)
    reported_dates = {field: proposal[field] for field in ('discovery_date', 'announcement_date', 'publication_date')}
    for field in reported_dates:
        proposal[field] = {'value':None, 'precision':'unknown', 'evidence':None}
    check = {'schema_version':1, 'registry_created_on':proposal['recorded_on'], 'homepage_limit':6, 'records':[proposal]}
    validate(check, root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({'proposal_schema':1, 'warning':'Proposed only; requires source, bilingual, privacy and human editorial review. No promotion authority.', 'review_flags':['bilingual_review_pending', 'source_and_date_verification_pending', 'privacy_review_pending'],
                                       'reported_dates_unverified':reported_dates, 'record':proposal}, ensure_ascii=False, indent=2)+'\n')


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


def check_rendered(root, directory, registry):
    reviewed, baseline = ordered(registry)
    expected = {r['id'] for r in reviewed+baseline}
    for filename, ids in [('index.html', {r['id'] for r in recent(registry)}),
                          ('update-history.html', expected)]:
        path = directory/filename
        text = path.read_text()
        observed = re.findall(r'data-update-id="([^"]+)"', text)
        require(set(observed) == ids and len(observed) == len(ids), 'Rendered update count/identity drift: '+filename)
        parser = Links(); parser.feed(text)
        for href in parser.links:
            parsed = urlsplit(href)
            if not parsed.scheme and parsed.path:
                target = (path.parent/parsed.path).resolve()
                require(target.is_relative_to(directory.resolve()) and target.exists(), 'Broken rendered link: '+href)
    home = (directory/'index.html').read_text()
    require('past-week-updates' in home and 'Current coverage' not in home, 'Weekly updates must replace Current coverage')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'render', 'propose'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--view', choices=('latest', 'history'), default='latest')
    parser.add_argument('--rendered', type=Path)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'propose':
        require(args.input is not None and args.output is not None, 'Proposal input and output required')
        propose(json.loads(args.input.read_text()), args.output, args.root)
    else:
        registry = load(args.root)
        if args.command == 'render':
            print(render(registry, args.view))
        else:
            if args.rendered:
                check_rendered(args.root, args.rendered.resolve(), registry)
            print(f'Update registry valid: {len(registry["records"])} records; proposals are never rendered.')


if __name__ == '__main__':
    main()
