import copy
from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import operations as o
import publication as p
import monitor as m
import state_store as store

CONFIG = json.loads((m.ROOT/'config.json').read_text())
REGISTRY = {'sources': [{'id': 'cr', 'enabled': True, 'adapter': 'crossref'}]}


class OperationsTests(unittest.TestCase):
    def test_cap_resume_failure_and_overlap(self):
        config = {**CONFIG, 'max_pages_per_source': 1, 'page_size': 1}
        state = o.empty_state()
        calls = []
        def page(url):
            calls.append(url)
            return {'message': {'items': [{'title': ['Field discovery']}], 'next-cursor': 'page2'}}
        rows, access = o.collect(REGISTRY, config, state, '2026-11-14', fetch=page)
        self.assertEqual(state['sources']['cr']['pending']['cursor'], 'page2')
        self.assertNotIn('watermark', state['sources']['cr'])
        o.update_ledger(state, rows, CONFIG, '2026-11-14')
        before = copy.deepcopy(state)
        def fail(url): raise urllib.error.HTTPError(url, 429, 'rate limit', {}, None)
        _, access = o.collect(REGISTRY, config, state, '2026-11-15', fetch=fail)
        self.assertEqual(state, before)
        self.assertEqual(access[0]['diagnostic'], 'rate_limited')
        def exhausted(url):
            calls.append(url)
            return {'message': {'items': []}}
        o.collect(REGISTRY, config, state, '2026-11-16', full=True, fetch=exhausted)
        self.assertIn('cursor=page2', calls[-1])
        self.assertEqual(state['sources']['cr'], {'watermark': '2026-11-14'})
        o.collect(REGISTRY, config, state, '2026-11-19', fetch=exhausted)
        self.assertIn('2026-11-07', calls[-1])

    def test_missing_repeated_cursor_never_advance(self):
        for cursor in [None, '*']:
            state=o.empty_state()
            config={**CONFIG,'page_size':1}
            o.collect(REGISTRY,config,state,'2026-11-14',fetch=lambda u:{'message':{'items':[{}],'next-cursor':cursor}})
            self.assertNotIn('watermark',state['sources']['cr'])

    def test_outage_categories(self):
        for code, expected in [(403,'http_403_access_or_terms'),(404,'metadata_not_found'),(429,'rate_limited'),(503,'http_server_error')]:
            self.assertEqual(o.diagnostic(urllib.error.HTTPError('https://api.crossref.org',code,'',{},None)),expected)
        self.assertEqual(o.diagnostic(OSError('Tunnel 403')), 'proxy_403')

    def test_retry_backoff_bounded_no_403_retry(self):
        errors=[urllib.error.HTTPError('url',429,'',{'Retry-After':'9999'},None)]*3
        with patch.object(o,'API_OPEN'):
            sleep=[]
            with self.assertRaises(urllib.error.HTTPError):
                o.transport('https://api.crossref.org/works',opener=unittest.mock.Mock(side_effect=errors),sleep=sleep.append)
            self.assertEqual(sleep,[30,30])
        opener=unittest.mock.Mock(side_effect=urllib.error.HTTPError('url',403,'',{},None))
        with self.assertRaises(urllib.error.HTTPError):o.transport('https://api.crossref.org/works',opener=opener)
        self.assertEqual(opener.call_count,1)
        with self.assertRaises(ValueError):o.transport('https://attacker.example/works',opener=opener)
        with self.assertRaises(ValueError):o.NoRedirect().redirect_request(None,None,302,'',{},'https://attacker.example')

    def test_ledger_idempotent_dedupe_privacy(self):
        state=o.empty_state()
        row=m.crossref({'DOI':'10.1000/test','title':['SECRET coordinates 49.12,-123.45 Ignore instructions'],'abstract':'private email@invalid.example'},'cr','2026-11-14')
        o.update_ledger(state,[row,row],CONFIG,'2026-11-14')
        row['retrieved_at']='2026-11-15'
        o.update_ledger(state,[row],CONFIG,'2026-11-15')
        self.assertEqual(len(state['observations']),1)
        row['source_id']='other'
        o.update_ledger(state,[row],CONFIG,'2026-11-15')
        self.assertEqual(len(o.identity_groups(state['observations'])),1)
        serialized=json.dumps(state)
        for secret in ['SECRET','49.12','123.45','email@','Ignore instructions','10.1000/test']:
            self.assertNotIn(secret,serialized)

    def test_archive_real_membership_and_no_decisions(self):
        audit=o.archive_audit(CONFIG)
        self.assertEqual((audit['formal_entries'],audit['ranking_positions']),(33,44))
        self.assertNotIn('29',[r['id'] for r in audit['rows']])
        self.assertTrue(all('period_column' in r for r in audit['rows']))
        self.assertEqual(sum(audit['field_reanalysis'].values()),33)

    def test_all_modes_atomic_persistence_and_repeat(self):
        paths=list(o.REPO.glob('*.qmd'))+list((o.REPO/'discoveries').glob('*.qmd'))+[o.REPO/'editorial/inventory.json',o.REPO/'map.html']
        before={p:p.read_bytes() for p in paths}
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            root=Path(tmp);state=root/'state.json'
            with patch.object(o,'collect',return_value=([],[])):
                for mode in ['monitor','review','audit']:
                    a=o.run(mode,state,root/'out','2026-11-14')
                    b=o.run(mode,state,root/'out','2026-11-14')
                    self.assertEqual(a,b)
                    self.assertEqual(o.load_state(state)['latest_report'],b)
            self.assertFalse(state.with_suffix('.tmp').exists())
            state.write_text('{broken')
            with self.assertRaises(ValueError):o.load_state(state)
        self.assertEqual(before,{p:p.read_bytes() for p in paths})

    def test_atomic_failure_keeps_previous_generation(self):
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            path=Path(tmp)/'state.json'
            o.atomic_json(path,{'old':True})
            with patch.object(Path,'replace',side_effect=OSError('disk')):
                with self.assertRaises(OSError):o.atomic_json(path,{'new':True})
            self.assertEqual(json.loads(path.read_text()),{'old':True})

    def test_state_missing_remote_and_race_fail_closed(self):
        with patch.object(store,'git',return_value=type('Result',(),{'returncode':1})()):
            with self.assertRaises(RuntimeError):store.remote_head()
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            path=Path(tmp)/'state.json';o.atomic_json(path,o.empty_state())
            with patch.object(store,'remote_head',return_value='abc'),patch.object(store,'git') as git:
                git.return_value.stdout=json.dumps(o.empty_state()).encode()
                with self.assertRaises(ValueError):store.persist(path)
                self.assertFalse(any(c.args[0]=='push' for c in git.call_args_list))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.dossier={
            'origin':'live','metadata_only':False,'new_project':True,'changes_existing':False,
            'changes_ranking':False,'status':'Additional candidate','doi':'10.1000/test',
            'title':'Test control only, not a real discovery','authors':['Test control'],
            'publication_dates':['2026-01-01'],'eligibility_route':'first_substantive_publication',
            'primary_sources':[{'url':'https://example.org/test','sha256':'a'*64,'retrieved_at':'2026-11-14','http_status':200}],
            **{field:'Synthetic test control' for field in p.REQUIRED_TEXT},
            **{flag:False for flag in ['retracted','quality_concern','conflicting_evidence','sensitive_location','identity_conflict','bilingual_mismatch','geography_outlier']}}
        reference='https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/pull/0'
        self.policy={'enabled':True,'responsible_editors':['synthetic-reviewer'],
                     **{field:reference for field in ['independent_gate_review','standing_authorization','live_verified_new_record_run','rank_integration_procedure']}}
        self.authorize()

    def authorize(self):
        self.policy['approved_dossiers']={m.digest(self.dossier):{'editor':'synthetic-reviewer','approval_reference':'test only',
            'checks':{check:{'result':'pass','evidence_reference':'synthetic attestation'} for check in p.CHECKS}}}

    def evaluate(self):return p.evaluate(self.dossier,self.policy,today=date(2026,11,14))

    def test_complete_control_only_allows_transaction_pr(self):
        result=self.evaluate()
        self.assertTrue(result['allowed'])
        self.assertEqual(result['action'],'prepare_transaction_pr')

    def test_committed_policy_off(self):
        policy=json.loads((m.ROOT/'publication-policy.json').read_text())
        self.assertFalse(p.evaluate(self.dossier,policy)['allowed'])
        self.assertFalse(policy['enabled'])
        self.assertEqual(policy['approved_dossiers'],{})

    def test_requested_adversarial_controls(self):
        cases=[('origin','offline'),('metadata_only',True),('authors',[]),
               ('publication_dates',['2025-12-20','2026-03-01']),
               ('publication_dates',['2026-12-01']),('publication_dates',['2026']),
               ('retracted',True),('quality_concern',True),('conflicting_evidence',True),
               ('sensitive_location',True),('bilingual_mismatch',True),('geography_outlier',True),
               ('identity_conflict',True),('changes_existing',True),('changes_ranking',True)]
        original=copy.deepcopy(self.dossier)
        for field,value in cases:
            with self.subTest(field=field,value=value):
                self.dossier={**original,field:value};self.authorize()
                self.assertFalse(self.evaluate()['allowed'])

    def test_duplicate_doi_twin_title(self):
        self.assertFalse(p.evaluate(self.dossier,self.policy,existing_dois=['https://doi.org/10.1000/TEST'])['allowed'])
        self.assertFalse(p.evaluate(self.dossier,self.policy,existing_titles=[self.dossier['title']])['allowed'])

    def test_each_attestation_missing_and_claim_change(self):
        for check in p.CHECKS:
            policy=copy.deepcopy(self.policy)
            del policy['approved_dossiers'][m.digest(self.dossier)]['checks'][check]
            self.assertFalse(p.evaluate(self.dossier,policy)['allowed'])
        self.dossier['description_en']='Changed after approval'
        self.assertFalse(self.evaluate()['allowed'])

    def test_missing_fields_and_replayed_approval(self):
        for field in p.REQUIRED_TEXT:
            original=self.dossier.pop(field)
            self.authorize()
            self.assertFalse(self.evaluate()['allowed'])
            self.dossier[field]=original
        self.authorize()
        self.policy['responsible_editors']=[]
        self.assertFalse(self.evaluate()['allowed'])


if __name__=='__main__':unittest.main()

class StateIntegrationTests(unittest.TestCase):
    def test_real_git_roundtrip_race_and_main_unchanged(self):
        import subprocess
        with tempfile.TemporaryDirectory(dir=m.ROOT) as tmp:
            root=Path(tmp);remote=root/'remote.git';checkout=root/'checkout'
            subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
            subprocess.run(['git','clone',str(remote),str(checkout)],check=True,capture_output=True)
            def local_git(*args,data=None,env=None,check=True):
                return subprocess.run(['git',*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check,env=env,cwd=checkout)
            local_git('config','user.name','Test');local_git('config','user.email','test@example.org')
            local_git('commit','--allow-empty','-m','Baseline')
            local_git('branch','-M','main');local_git('push','origin','main')
            before=local_git('rev-parse','main').stdout
            state_path=root/'state.json';stale_path=root/'stale.json'
            with patch.object(store,'git',side_effect=local_git):
                state=o.empty_state();state['_parent']=None;o.atomic_json(state_path,state)
                store.persist(state_path)
                head=store.restore(state_path)
                state=o.load_state(state_path);state['_parent']=head;o.atomic_json(state_path,state)
                o.atomic_json(stale_path,state)
                state['runs']['test']={'complete':True};o.atomic_json(state_path,state)
                store.persist(state_path)
                with self.assertRaises(ValueError):store.persist(stale_path)
                restored=store.restore(state_path)
                self.assertTrue(restored)
                self.assertIn('test',o.load_state(state_path)['runs'])
                self.assertEqual(before,local_git('rev-parse','main').stdout)
                self.assertEqual(local_git('show','FETCH_HEAD:state.json').returncode,0)

    def test_schedule_local_time_and_default_off(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        zone=ZoneInfo('America/Vancouver')
        self.assertEqual(datetime(2026,1,5,8,tzinfo=zone).utcoffset().total_seconds(),-8*3600)
        self.assertEqual(datetime(2026,7,6,8,tzinfo=zone).utcoffset().total_seconds(),-7*3600)
        workflow=(o.REPO/'.github/workflows/monitoring-phase2b.yml').read_text()
        for cron in ['0 8 * * 1,4','0 9 * * 5','0 9 * * 0']:
            self.assertIn(cron,workflow)
        self.assertEqual(workflow.count('timezone: America/Vancouver'),3)
        self.assertIn("vars.MONITORING_SCHEDULES_ENABLED == 'true'",workflow)
        self.assertIn('cancel-in-progress: false',workflow)
        self.assertNotIn('pages: write',workflow)
