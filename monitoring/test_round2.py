"""Targeted controls for independent review findings 1–10. All dossier facts synthetic."""
import ast
import copy
from datetime import date
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import eligibility as e
import monitor as m
import operations as o
import state_schema as schema
import state_store as store
import test_operations as prior_tests

CONFIG = json.loads((m.ROOT/'config.json').read_text())
REGISTRY = json.loads((m.ROOT/'sources.json').read_text())
TODAY = date(2026, 11, 14)


def statement():
    return {'statement': 'Synthetic controlled review evidence, not a real finding', 'source_ids': ['primary-1']}


def route_data(route):
    if route == 'first_public_announcement':
        return {'announcement_date': '2026-01-02', 'fieldwork_dates': ['2024-05-01'],
                'first_announcement_confirmed': True, 'announcement_source_ids': ['primary-1'],
                'field_context_source_ids': ['primary-1'], 'earlier_announcement_search': statement()}
    common = {'publication_dates': {'online':'2026-02-01', 'print':'2026-03-01', 'first_publication':'2026-02-01'},
              'publication_source_ids': ['primary-1'], 'peer_reviewed': True,
              'earlier_publications': [{'date':'2022-01-01','stage':'preliminary','description':'Synthetic prior report','source_ids':['primary-1']}],
              'history_search': statement()}
    if route == 'first_substantive_publication':
        return {**common, 'substantive_increment': statement()}
    return {**common, 'legacy_material': True,
            'legacy_provenance': {'material_or_dataset': 'Synthetic collection', 'original_dates': ['1950-01-01'], 'source_ids':['primary-1']},
            'analysis_date':'2026-01-15', 'important_question': statement(),
            'interpretive_gain': statement(), 'gain_type':'major_new_interpretation'}


class IdentityRevisionTests(unittest.TestCase):
    def setUp(self):
        self.raw = {'DOI':'10.1000/control', 'title':['Synthetic archaeology control'],
                    'author':[{'given':'Synthetic','family':'Control'}], 'abstract':'Controlled abstract',
                    'published-online':{'date-parts':[[2026,1,1]]},
                    'indexed': {'date-parts':[[2026,11,1]]}, 'is-referenced-by-count':1,
                    'reference':[{'key':'r1','unstructured':'Provider reference control'}]}

    def record(self, item, source='crossref', when='2026-11-14'):
        return m.crossref(item,source,when)

    def test_indexed_deposited_counts_references_score_and_source_do_not_create_revision(self):
        changed = {**self.raw, 'indexed':{'date-parts':[[2026,11,14]]},
                   'deposited':{'timestamp':999}, 'is-referenced-by-count':999, 'reference-count':8,
                   'reference':[{'unstructured':'Changed provider bibliography'}], 'score':99}
        state = o.empty_state()
        o.update_ledger(state,[self.record(self.raw)],CONFIG,'2026-11-13')
        o.update_ledger(state,[self.record(changed,'antiquity')],CONFIG,'2026-11-14')
        self.assertEqual(len(state['observations']),1)
        row = next(iter(state['observations'].values()))
        self.assertEqual(row['first_seen'],'2026-11-13')
        self.assertEqual(row['source_ids'],['antiquity','crossref'])
        o.validate_state(state)

    def test_scholarly_title_abstract_dates_authors_and_retractions_preserve_revisions(self):
        for field, value in [('title',['Revised scholarly title']),('abstract','Revised interpretation'),
                             ('published-online',{'date-parts':[[2025,12,1]]}),
                             ('author',[{'family':'Different author'}]),
                             ('update-to',[{'type':'retraction','DOI':'10.1000/retraction'}]),
                             ('relation',{'is-corrected-by':[{'id':'10.1000/correction'}]})]:
            with self.subTest(field=field):
                state=o.empty_state()
                o.update_ledger(state,[self.record(self.raw),self.record({**self.raw,field:value})],CONFIG,'2026-11-14')
                self.assertEqual(len(state['observations']),2)
                self.assertEqual(len(o.identity_groups(state['observations'])),1)


class RouteAndProvenanceTests(unittest.TestCase):
    def test_all_three_routes_have_distinct_complete_structures(self):
        for route in e.ROUTES:
            data=route_data(route)
            self.assertEqual(e.validate(route,{route:data},{'primary-1'},TODAY),[])
            for field in data:
                incomplete=copy.deepcopy(data);del incomplete[field]
                with self.subTest(route=route,missing=field):
                    self.assertTrue(e.validate(route,{route:incomplete},{'primary-1'},TODAY))

    def test_announcement_requires_announcement_not_a_bibliographic_date(self):
        route='first_public_announcement'
        for change in [{'announcement_date':None},{'announcement_date':'2025-01-01'},
                       {'announcement_date':'2026'}, {'announcement_date':'2026-12-01'},
                       {'fieldwork_dates':[]},{'fieldwork_dates':['2026-01-03']},
                       {'first_announcement_confirmed':False}, {'announcement_source_ids':['absent']}]:
            self.assertTrue(e.validate(route,{route:{**route_data(route),**change}},{'primary-1'},TODAY))

    def test_separate_online_print_history_and_increment(self):
        route='first_substantive_publication';data=route_data(route)
        for change in [{'publication_dates': {'online':'2025-12-01','print':'2026-03-01','first_publication':'2026-03-01'}},
                       {'publication_dates': {'online':'2026-02-01','print':'2026-03-01','first_publication':'2026-03-01'}},
                       {'earlier_publications':None},{'earlier_publications':[{'date':'2022'}]},
                       {'substantive_increment':{'statement':'Unsupported free text','source_ids':[]}}, {'peer_reviewed':False}]:
            self.assertTrue(e.validate(route,{route:{**data,**change}},{'primary-1'},TODAY))

    def test_reanalysis_requires_legacy_dates_2026_analysis_and_major_gain(self):
        route='Reanalysis';data=route_data(route)
        for change in [{'legacy_material':False},{'legacy_provenance':statement()},
                       {'legacy_provenance':{'material_or_dataset':'Control','original_dates':['2026-12-01'],'source_ids':['primary-1']}},
                       {'analysis_date':'2025-12-01'},{'analysis_date':'2026-03-01'},
                       {'gain_type':'sample_expansion'},{'important_question':None},{'interpretive_gain':None}]:
            self.assertTrue(e.validate(route,{route:{**data,**change}},{'primary-1'},TODAY))

    def test_https_receipt_is_raw_scheme_not_generic_normalization(self):
        control=prior_tests.GateTests();control.setUp()
        for url in ['http://example.org/test','https://name:password@example.org/test',
                    ' https://example.org/test','https://example.org/test\n', 'https://localhost/test',
                    'https://127.0.0.1/test','https://example.org:bad/test','https://example.org\\@attacker.example/test']:
            with self.subTest(url=url):
                control.dossier['primary_sources'][0]['url']=url
                control.authorize()
                self.assertIn('invalid_primary_provenance',control.evaluate()['reasons'])
        self.assertEqual(m.url('http://example.org/test'),'https://example.org/test')
        self.assertTrue(e.https_provenance_url('https://example.org/test'))

    def test_receipt_hash_time_status_and_ids_bound_to_dossier(self):
        for field,value in [('sha256','wrong'),('retrieved_at','2026-11-14'),
                            ('retrieved_at','2026-12-01T00:00:00Z'),('http_status',True),('id','')]:
            control=prior_tests.GateTests();control.setUp()
            control.dossier['primary_sources'][0][field]=value;control.authorize()
            self.assertFalse(control.evaluate()['allowed'])
        control=prior_tests.GateTests();control.setUp()
        control.dossier['primary_sources'][0]['sha256']='b'*64
        self.assertIn('no_bound_editor_authorization',control.evaluate()['reasons'])

    def test_gate_accepts_only_structure_complete_announcements_and_reanalysis(self):
        for route in e.ROUTES:
            control=prior_tests.GateTests();control.setUp()
            control.dossier['eligibility_route']=route
            control.dossier['eligibility_evidence']={route:route_data(route)}
            if route=='first_public_announcement':
                control.dossier.pop('publication_dates',None)
            control.authorize()
            self.assertTrue(control.evaluate()['allowed'])
            control.dossier['eligibility_evidence'][route].clear();control.authorize()
            self.assertFalse(control.evaluate()['allowed'])


class StrictStateTests(unittest.TestCase):
    def state(self):
        state=o.empty_state()
        row=m.crossref({'DOI':'10.1000/control','title':['Synthetic control']},'crossref','2026-11-14')
        o.update_ledger(state,[row],CONFIG,'2026-11-14')
        state['sources']['crossref']={'pending':{'since':'2026-01-01','until':'2026-11-14','cursor':'*'}}
        state['runs']['2026-11-14:monitor']={'report_sha256':'a'*64,'outages':['crossref']}
        return state

    def test_nested_observation_allowlists_types_dates_and_hashes(self):
        original=self.state();schema.validate(original,REGISTRY,CONFIG,TODAY)
        mutations=[('source_ids',['attacker']),('tags',{'geographic':['SECRET coordinates']}),
                   ('tags',{**next(iter(original['observations'].values()))['tags'],'geographic':['SECRET coordinates']}),
                   ('tags',{**next(iter(original['observations'].values()))['tags'],'injected':['secret']}),
                   ('identity_keys',['not-a-hash']),('identity_keys','a'*64),
                   ('classification','Field discovery'),('classification','attacker'),
                   ('first_seen','2026'),('last_seen','2025-01-01'),('last_seen','2026-12-01')]
        for field,value in mutations:
            state=copy.deepcopy(original);next(iter(state['observations'].values()))[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                schema.validate(state,REGISTRY,CONFIG,TODAY)

    def test_unknown_top_level_taxonomy_old_schema_sources_windows_runs_and_parent(self):
        original=self.state()
        bad_states=[]
        for field,value in [('latest_report',{'secret':'unvalidated'}),('unexpected','secret'),
                            ('schema',1),('taxonomy_sha256','a'*64),('_parent','not-a-commit'),
                            ('sources',{'attacker':{}}),('sources',{'crossref':{'pending':{'since':'2026-11-14','until':'2026-01-01','cursor':'*'}}}),
                            ('sources',{'crossref':{'pending':{'since':'2026-01-01','until':'2026-11-14','cursor':'private text'}}}),
                            ('sources',{'crossref':{'watermark':'2026-99-99'}}),
                            ('runs',{'2026-11-14:monitor':{'report_sha256':'bad','outages':[]}})]:
            bad_states.append({**original,field:value})
        for state in bad_states:
            with self.assertRaises(ValueError):schema.validate(state,REGISTRY,CONFIG,TODAY)
        with self.assertRaises(ValueError):schema.decode(b'{"schema":2,"schema":2}',REGISTRY,CONFIG)

    def test_access_diagnostics_allowlist_and_restore_validates_before_replace(self):
        state=self.state()
        state.update(last_monitor_date='2026-11-14',last_monitor_access=[{
            'source':'crossref','status':'incomplete','diagnostic':'SECRET error body',
            'pages':0,'watermark_advanced':False,'since':'2026-01-01','until':'2026-11-14'}])
        with self.assertRaises(ValueError):schema.validate(state,REGISTRY,CONFIG,TODAY)
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            path=Path(tmp)/'state.json';o.atomic_json(path,o.empty_state());before=path.read_bytes()
            with patch.object(store,'remote_head',return_value='a'*40),patch.object(store,'remote_payload',return_value=json.dumps(state).encode()),patch.object(store,'git') as git:
                git.return_value.stdout=json.dumps(state).encode()
                with self.assertRaises(ValueError):store.restore(path)
            self.assertEqual(path.read_bytes(),before)

    def test_remote_size_checked_before_blob_read_and_git_token_not_in_arguments(self):
        with patch.object(store,'git',return_value=type('Result',(),{'stdout':str(schema.MAX_BYTES+1).encode()})()) as git:
            with self.assertRaises(ValueError):store.remote_payload('a'*40)
            self.assertEqual(git.call_count,1)
            self.assertEqual(git.call_args.args[0],'cat-file')
        with patch.dict('os.environ',{'GH_TOKEN':'synthetic-token'}),patch.object(subprocess,'run') as process:
            store.git('ls-remote','origin',store.REF)
            self.assertNotIn('synthetic-token',repr(process.call_args.args))
            self.assertEqual(process.call_args.kwargs['env']['GIT_CONFIG_KEY_0'],'http.https://github.com/.extraheader')


class CategoryAndContactTests(unittest.TestCase):
    def test_four_categories_need_reviewed_provenance_no_field_inference(self):
        for category in schema.CATEGORIES:
            project={'research_type':category,'reanalysis':False}
            self.assertEqual(o.archive_category(project),'Unresolved')
            project['research_type_provenance']={'editor':'Synthetic reviewer',
                'approval_reference':'https://example.org/approval','source_references':['https://example.org/primary']}
            self.assertEqual(o.archive_category(project),category)
        self.assertEqual(o.archive_category({'reanalysis':True}),'Reanalysis')
        audit=o.archive_audit(CONFIG)
        self.assertEqual(audit['field_reanalysis'],{'Field discovery':0,'Reanalysis':1,'Mixed':0,'Unresolved':32})

    def test_no_invented_contact_and_reviewed_mailto_only_crossref(self):
        config=o.crossref_contact()
        self.assertIsNone(config['institutional_contact_email'])
        with patch.object(Path,'read_text',return_value=json.dumps({**config,'institutional_contact_email':'malicious\n@example.org','approval_reference':'synthetic'})):
            with self.assertRaises(ValueError):o.crossref_contact()
        requests=[]
        def opener(request,timeout):
            requests.append(request)
            return io.BytesIO(b'{}')
        o.transport('https://api.crossref.org/works?rows=1',opener=opener)
        self.assertNotIn('mailto',requests[-1].full_url)
        # Explicit test-only domain; never configured in production.
        with patch.object(o,'crossref_contact',return_value={**config,'institutional_contact_email':'test@example.org','approval_reference':'synthetic'}):
            o.transport('https://api.crossref.org/works?rows=1',opener=opener)
            self.assertIn('mailto=test%40example.org',requests[-1].full_url)
            self.assertIn('mailto:test@example.org',requests[-1].get_header('User-agent'))
            o.transport('https://api.openalex.org/works',opener=opener)
            self.assertNotIn('mailto',requests[-1].full_url)


class DocumentationAndPackageTests(unittest.TestCase):
    def test_default_branch_prerequisite_and_activation_limits_documented(self):
        guide=(m.ROOT/'PHASE2B.md').read_text()
        results=(m.ROOT/'PHASE2B_RESULTS.md').read_text()
        self.assertNotIn('may require a workflow file', guide + results)
        self.assertIn('GitHub requires the workflow file to exist on the default branch',guide)
        self.assertIn('it cannot make a PR-only workflow dispatchable',guide)
        self.assertIn('repository-scoped, **not ref-scoped**',guide)
        self.assertIn('No variables, credentials or protections were activated',guide)
        self.assertIn('institutional_contact_email', (m.ROOT/'contact.json').read_text())

    def test_review_package_contains_only_committed_snapshot_and_patches(self):
        import package_review as pack
        import zipfile
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            target=Path(tmp)/'review.zip'
            snapshot=io.BytesIO()
            with zipfile.ZipFile(snapshot,'w') as source:
                source.writestr('monitoring/example.py','committed test control')
            def git(*args):
                if args[0]=='rev-parse': return b'a'*40 + b'\n'
                if args[0]=='archive': return snapshot.getvalue()
                if args[0]=='diff': return b'diff test control'
                raise AssertionError(args)
            with patch.object(pack,'git',side_effect=git):
                pack.package(target)
            with zipfile.ZipFile(target) as archive:
                self.assertEqual(set(archive.namelist()),{'source/monitoring/example.py','manifest.json','round2.diff','complete-pr.diff'})
                manifest=json.loads(archive.read('manifest.json'))
                self.assertEqual(manifest['head'],'a'*40)
                self.assertEqual(set(manifest['source_sha256']),{'monitoring/example.py'})


class WorkflowRevisionTests(unittest.TestCase):
    def test_actions_pinned_and_no_production_schedule_or_publication_activation(self):
        for name in ['monitoring-phase2b.yml','monitoring-tests.yml','monitoring-dry-run.yml','editorial-qa.yml']:
            workflow=(o.REPO/'.github/workflows'/name).read_text()
            for action in re.findall(r'uses:\s*([^\s]+)',workflow):
                self.assertRegex(action,r'@[a-f0-9]{40}$')
        workflow=(o.REPO/'.github/workflows/monitoring-phase2b.yml').read_text()
        self.assertIn("if: github.event_name == 'workflow_dispatch'\n",workflow)
        self.assertNotIn("vars.MONITORING_SCHEDULES_ENABLED == 'true'",workflow)
        self.assertFalse(json.loads((m.ROOT/'publication-policy.json').read_text())['enabled'])
        self.assertIn('  persist:\n    # No hosted contents-write token until protections and credentials are independently reviewed.\n    if: false',workflow)

    def test_failure_alert_independent_of_artifacts_and_persist_success(self):
        workflow=(o.REPO/'.github/workflows/monitoring-phase2b.yml').read_text()
        alert=workflow.split('  operational-failure-alert:\n')[1]
        self.assertIn('if: always() &&',alert)
        for stage in ['collect','persist','editorial-queue']:
            for result in ['failure','cancelled']:
                self.assertIn(f"needs.{stage}.result == '{result}'",alert)
        self.assertNotIn('download-artifact',alert)
        self.assertNotIn('checkout@',alert)
        self.assertNotIn('contents: write',alert)
        self.assertIn('issues: write',alert)
        # Execute the exact inline workflow Python with no reports/state/files and a
        # mocked gh process, for collection failure AND persistence failure.
        script=alert.split("          python - <<'PY'\n",1)[1].rsplit('          PY',1)[0]
        script='\n'.join(line[10:] if line.startswith('          ') else line for line in script.splitlines())
        for collect,persist in [('failure','skipped'),('success','failure')]:
            with tempfile.TemporaryDirectory() as tmp:
                environment={'COLLECT_RESULT':collect,'PERSIST_RESULT':persist,'QUEUE_RESULT':'skipped',
                             'GITHUB_REPOSITORY':'UBC-ARCHAEOLOGY/archaeology_discoveries','GITHUB_RUN_ID':'0',
                             'GITHUB_STEP_SUMMARY':str(Path(tmp)/'summary.md')}
                fake=Mock(side_effect=['[]','created'])
                with patch.dict('os.environ',environment),patch.object(subprocess,'check_output',fake):
                    exec(compile(script,'workflow-alert','exec'),{})
                self.assertEqual(fake.call_count,2)
                self.assertEqual(fake.call_args_list[-1].args[0][1:3],['issue','create'])
                self.assertIn('Operational failure',Path(environment['GITHUB_STEP_SUMMARY']).read_text())


if __name__=='__main__':
    unittest.main()
