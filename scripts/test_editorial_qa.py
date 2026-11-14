"""Mutation tests against an isolated copy: never change academic source files."""
from pathlib import Path
import shutil
import tempfile
import unittest

from editorial_qa import numbers, numeric_review_hint, run


SOURCE = Path(__file__).resolve().parents[1]


class EditorialQA(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('discoveries', 'editorial', 'figures', 'map-assets'):
            shutil.copytree(SOURCE / name, self.root / name)
        for path in SOURCE.glob('*.qmd'):
            shutil.copy(path, self.root / path.name)
        shutil.copy(SOURCE / 'map.html', self.root / 'map.html')

    def mutate(self, name, old, new):
        p = self.root / name
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1))

    def codes(self, severity='error'):
        return {f['code'] for f in run(self.root) if f['severity'] == severity}

    def test_current_corpus_and_no_source_writes(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.codes(), set())
        self.assertIn('reanalysis-label', self.codes('warning'))
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_chinese_summary_count(self):
        self.mutate('index.qmd', '全部33项发现', '全部34项发现')
        self.assertIn('summary-count', self.codes())

    def test_missing_english_summary_not_silent(self):
        self.mutate('index.qmd', 'all 33 discoveries', 'all discoveries')
        self.assertIn('summary-count', self.codes())

    def test_status_disagreement(self):
        self.mutate('discoveries/29-etowah-cacao.qmd', 'Under review — Reanalysis', 'Additional candidate — Reanalysis')
        self.assertIn('page-status', self.codes())

    def test_evidence_translation_disagreement(self):
        self.mutate('discoveries/01-wonderwerk-fire.qmd', 'B级', 'A级')
        self.assertIn('page-grade', self.codes())

    def test_rank_grade_disagreement(self):
        self.mutate('ranking.qmd', 'Evidence:** A', 'Evidence:** D')
        self.assertIn('rank-grade', self.codes())

    def test_rank_change_needs_review(self):
        self.mutate('ranking.qmd', '### 1.', '### 2.')
        self.assertTrue({'rank-baseline', 'rank-sequence'} <= self.codes())

    def test_decision_change(self):
        self.mutate('under-review.qmd', 'decision: HOLD', 'decision: PROMOTE')
        self.assertIn('review-decision', self.codes())

    def test_retired_id_not_formal(self):
        p = self.root / 'discoveries.qmd'
        p.write_text(p.read_text() + '\n| 29 | [Etowah](discoveries/29-etowah-cacao.qmd) | USA | CE | Additional candidate / 补充建议 |\n')
        self.assertIn('formal-membership', self.codes())

    def test_stable_id(self):
        self.mutate('discoveries.qmd', '| 1 |', '| 99 |')
        self.assertIn('stable-id', self.codes())

    def test_map_status(self):
        self.mutate('map.html', '<circle class="marker extra"', '<circle class="marker cctv"')
        self.assertIn('map-status', self.codes())

    def test_map_duplicate_with_unchanged_count(self):
        self.mutate('map.html', 'href="discoveries/02-yunxian-homo-erectus.html"', 'href="discoveries/01-wonderwerk-fire.html"')
        self.assertIn('map-membership', self.codes())

    def test_map_missing_marker(self):
        self.mutate('map.html', 'class="marker cctv"', 'class="hidden"')
        self.assertIn('map-membership', self.codes())

    def test_mobile_map_membership(self):
        self.mutate('map.html', '<option value="discoveries/01-wonderwerk-fire.html"', '<option value="missing.html"')
        self.assertIn('map-options', self.codes())

    def test_missing_internal_source_link(self):
        self.mutate('index.qmd', '](cctv.qmd)', '](missing.qmd)')
        self.assertIn('internal-link', self.codes())

    def test_missing_rendered_output_is_failure(self):
        codes = {f['code'] for f in run(self.root, self.root / 'empty-output')}
        self.assertIn('rendered-missing', codes)

    def test_bilingual_numeric_drift_is_visible(self):
        self.mutate('discoveries/30-roman-iberia-adna.qmd', 'reports genome-wide data from 243', 'reports genome-wide data from 999')
        warnings = [f for f in run(self.root) if f['code'] == 'bilingual-numbers']
        self.assertTrue(any('999' in f['message'] and '30-roman' in f['path'] for f in warnings))

    def test_common_scale_units(self):
        self.assertEqual(numbers('6.78万年前'), numbers('67.8 ka'))
        self.assertEqual(numbers('1.8 Ma'), numbers('180万年前'))

    def test_english_million_and_thousand_scales(self):
        self.assertEqual(numbers('1.77 million years ago'), numbers('177万年前'))
        self.assertEqual(numbers('1.8 Ma'), numbers('180万年前'))
        self.assertEqual(numbers('14.2 thousand years ago'), numbers('1.42万年前'))

    def test_shared_unit_ranges(self):
        self.assertEqual(numbers('14.2–15.8 ka'), numbers('1.42万–1.58万年前'))
        self.assertEqual(numbers('1.7 to 1.8 Ma'), numbers('170万至180万年前'))
        self.assertEqual(numbers('55–37 ka'), numbers('5.5万–3.7万年前'))
        self.assertEqual(numbers('55–37 ka层段'), numbers('5.5万–3.7万年前'))
        self.assertEqual(numbers('Between roughly 55 and 37 ka'), numbers('55–37 ka'))
        self.assertEqual(numbers('between about 64 and 55 ka'), numbers('64–55 ka'))
        self.assertEqual(numbers('1.77 Ma年代'), numbers('177万年前'))

    def test_english_number_words_are_review_not_guessed(self):
        self.assertEqual(numeric_review_hint('5至8项', 'five to eight cases'),
                         'spelled-number-or-scope')
        self.assertNotEqual(numbers('five to eight'), numbers('5–8'))

    def test_true_number_conflict_still_visible(self):
        self.assertNotEqual(numbers('14.2 ka'), numbers('15.8 thousand years'))
        self.assertEqual(numeric_review_hint('14.2 ka', '15.8 thousand years'),
                         'unit-or-range-context')

    def test_normalized_equivalent_quantities(self):
        self.assertEqual(numbers('1.77 million'), numbers('177万'))
        self.assertEqual(numbers('55–37 ka'), numbers('55 to 37 thousand years ago'))

    def test_review_category_is_machine_readable(self):
        self.mutate('discoveries/30-roman-iberia-adna.qmd',
                    'reports genome-wide data from 243',
                    'reports genome-wide data from 999')
        findings = [f for f in run(self.root) if f['code'] == 'bilingual-numbers']
        self.assertTrue(any(f.get('review_category') for f in findings))

    def test_rendered_fragment(self):
        site = self.root / 'rendered'
        site.mkdir()
        (site / 'a.html').write_text('<a href="b.html#absent">B</a>')
        (site / 'b.html').write_text('<h1 id="present">B</h1>')
        findings = run(self.root, site)
        self.assertTrue(any(f['code'] == 'internal-fragment' for f in findings))

    def test_same_page_fragment(self):
        site = self.root / 'rendered'
        site.mkdir()
        (site / 'a.html').write_text('<a href="#absent">Missing</a>')
        self.assertTrue(any(f['code'] == 'internal-fragment' for f in run(self.root, site)))


if __name__ == '__main__':
    unittest.main()
