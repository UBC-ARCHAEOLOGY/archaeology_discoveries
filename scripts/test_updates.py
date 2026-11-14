"""Registry mutation tests: chronology, evidence, identity and proposal separation."""
import copy
from datetime import date, datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo
import updates as u

AS_OF=date(2026,11,14)


class UpdatesTests(unittest.TestCase):
    def setUp(self):
        (u.ROOT/'work').mkdir(exist_ok=True)
        self.data=json.loads((u.ROOT/'updates.json').read_text())
        self.data['records']=[r for r in self.data['records'] if r['state']=='baseline']

    def validate(self,data):
        return u.validate(data,as_of=AS_OF)

    def test_baseline_is_evidenced_bilingual_and_does_not_invent_website_dates(self):
        self.validate(self.data)
        self.assertEqual(len(self.data['records']),6)
        self.assertEqual({r['category'] for r in self.data['records']},set(u.BASELINE_CATEGORIES))
        self.assertTrue(all(r['state']=='baseline' and r['website_updated_on'] is None for r in self.data['records']))
        for r in self.data['records']:
            for field in ('discovery_date','announcement_date','publication_date'):
                self.assertNotEqual(r[field]['value'],'2026-01-01')
        self.assertIn('Retrospective archive baseline',u.render(self.data,'history'))
        self.assertEqual(u.render(self.data,'latest',AS_OF).count('<article '),0)

    def test_duplicate_id_title_and_substantive_identity_fail(self):
        for variant in ('id','title','identity'):
            data=copy.deepcopy(self.data);row=copy.deepcopy(data['records'][0])
            if variant!='id':row['id']='another-record'
            if variant=='identity':row['title']={'zh':'不同标题','en':'Different title'}
            data['records'].append(row)
            with self.subTest(variant=variant),self.assertRaises(ValueError):self.validate(data)

    def test_category_dates_and_precision_fail_closed(self):
        mutations=[('category','PROMOTE'),('recorded_on','2026-02-30'),('recorded_on','2027-01-01'),
                   ('recorded_on','2026'),('website_updated_on','2026-11-14')]
        for key,value in mutations:
            data=copy.deepcopy(self.data);data['records'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.validate(data)
        for value,precision in [('2026-01-01','year'),('2026-99','month'),('2026-02-30','day')]:
            data=copy.deepcopy(self.data);data['records'][0]['publication_date'].update(value=value,precision=precision)
            with self.assertRaises(ValueError):self.validate(data)

    def test_local_and_source_links_must_exist_and_be_supported(self):
        for key,value in [('page','missing.qmd'),('page','../outside.qmd'),('page','https://example.org/a'),
                          ('source_url','javascript:alert(1)'),('source_url','http://example.org/a'),
                          ('source_url','https://example.org/not-in-page')]:
            data=copy.deepcopy(self.data);data['records'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.validate(data)
        data=copy.deepcopy(self.data);next(r for r in data['records'] if r['category']=='publication_added')['source_url']=None
        with self.assertRaises(ValueError):self.validate(data)

    def test_source_quotations_hashes_and_date_values_are_checked(self):
        for mutation in ('quote','sha256','date'):
            data=copy.deepcopy(self.data)
            if mutation=='date':data['records'][0]['publication_date']['value']='2026-02-23'
            else:data['records'][0]['evidence'][0][mutation]='Not supported'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):self.validate(data)

    def test_bilingual_completeness_and_numbers(self):
        for value in ({'zh':'中文','en':''},{'zh':'2026年','en':'2025'},{'en':'English only'}):
            data=copy.deepcopy(self.data);data['records'][0]['description']=value
            with self.assertRaises(ValueError):self.validate(data)

    def reviewed(self,row,when):
        row.update(state='reviewed',website_updated_on=when,
                   website_date_evidence={'reference':'https://example.org/release','description':{'zh':'合成测试','en':'Synthetic control'}},
                   review={'editor':'Synthetic test editor','reference':'https://example.org/review'})
        return row

    def test_real_website_dates_order_independently_of_publication_or_input_order(self):
        data=copy.deepcopy(self.data)
        old=self.reviewed(data['records'][0],'2026-11-12')
        new=self.reviewed(data['records'][1],'2026-11-13')
        # Publication dates do not supply website chronology.
        old['publication_date']={'value':None,'precision':'unknown','evidence':None}
        self.validate(data)
        reviewed,baseline=u.ordered(data)
        self.assertEqual([r['id'] for r in reviewed],[new['id'],old['id']])
        html=u.render(data,'latest',AS_OF)
        self.assertLess(html.index(new['id']),html.index(old['id']))
        self.assertNotIn('updates-baseline-label',html)

    def test_reviewed_record_requires_editor_and_website_date_evidence(self):
        for missing in ('review','website_date_evidence','website_updated_on'):
            data=copy.deepcopy(self.data);self.reviewed(data['records'][0],'2026-11-14');data['records'][0][missing]=None
            with self.assertRaises(ValueError):self.validate(data)

    def test_proposals_cannot_publish_or_overwrite_registry(self):
        before=(u.ROOT/'updates.json').read_bytes()
        with tempfile.TemporaryDirectory(dir=u.ROOT/'work') as tmp:
            candidate=copy.deepcopy(self.data['records'][0])
            self.reviewed(candidate,'2026-11-14')
            candidate['source_url']='https://example.org/unverified-new-paper'
            candidate['evidence']=[]
            destination=Path(tmp)/'proposal.json'
            u.propose(candidate,destination)
            payload=json.loads(destination.read_text());row=payload['record']
            self.assertEqual(row['state'],'proposed')
            self.assertIsNone(row['website_updated_on']);self.assertIsNone(row['review'])
            self.assertIn('reported_dates_unverified',payload)
            data=copy.deepcopy(self.data);row['id']='proposal-control';row['title']={'zh':'待审提案','en':'Pending proposal'}
            data['records'].append(row)
            self.validate(data)
            self.assertNotIn('proposal-control',u.render(data,'latest',AS_OF))
            self.assertNotIn('proposal-control',u.render(data,'history'))
            with self.assertRaises(ValueError):u.propose(candidate,u.ROOT/'updates.json')
        self.assertEqual((u.ROOT/'updates.json').read_bytes(),before)

    def test_english_only_automated_proposal_is_retained_but_never_rendered(self):
        row=copy.deepcopy(self.data['records'][0])
        row.update(id='english-only-proposal', title={'en':'Unverified source lead'},
                   description={'en':'Draft source claim awaiting bilingual and primary review.'},
                   source_url='https://example.org/new-paper', evidence=[])
        with tempfile.TemporaryDirectory(dir=u.ROOT/'work') as tmp:
            output=Path(tmp)/'proposal.json';u.propose(row,output)
            payload=json.loads(output.read_text());draft=payload['record']
            self.assertEqual(draft['title']['zh'],'')
            self.assertIn('bilingual_review_pending',payload['review_flags'])
            data=copy.deepcopy(self.data);data['records'].append(draft)
            self.validate(data)
            self.assertNotIn('english-only-proposal',u.render(data,'latest',AS_OF))
            self.assertNotIn('english-only-proposal',u.render(data,'history'))
            draft['state']='baseline'
            with self.assertRaises(ValueError):self.validate(data)

    def test_proposal_symlink_cannot_escape_to_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'work').symlink_to(root,target_is_directory=True)
            with self.assertRaises(ValueError):u.propose(self.data['records'][0],root/'work/updates.json',root)
            self.assertFalse((root/'updates.json').exists())

    def test_plain_text_is_escaped_not_executable_markup(self):
        data=copy.deepcopy(self.data);self.reviewed(data['records'][0],'2026-11-14');data['records'][0]['title']={'zh':'<script>攻击</script>','en':'<script>attack</script>'}
        self.validate(data)
        html=u.render(data,'latest',AS_OF)
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('.qmd"',html)

    def test_history_retains_records_beyond_homepage_limit(self):
        data=copy.deepcopy(self.data)
        row=copy.deepcopy(data['records'][0]);row['id']='seventh-record';row['title']={'zh':'另一个研究更新','en':'Another research update'};row['category']='research_update'
        row['page']='discoveries/24-sheg-xdaltthi.qmd';row['source_url']=None
        self.reviewed(row,'2026-11-14')
        data['records'].append(row)
        self.validate(data)
        self.assertEqual(u.render(data,'latest',AS_OF).count('<article '),1)
        self.assertEqual(u.render(data,'history').count('<article '),7)

    def test_seventh_baseline_and_replacement_with_unapproved_baseline_are_rejected(self):
        row=copy.deepcopy(self.data['records'][0])
        row.update(id='new-unapproved-baseline',title={'zh':'另一条记录','en':'Another record'},
                   category='research_update',page='discoveries/24-sheg-xdaltthi.qmd',source_url=None)
        for replace in (False,True):
            data=copy.deepcopy(self.data)
            if replace:data['records'][0]=row
            else:data['records'].append(row)
            with self.assertRaisesRegex(ValueError,'six bootstrap IDs'):self.validate(data)

    def test_known_bootstrap_id_cannot_be_reused_for_changed_content_or_day(self):
        data=copy.deepcopy(self.data)
        data['records'][0]['description']={'zh':'经过改写的内容','en':'Changed content'}
        with self.assertRaisesRegex(ValueError,'Frozen baseline content changed'):self.validate(data)
        data=copy.deepcopy(self.data);data['registry_created_on']='2026-11-13';data['records'][0]['recorded_on']='2026-11-13'
        with self.assertRaisesRegex(ValueError,'recording day is fixed'):self.validate(data)

    def test_full_proposal_cannot_gain_publication_by_becoming_baseline(self):
        row=copy.deepcopy(self.data['records'][0])
        row.update(id='proposal-cast-to-baseline',title={'zh':'待审记录','en':'Pending record'},state='proposed')
        data=copy.deepcopy(self.data);data['records'][0]=row
        self.validate(data)
        self.assertNotIn(row['id'],u.render(data,'latest',AS_OF))
        row['state']='baseline'
        with self.assertRaisesRegex(ValueError,'six bootstrap IDs'):self.validate(data)
        row['state']='reviewed'
        with self.assertRaises(ValueError):self.validate(data)

    def test_same_page_source_cannot_duplicate_by_category_or_date(self):
        for category in u.CATEGORIES:
            for when in ('2026-11-13','2026-11-14'):
                data=copy.deepcopy(self.data)
                duplicate=copy.deepcopy(data['records'][0])
                duplicate.update(id='duplicate-event',title={'zh':'另一标题','en':'Different title'},category=category)
                self.reviewed(duplicate,when)
                data['records'].append(duplicate)
                with self.subTest(category=category,date=when),self.assertRaisesRegex(ValueError,'Duplicate substantive update'):
                    self.validate(data)

    def test_baseline_labels_and_date_prominence_are_state_specific(self):
        home=u.render(self.data,'latest',AS_OF);history=u.render(self.data,'history')
        for label in ('Existing archive entry','Existing publication reference','Existing research note'):
            self.assertIn(label,history)
        self.assertNotIn('Archive entry added',history)
        self.assertNotIn('Reference added',history)
        self.assertNotIn('<time',home)
        self.assertNotIn('update-dates',home)
        self.assertEqual(history.count('class="update-recorded-date"'),6)
        self.assertEqual(history.count('<dl class="update-dates">'),6)
        self.assertNotIn('class="update-date"',history)
        data=copy.deepcopy(self.data);self.reviewed(data['records'][0],'2026-11-14')
        rendered=u.render(data,'latest',AS_OF)
        self.assertIn('Window:',rendered)
        self.assertIn('Archive entry added',rendered)
        self.assertIn('<time datetime="2026-11-14">',rendered)

    def test_week_window_is_inclusive_and_excludes_stale_future_baseline_proposed(self):
        data=copy.deepcopy(self.data)
        for i,day in enumerate(('2026-11-14','2026-11-15','2026-11-21','2026-11-22')):
            row=copy.deepcopy(data['records'][i]);self.reviewed(row,day)
            data['records'][i]=row
        draft=copy.deepcopy(data['records'][0]);draft.update(id='draft',state='proposed')
        data['records'].append(draft)
        rows=u.recent(data,date(2026,11,21))
        self.assertEqual([r['website_updated_on'] for r in rows],['2026-11-21','2026-11-15'])
        self.assertNotIn('draft',u.render(data,'latest',date(2026,11,21)))
        self.assertEqual(u.render(data,'latest',date(2026,11,21)).count('<article '),2)
        self.assertIn('2026-11-15 – 2026-11-21',u.render(data,'latest',date(2026,11,21)))

    def test_live_registry_and_ranking_other_categories_keep_review_gate(self):
        registry=u.load()
        self.assertEqual(len([r for r in registry['records'] if r['state']=='baseline']),6)
        self.assertTrue(any(r['id']=='website-update-history-launch' for r in registry['records']))
        for category in ('ranking_changed','site_updated'):
            data=copy.deepcopy(self.data);r=self.reviewed(data['records'][0],'2026-11-14')
            r['category']=category;self.validate(data)
            html=u.render(data,'latest',AS_OF)
            self.assertIn('href="discoveries/25-huitzo-tomb-10.html"',html)
            self.assertIn(u.CATEGORIES[category][1],html)
            r['review']=None
            with self.assertRaises(ValueError):self.validate(data)


    def test_today_uses_beijing_midnight_not_vancouver_or_utc(self):
        self.assertEqual(u.UPDATE_TIMEZONE,'Asia/Shanghai')
        for instant, expected in [('2026-11-14T15:59:59+00:00',date(2026,11,14)),
                                  ('2026-11-14T16:00:00+00:00',date(2026,11,15))]:
            with patch('updates.datetime',wraps=datetime) as clock:
                clock.now.return_value=datetime.fromisoformat(instant).astimezone(ZoneInfo(u.UPDATE_TIMEZONE))
                self.assertEqual(u.today(),expected)
                clock.now.assert_called_once_with(ZoneInfo('Asia/Shanghai'))

    def test_receipt_timestamp_requires_matching_beijing_date(self):
        data=copy.deepcopy(self.data);row=self.reviewed(data['records'][0],'2026-11-14')
        row['website_date_evidence']['published_at']='2026-11-13T16:00:00Z'
        self.validate(data)
        row['website_date_evidence']['published_at']='2026-11-13T15:59:59Z'
        with self.assertRaisesRegex(ValueError,'Beijing time'):self.validate(data)
        for stamp in ('2026-11-13T16:00:00','not-a-time'):
            row['website_date_evidence']['published_at']=stamp
            with self.assertRaisesRegex(ValueError,'UTC deployment timestamp'):self.validate(data)



if __name__=='__main__':unittest.main()
