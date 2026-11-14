#!/usr/bin/env python3
"""Read-only corpus consistency checks. No network requests or academic decisions."""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class HTMLFacts(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.markers, self.options = [], [], [], []
        self.anchor = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.anchor = a.get('href')
        if tag in ('a', 'iframe', 'img', 'script', 'link'):
            value = a.get('href' if tag in ('a', 'link') else 'src')
            if value:
                self.links.append(value)
        if tag == 'circle' and 'marker' in a.get('class', '').split():
            self.markers.append((self.anchor, a.get('class', '').split()))
        if tag == 'option' and a.get('value'):
            self.options.append(a['value'])

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor = None


def sections(text, level):
    return [(m[1], m[2], m[3]) for m in re.finditer(
        rf'^{"#" * level} (\d+)\. ([^\n]+)\n(.*?)(?=^{"#" * level} |\Z)',
        text, re.M | re.S)]


_SCALE = {
    '百万': 1000000, '万': 10000, '千': 1000,
    'ma': 1000000, 'ka': 1000,
    'million': 1000000, 'millions': 1000000,
    'thousand': 1000, 'thousands': 1000,
}
_SCALE_RE = r'(?:百万|万|千|Ma(?![A-Za-z])|ka(?![A-Za-z])|millions?\b|thousands?\b)'
_NUMBER_RE = r'\d[\d,]*(?:\.\d+)?'
_RANGE_UNIT_RE = re.compile(
    rf'(?<![\d.])(?P<first>{_NUMBER_RE})(?P<sep>\s*(?:–|—|-|\bto\b)\s*)'
    rf'(?P<second>{_NUMBER_RE})(?P<space>\s*)(?P<scale>{_SCALE_RE})',
    re.I,
)
_BETWEEN_UNIT_RE = re.compile(
    rf'\bbetween\s+(?:roughly\s+|about\s+|approximately\s+)?'
    rf'(?P<first>{_NUMBER_RE})\s+and\s+'
    rf'(?P<second>{_NUMBER_RE})\s+(?P<scale>{_SCALE_RE})',
    re.I,
)
_TOKEN_RE = re.compile(
    rf'(?<![\d.])(?P<number>{_NUMBER_RE})\s*(?P<scale>{_SCALE_RE})?',
    re.I,
)
_WORD_NUMBER_RE = re.compile(
    r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|'
    r'eleven|twelve|twenty|thirty|forty|fifty|hundred|'
    r'first|second|third)\b', re.I,
)


def numbers(text):
    """Normalize explicit Arabic quantities, including English scale words.

    A range suffix such as '14.2–15.8 ka' applies to BOTH endpoints.
    This deliberately does not infer hidden context (e.g. a date in an earlier
    paragraph) or transform English number words into numbers.
    """
    text = _BETWEEN_UNIT_RE.sub(
        lambda m: f"between {m['first']} {m['scale']} and {m['second']} {m['scale']}",
        text,
    )
    text = _RANGE_UNIT_RE.sub(
        lambda m: (
            f"{m['first']} {m['scale']}{m['sep']}"
            f"{m['second']}{m['space']}{m['scale']}"
        ),
        text,
    )
    values = []
    for m in _TOKEN_RE.finditer(text):
        scale = _SCALE.get((m['scale'] or '').lower(), 1)
        values.append(Decimal(m['number'].replace(',', '')) * scale)
    return sorted(values)


def numeric_review_hint(chinese, english):
    """Advisory category only; none of these labels establishes a factual error."""
    if _WORD_NUMBER_RE.search(english):
        return 'spelled-number-or-scope'
    if re.search(rf'{_SCALE_RE}', chinese + ' ' + english, re.I):
        return 'unit-or-range-context'
    if len(numbers(chinese)) != len(numbers(english)):
        return 'unequal-detail-or-context'
    return 'possible-quantity-discrepancy'



def run(root, rendered=None):
    findings = []

    def report(code, path, message, severity='error', category=None):
        finding = dict(severity=severity, code=code, path=str(path), message=message)
        if category is not None:
            finding['review_category'] = category
        findings.append(finding)

    def require(ok, code, path, message):
        if not ok:
            report(code, path, message)

    names = ['methods.qmd', 'ranking.qmd', 'under-review.qmd', 'discoveries.qmd', 'index.qmd']
    names += sorted(str(p.relative_to(root)) for p in (root / 'discoveries').glob('*.qmd'))
    texts = {}
    for name in names:
        try:
            texts[name] = (root / name).read_text(encoding='utf-8')
        except OSError as e:
            report('missing-source', name, str(e))
            texts[name] = ''
    try:
        records = json.loads((root / 'editorial/inventory.json').read_text())['projects']
        map_text = (root / 'map.html').read_text()
    except (OSError, ValueError, KeyError) as e:
        report('input', 'editorial/inventory.json or map.html', str(e))
        return findings
    require(bool(records), 'inventory', 'editorial/inventory.json', 'Empty inventory')
    require(len({r['key'] for r in records}) == len(records), 'identity', 'editorial/inventory.json', 'Duplicate project keys')
    expected_pages = [r['page'] for r in records if 'page' in r]
    require(len(set(expected_pages)) == len(expected_pages), 'identity', 'editorial/inventory.json', 'Duplicate page identities')
    require(set(expected_pages) == set(names[5:]), 'page-inventory', 'discoveries/', 'Discovery page set differs from inventory')

    ranks = sections(texts['ranking.qmd'], 3)
    reviews = sections(texts['under-review.qmd'], 2)
    require([int(n) for n, _, _ in reviews] == list(range(1, sum('review_heading' in r for r in records) + 1)), 'review-sequence', 'under-review.qmd', 'Review section numbers must be unique and consecutive (not stable project IDs)')
    require([int(n) for n, _, _ in ranks] == list(range(1, len(records) + 1)), 'rank-sequence', 'ranking.qmd', 'Ranks must be unique and consecutive')
    require(len({h for _, h, _ in ranks}) == len(ranks), 'rank-identity', 'ranking.qmd', 'Duplicate ranked headings')
    require({h for _, h, _ in ranks} == {r['ranking_heading'] for r in records}, 'rank-inventory', 'ranking.qmd', 'Ranked project set differs from inventory')
    require({h for _, h, _ in reviews} == {r['review_heading'] for r in records if 'review_heading' in r}, 'review-inventory', 'under-review.qmd', 'Review project set differs; updates such as Stonehenge are not candidates')
    rank_by_title = {h: (int(n), body) for n, h, body in ranks}
    review_by_title = {h: body for _, h, body in reviews}
    formal = {r['page']: r for r in records if 'page' in r and r['status'] != 'Under review'}
    table = re.findall(r'^\|\s*(\d+)\s*\|.*?\]\((discoveries/[^)]+)\).*?\|\s*(CCTV candidate / 央视候选|Additional candidate / 补充建议)\s*\|$', texts['discoveries.qmd'], re.M)
    require(Counter(p for _, p, _ in table) == Counter(formal.keys()), 'formal-membership', 'discoveries.qmd', 'Formal table must contain each formal project once and exclude under-review projects')
    for pid, page, status in table:
        require(int(pid) == int(Path(page).name.split('-')[0]), 'stable-id', 'discoveries.qmd', f'ID {pid} disagrees with {page}')
        if page in formal:
            require(status.startswith(formal[page]['status']), 'table-status', 'discoveries.qmd', f'{page}: status differs from inventory')

    for r in records:
        loc = r.get('page', 'under-review.qmd')
        if 'review_heading' in r:
            review_body = review_by_title.get(r['review_heading'], '')
            decisions = sorted(set(re.findall(r'decision: (PROMOTE|HOLD|REJECT)', review_body)))
            require(decisions == r['review_decisions'], 'review-decision', 'under-review.qmd', f"{r['key']}: explicit decision differs from observed baseline; human approval required")
            chinese_decisions = sorted(set(re.findall(r'结论：(PROMOTE|HOLD|REJECT)', review_body)))
            require(chinese_decisions == decisions, 'review-decision-language', 'under-review.qmd', f"{r['key']}: Chinese/English explicit decisions disagree")
        n, body = rank_by_title.get(r['ranking_heading'], (None, ''))
        require(n == r['rank'], 'rank-baseline', 'ranking.qmd', f"{r['key']}: rank differs from observed baseline; human review required")
        status = re.search(r'Status:\*\* (CCTV|Additional|Under review)(?:\s|·|$)', body)
        require(status is not None and status[1] == r['status'], 'rank-status', 'ranking.qmd', f"{r['key']}: missing/inconsistent status")
        grade = re.search(r'Evidence:\*\* ([A-D])(?:\s|$)', body)
        require((grade[1] if grade else None) == r['grade'], 'rank-grade', 'ranking.qmd', f"{r['key']}: missing/inconsistent evidence grade")
        require(('Reanalysis' in body.split('\n')[0]) == r['reanalysis'], 'rank-reanalysis', 'ranking.qmd', f"{r['key']}: Reanalysis flag differs")
        if 'page' not in r:
            continue
        text = texts.get(loc, '')
        eng = re.findall(r'^([A-D])\s*—', text, re.M)
        zh = re.findall(r'^([A-D])级', text, re.M)
        require(eng == [r['grade']] and zh == [r['grade']], 'page-grade', loc, 'English/Chinese evidence grades must agree with ranking and inventory')
        status_block = re.search(r'\*\*CCTV status / 央视遴选状态\*\*\s*\n([^\n]+)', text)
        labels = {'CCTV': ('CCTV candidate', '央视候选'), 'Additional': ('Additional candidate', '补充建议'), 'Under review': ('Under review', '待评估')}
        require(status_block is not None and all(s in status_block[1] for s in labels[r['status']]), 'page-status', loc, 'Bilingual status missing or inconsistent')
        require(bool(re.search(rf'^title: ["\']?{int(r["key"])}\.', text, re.M)), 'page-id', loc, 'Title project ID differs from stable filename ID')
        if r['reanalysis'] and not ('Reanalysis' in text and '旧材料再分析' in text):
            report('reanalysis-label', loc, 'Ranking labels this Reanalysis; explicit bilingual label missing on discovery page. Human review required.', 'warning')

    counts = Counter(r['status'] for r in records)
    # Explicit summary claims in both languages, rather than arbitrary numerals.
    claims = {
        'index.qmd': [(r'全部(\d+)项发现', len(formal)), (r'all (\d+) discoveries', len(formal)),
                      (r'\*\*(\d+)项\*\*中央', counts['CCTV']), (r'\*\*(\d+)\*\* discoveries from', counts['CCTV']),
                      (r'\*\*(\d+)项\*\*补充', counts['Additional']), (r'\*\*(\d+)\*\* additional candidates', counts['Additional'])],
        'ranking.qmd': [(r'\*\*(\d+)个候选项目', len(records)), (r'\*\*(\d+) current candidate projects', len(records)),
                        (r'(\d+)项央视候选', counts['CCTV']), (r'(\d+) CCTV candidates', counts['CCTV']),
                        (r'(\d+)项补充建议', counts['Additional']), (r'(\d+) additional candidates', counts['Additional']),
                        (r'(\d+)项仍在', counts['Under review']), (r'(\d+) projects still under review', counts['Under review'])]}
    for path, patterns in claims.items():
        for pattern, expected in patterns:
            values = re.findall(pattern, texts[path])
            require(bool(values) and all(int(v) == expected for v in values), 'summary-count', path, f'{pattern}: expected {expected}, found {values}')
    methods = texts['methods.qmd']
    route_block = methods.split('## “2026年发现”的口径', 1)[-1].split(':::')[0]
    require(Counter(re.findall(r'^([123])\. ', route_block, re.M)) == Counter({'1': 2, '2': 2, '3': 2}), 'eligibility-schema', 'methods.qmd', 'Expected three eligibility routes in each language')
    for grade in 'ABCD':
        require(f'{grade}级 / Grade {grade}' in methods, 'grade-schema', 'methods.qmd', f'Missing bilingual definition for {grade}')

    facts = HTMLFacts(map_text)
    expected_map = {p.replace('.qmd', '.html'): r for p, r in formal.items()}
    require(Counter(h for h, _ in facts.markers) == Counter(expected_map.keys()), 'map-membership', 'map.html', 'SVG markers must match formal project links exactly once')
    require(Counter(facts.options) == Counter(expected_map.keys()), 'map-options', 'map.html', 'Mobile selector must match formal projects exactly once')
    for href, classes in facts.markers:
        if href in expected_map:
            require(('cctv' in classes, 'extra' in classes) == (expected_map[href]['status'] == 'CCTV', expected_map[href]['status'] == 'Additional'), 'map-status', 'map.html', f'{href}: marker color/status mismatch')

    # Screen adjacent explicitly labelled bilingual paragraphs; prose equivalence
    # cannot be inferred reliably from numeric tokens. Warnings never edit text.
    for path, text in texts.items():
        for match in re.finditer(r'\*\*中文[^*]*\*\*((?:(?!\n\s*\n).)*)\n\s*\*\*English\.\*\*(.*?)(?=\n\s*\n|\Z)', text, re.S):
            left, right = numbers(match[1]), numbers(match[2])
            if left != right:
                line = text[:match.start()].count('\n') + 1
                category = numeric_review_hint(match[1], match[2])
                report('bilingual-numbers', f'{path}:{line}',
                       f'Explicit quantities differ after scale normalization: Chinese {left}; English {right}. Heuristic: {category}; inspect context manually.',
                       'warning', category=category)

    def check_link(path, href, base, html_mode=False):
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or (not parsed.path and not (html_mode and parsed.fragment)):
            return
        clean = unquote(parsed.path)
        target = (path if not clean else base / clean.lstrip('/') if clean.startswith('/') else path.parent / clean).resolve()
        if not target.is_relative_to(base.resolve()):
            report('internal-link', path.relative_to(base), f'Link escapes site: {href}')
            return
        if clean.endswith('/'):
            target /= 'index.html'
        if not html_mode and target.suffix == '.html' and target.name != 'map.html':
            source = target.with_suffix('.qmd')
            if source.is_file():
                target = source
        require(target.is_file(), 'internal-link', path.relative_to(base), f'Missing target: {href}')
        if html_mode and target.is_file() and target.suffix == '.html' and parsed.fragment:
            ids = HTMLFacts(target.read_text(encoding='utf-8')).ids
            require(unquote(parsed.fragment) in ids, 'internal-fragment', path.relative_to(base), f'Missing fragment: {href}')

    for name, text in texts.items():
        links = re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', text)
        links += HTMLFacts(text).links
        for href in links:
            check_link(root / name, href, root)
    for href in facts.links + facts.options:
        check_link(root / 'map.html', href, root)
    if rendered is not None:
        expected = [Path(n).with_suffix('.html') for n in names] + [Path('map.html')]
        for name in expected:
            require((rendered / name).is_file(), 'rendered-missing', name, 'Expected rendered page missing; render first')
        for path in rendered.rglob('*.html'):
            html = HTMLFacts(path.read_text(encoding='utf-8'))
            for href in html.links:
                check_link(path, href, rendered, True)
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--rendered', type=Path, help='Existing rendered site directory, relative to root')
    parser.add_argument('--json', type=Path, help='Write report outside source tree when possible')
    args = parser.parse_args()
    root = args.root.resolve()
    findings = run(root, root / args.rendered if args.rendered else None)
    for f in findings:
        print(f"{f['severity'].upper()} [{f['code']}] {f['path']}: {f['message']}")
    counts = Counter(f['severity'] for f in findings)
    print(f"Editorial QA: {counts['error']} errors, {counts['warning']} review warnings")
    review_categories = Counter(f.get('review_category') for f in findings if f.get('review_category'))
    if review_categories:
        print("Numeric review categories (heuristic, not verified errors):")
        for category, count in sorted(review_categories.items()):
            print(f"  {category}: {count}")
    if args.json:
        args.json.write_text(json.dumps({'errors': counts['error'], 'warnings': counts['warning'],
                                         'review_categories': dict(sorted(review_categories.items())),
                                         'findings': findings}, ensure_ascii=False, indent=2) + '\n')
    return 1 if counts['error'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
