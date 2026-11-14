"""Focused controls for the attached second independent review. All changes to
archive data below occur in memory only; synthetic evidence is never live intake.
"""
import copy
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import eligibility as e
import monitor as m
import operations as o
import state_schema as schema
import test_operations as previous
import test_round2 as round2

CONFIG = json.loads((m.ROOT/'config.json').read_text())
TODAY = date(2026, 11, 14)


class ClassificationConflictTests(unittest.TestCase):
    def test_existing_reanalysis_cannot_be_overridden_by_formatted_proposal(self):
        provenance = {'editor':'Synthetic reviewer', 'approval_reference':'https://example.org/review',
                      'source_references':['https://example.org/primary']}
        for proposed in ('Field discovery', 'Mixed', 'Unresolved'):
            for supplied in (None, provenance):
                with self.subTest(proposed=proposed, provenance=supplied):
                    project = {'reanalysis':True,'research_type':proposed,'research_type_provenance':supplied}
                    result = o.archive_classification(project)
                    self.assertEqual(result['category'],'Reanalysis')
                    self.assertTrue(result['classification_conflict'])
                    self.assertTrue(result['review_required'])
                    self.assertEqual(result['proposed_category'],proposed)
                    self.assertEqual(o.archive_category(project),'Reanalysis')

    def test_compatible_category_does_not_create_conflict_or_reclassify_unresolved(self):
        for project, expected in [({'reanalysis':True},'Reanalysis'),
                                  ({'reanalysis':True,'research_type':'Reanalysis'},'Reanalysis'),
                                  ({'reanalysis':False},'Unresolved')]:
            result=o.archive_classification(project)
            self.assertEqual(result['category'],expected)
            self.assertFalse(result['classification_conflict'])

    def test_conflict_surfaces_in_audit_without_changing_inventory_or_counts(self):
        path=m.ROOT.parent/'editorial/inventory.json'
        before=path.read_bytes()
        inventory=json.loads(before)
        entry=next(p for p in inventory['projects'] if str(p['key'])=='31')
        entry.update(research_type='Field discovery',research_type_provenance={
            'editor':'Synthetic reviewer','approval_reference':'https://example.org/review',
            'source_references':['https://example.org/primary']})
        original=Path.read_text
        def read(file,*args,**kwargs):
            return json.dumps(inventory) if file==path else original(file,*args,**kwargs)
        with patch.object(Path,'read_text',read):
            audit=o.archive_audit(CONFIG)
        self.assertEqual(audit['classification_conflicts'],['31'])
        self.assertEqual(audit['field_reanalysis'],{'Field discovery':0,'Reanalysis':1,'Mixed':0,'Unresolved':32})
        row=next(r for r in audit['rows'] if r['id']=='31')
        self.assertTrue(row['classification_conflict'])
        self.assertTrue(row['classification_review_required'])
        self.assertEqual(row['proposed_field_reanalysis'],'Field discovery')
        self.assertEqual(path.read_bytes(),before)


class PublicationDateEvidenceTests(unittest.TestCase):
    def test_self_reported_first_date_with_no_online_or_print_record_is_blocked(self):
        for route in ('first_substantive_publication','Reanalysis'):
            data=round2.route_data(route)
            data['publication_dates'].update(online=None,print=None)
            for state in ('unknown','not_applicable','verified'):
                for field in ('online','print'):
                    data['publication_dates']['verification'][field]['status']=state
                self.assertIn('ineligible_or_tentative_publication_dates',e.validate(route,{route:data},{'primary-1'},TODAY))
        # Re-authorize the modified dossier: rejection must come from evidence,
        # not merely the old approval hash no longer matching.
        gate=previous.GateTests();gate.setUp()
        gate.dossier['eligibility_evidence']['first_substantive_publication']['publication_dates'].update(online=None,print=None)
        gate.authorize()
        self.assertIn('ineligible_or_tentative_publication_dates',gate.evaluate()['reasons'])

    def test_date_verification_requires_status_rationale_and_receipt_reference(self):
        original=round2.route_data('first_substantive_publication')['publication_dates']
        self.assertTrue(e.publication_dates(original,TODAY,{'primary-1'}))
        for field in ('online','print','first_publication'):
            for change in ({'status':'unknown'},{'source_ids':[]},{'source_ids':['absent']},{'rationale':''}):
                dates=copy.deepcopy(original)
                dates['verification'][field].update(change)
                self.assertFalse(e.publication_dates(dates,TODAY,{'primary-1'}))
        for missing in ('verification','online','print','first_publication'):
            dates=copy.deepcopy(original);del dates[missing]
            self.assertFalse(e.publication_dates(dates,TODAY,{'primary-1'}))

    def test_absent_edition_requires_supported_not_applicable_never_unknown(self):
        for absent in ('online','print'):
            dates=copy.deepcopy(round2.route_data('first_substantive_publication')['publication_dates'])
            dates[absent]=None
            remaining='print' if absent=='online' else 'online'
            dates['first_publication']=dates[remaining]
            dates['verification'][absent]['status']='not_applicable'
            self.assertTrue(e.publication_dates(dates,TODAY,{'primary-1'}))
            dates['verification'][absent]['status']='unknown'
            self.assertFalse(e.publication_dates(dates,TODAY,{'primary-1'}))
            dates['verification'][absent]['status']='not_applicable'
            dates['verification'][absent]['source_ids']=[]
            self.assertFalse(e.publication_dates(dates,TODAY,{'primary-1'}))


class AffiliationAndQueueTests(unittest.TestCase):
    def test_affiliation_only_edits_do_not_create_scholarly_revision(self):
        original={'DOI':'10.1000/control','title':['Synthetic control'],
                  'author':[{'given':'Test','family':'Author','affiliation':[{'name':'Institution, Dept.'}]}],
                  'published-online':{'date-parts':[[2026,1,1]]}}
        changed=copy.deepcopy(original)
        changed['author'][0]['affiliation']=[{'name':'Institution Department','id':'provider-affiliation-identifier'}]
        state=o.empty_state()
        o.update_ledger(state,[m.crossref(original,'crossref','2026-11-13')],CONFIG,'2026-11-13')
        o.update_ledger(state,[m.crossref(changed,'crossref','2026-11-14')],CONFIG,'2026-11-14')
        self.assertEqual(len(state['observations']),1)
        changed['author'][0]['family']='Different author'
        o.update_ledger(state,[m.crossref(changed,'crossref','2026-11-14')],CONFIG,'2026-11-14')
        self.assertEqual(len(state['observations']),2)
        legacy=o.empty_state();legacy['schema']=2
        with self.assertRaises(ValueError):o.validate_state(legacy)
        legacy=o.empty_state();legacy['observation_projection']=2
        with self.assertRaises(ValueError):o.validate_state(legacy)

    def test_issue_queue_disabled_but_manual_review_report_still_available(self):
        workflow=(m.ROOT.parent/'.github/workflows/monitoring-phase2b.yml').read_text()
        queue=workflow.split('  editorial-queue:\n',1)[1].split('  operational-failure-alert:\n',1)[0]
        self.assertIn('    if: false\n',queue)
        self.assertIn('    needs: [collect, persist]\n',queue)
        guide=(m.ROOT/'PHASE2B.md').read_text()
        self.assertIn('Normal Issue queue is disabled',guide)
        self.assertIn('persist is skipped',guide)
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            root=Path(tmp)
            result=o.run('review',root/'state.json',root/'reports','2026-11-14')
            self.assertEqual(result['mode'],'review')
            self.assertTrue((root/'reports/report.json').is_file())
            self.assertTrue((root/'reports/summary.md').is_file())
        # A disabled queue is not an operational failure; independent failure
        # notification remains enabled only for actual failure/cancelled results.
        alert=workflow.split('  operational-failure-alert:\n',1)[1]
        self.assertIn('if: always()',alert)
        self.assertNotIn("needs.editorial-queue.result == 'skipped'",alert)


if __name__=='__main__':
    unittest.main()
