import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import monitor as m

CONFIG = json.loads((m.ROOT/'config.json').read_text())

def record(**kw):
    r = dict(source_id='test', title='Excavation at a settlement', doi=None, url='https://example.org/p',
             publication_date='2026', announcement_date=None, claims={'en':'stratified excavation'}, earlier_history=[])
    r.update(kw)
    return r

class MonitorTests(unittest.TestCase):
    def test_doi_url_normalization(self):
        self.assertEqual(m.doi('https://doi.org/10.1017/S0003598X'), '10.1017/s0003598x')
        self.assertIsNone(m.doi('not a DOI'))
        self.assertEqual(m.url('http://example.org/a/?utm_source=x#p'), 'https://example.org/a')
        self.assertIsNone(m.url('file:///etc/passwd'))

    def test_dates_not_eligibility(self):
        self.assertEqual(m.classify(record(), 2026)[0], 'unresolved')
        self.assertEqual(m.classify(record(first_announcement_claim=True, announcement_date='2026-01-23'),2026)[0], 'first_public_announcement')
        self.assertEqual(m.classify(record(substantive_publication_claim=True),2026)[0], 'first_substantive_publication')
        self.assertEqual(m.classify(record(legacy_material=True),2026)[0], 'Reanalysis')
        self.assertEqual(m.classify(record(legacy_material=True, publication_date='2025'),2026)[0], 'unresolved')

    def test_metadata_conflicts_are_not_verified(self):
        r = record(doi='10.1017/test', title='Reported title')
        v = {'10.1017/test': {'DOI':'10.1017/other', 'title':['Other title'], 'published':{'date-parts':[[2025]]}}}
        out = m.prepare(r, CONFIG, v)
        self.assertEqual(out['metadata_status'], 'conflicting')
        self.assertIn('publication_date_mismatch', out['uncertainty_flags'])
        self.assertEqual(m.prepare(r, CONFIG)['metadata_status'], 'unverified')

    def test_metadata_match_is_only_metadata(self):
        r = record(doi='10.1017/test')
        v = {'10.1017/test': {'DOI':r['doi'], 'title':[r['title']], 'published':{'date-parts':[[2026,2]]}}}
        out = m.prepare(r,CONFIG,v)
        self.assertEqual(out['metadata_status'], 'metadata_matched')
        self.assertEqual(out['url_status'], 'syntax_only_not_resolved')
        self.assertEqual(out['editorial_review'], 'provisional_requires_human_review')

    def test_all_identity_keys_and_transitive_duplicates(self):
        rows = [record(source_id=str(i), title='Same title' if i<2 else 'Different',
                       doi='10.1017/test' if i in [1,2] else None, project_key='site' if i>1 else '') for i in range(4)]
        groups, edges = m.deduplicate([m.prepare(r,CONFIG) for r in rows])
        self.assertEqual(len(groups),1)
        self.assertTrue({'doi','url','title','project'}.issubset({e['basis'] for e in edges}))
        self.assertEqual(len(groups[0]['records']),4)

    def test_same_site_not_silently_assigned(self):
        rows = [record(title='Different '+str(i), url='https://example.org/'+str(i), site='same') for i in range(2)]
        self.assertEqual(len(m.deduplicate([m.prepare(r,CONFIG) for r in rows])[0]),2)

    def test_project_conflict_retains_both_dois(self):
        rows = [record(doi='10.1017/'+str(i),project_key='same',source_id=str(i)) for i in range(2)]
        groups,_=m.deduplicate([m.prepare(r,CONFIG) for r in rows])
        self.assertTrue(groups[0]['identity_conflict'])

    def test_tagging_does_not_use_prestige(self):
        a=m.prepare(record(),CONFIG)
        b=m.prepare(record(journal='Nature',impact_factor=100,cited_by_count=10000),CONFIG)
        self.assertEqual(a['intake_priority'],b['intake_priority'])
        self.assertEqual(a['tags'],b['tags'])
        self.assertIn('stratigraphy',a['tags']['evidence_type'])

    def test_false_positive_undated_and_old(self):
        for d in ['2025',None]:
            out=m.prepare(record(publication_date=d,title='Physics',claims={'en':'quantum'}),CONFIG)
            self.assertEqual(out['screening'],'outside_year_or_undated')
            self.assertIn('possible_non_archaeology_false_positive',out['uncertainty_flags'])

    def test_crossref_retains_distinct_dates(self):
        item={'title':['T'],'published-online':{'date-parts':[[2025,12,20]]},'published-print':{'date-parts':[[2026,3]]}}
        out=m.crossref(item,'cr','2026-11-14')
        self.assertEqual(out['publication_date'],'2025-12-20')
        self.assertIsNone(out['announcement_date'])
        self.assertEqual(out['source_dates']['published-print'],'2026-03')

    def test_watermark_failure_and_cap(self):
        registry={'sources':[{'id':'cr','enabled':True,'adapter':'crossref','access_note':'API'}]}
        state={'cr':'2026-10-01'}
        def fail(_): raise OSError('403')
        _, access, after=m.retrieve(registry,CONFIG,state,'2026-11-14',fail)
        self.assertEqual(after,state)
        self.assertEqual(access[0]['status'],'unavailable')
        def capped(_):return {'message':{'items':[{'title':['T']}]*CONFIG['page_size'],'next-cursor':'next'}}
        _,access,after=m.retrieve(registry,CONFIG,state,'2026-11-14',capped)
        self.assertEqual(after,state)
        self.assertEqual(access[0]['status'],'bounded_incomplete')

    def test_watermark_complete_with_overlap(self):
        registry={'sources':[{'id':'cr','enabled':True,'adapter':'crossref','access_note':'API'}]}
        calls=[]
        def fetch(u):calls.append(u);return {'message':{'items':[]}}
        _,access,after=m.retrieve(registry,CONFIG,{'cr':'2026-10-01'},'2026-11-14',fetch)
        self.assertEqual(after['cr'],'2026-11-14')
        self.assertIn('2026-09-24',calls[0])

    def test_offline_no_network_deterministic(self):
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            with patch.object(m,'get_json',side_effect=AssertionError('offline network')):
                m.main(['--output',tmp,'--as-of','2026-11-14'])
                first={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
                m.main(['--output',tmp,'--as-of','2026-11-14'])
                self.assertEqual(first,{p.name:p.read_bytes() for p in Path(tmp).iterdir()})
        fixture=json.loads((m.ROOT/'fixtures/sample.json').read_text())
        data=m.report(fixture['records'],CONFIG,fixture['source_access'])
        self.assertEqual(len(data['candidates']),17)
        self.assertEqual(sum(g['duplicate_count'] for g in data['candidates']),4)

    def test_output_cannot_touch_editorial_files(self):
        for p in [m.ROOT.parent/'discoveries.qmd',m.ROOT.parent/'editorial',m.ROOT/'../ranking.qmd']:
            with self.assertRaises(ValueError):m.safe_output(p)

    def test_invalid_dates_and_input_immutability(self):
        row=record(publication_date='2026-99-99')
        original=copy.deepcopy(row)
        out=m.prepare(row,CONFIG)
        self.assertEqual(row,original)
        self.assertIn('invalid_publication_date',out['uncertainty_flags'])
        self.assertEqual(out['screening'],'outside_year_or_undated')

    def test_geographic_false_match(self):
        out=m.prepare(record(title='Indonesia boat',claims={'en':'Indonesian maritime study'}),CONFIG)
        self.assertIn('Southeast Asia',out['tags']['geographic'])
        self.assertNotIn('South Asia',out['tags']['geographic'])

    def test_synthetic_false_positive_controls(self):
        rows=json.loads((m.ROOT/'fixtures/screening_controls.json').read_text())['records']
        result=[m.prepare(r,CONFIG) for r in rows]
        self.assertIn('possible_non_archaeology_false_positive',result[0]['uncertainty_flags'])
        self.assertEqual(result[1]['screening'],'outside_year_or_undated')
        self.assertEqual(result[2]['classification_proposal'],'unresolved')

    def test_disabled_institutions_never_fetched(self):
        registry=json.loads((m.ROOT/'sources.json').read_text())
        registry['sources']=[s for s in registry['sources'] if s['adapter']=='manual_primary']
        def fail(_):raise AssertionError('Institution scraping attempted')
        rows,access,state=m.retrieve(registry,CONFIG,{},'2026-11-14',fail)
        self.assertEqual(rows,[])
        self.assertTrue(all(a['status']=='not_fetched' for a in access))

    def test_preserve_academic_content(self):
        files=list((m.ROOT.parent/'discoveries').glob('*.qmd'))+[m.ROOT.parent/p for p in ['discoveries.qmd','ranking.qmd','under-review.qmd','map.html','editorial/inventory.json']]
        before={str(p):p.read_bytes() for p in files}
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            m.main(['--output',tmp])
        self.assertEqual(before,{str(p):p.read_bytes() for p in files})

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            link=Path(tmp)/'outside'
            link.symlink_to(m.ROOT.parent,target_is_directory=True)
            with self.assertRaises(ValueError):m.safe_output(link/'ranking.qmd')

    def test_feed_timestamp_is_not_first_announcement(self):
        rows=m.parse_feed('<rss><channel><item><title>A</title><link>https://example.org/a</link><pubDate>Thu, 01 Jan 2026 00:00:00 GMT</pubDate></item></channel></rss>','feed','2026-11-14')
        self.assertIsNone(rows[0]['announcement_date'])
        self.assertIn('2026',rows[0]['feed_timestamp'])

if __name__=='__main__':unittest.main()
