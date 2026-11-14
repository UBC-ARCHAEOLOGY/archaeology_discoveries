"""Safety controls for manually dispatched, artifact-only hosted smoke tests."""
import json
from pathlib import Path
import unittest
import operations as o


class ReadOnlySmokeTests(unittest.TestCase):
    def setUp(self):
        self.workflow=(o.REPO/'.github/workflows/monitoring-phase2b.yml').read_text()

    def test_smoke_defaults_on_and_suppresses_failure_issue_automation(self):
        setting=self.workflow.split('      read_only_smoke:\n',1)[1].split('      full:',1)[0]
        self.assertIn('type: boolean',setting)
        self.assertIn('default: true',setting)
        alert=self.workflow.split('  operational-failure-alert:\n',1)[1]
        self.assertIn('if: always() && inputs.read_only_smoke != true && (',alert)
        # Evaluate the actual workflow expression against controlled dependency
        # outcomes, rather than duplicating its condition in test implementation.
        import itertools
        condition=alert.split('    if: ',1)[1].splitlines()[0]
        outcomes=('success','failure','cancelled','skipped')
        for smoke in (False,True):
            for results in itertools.product(outcomes,repeat=3):
                expression=condition.replace('always()','True').replace('inputs.read_only_smoke',repr(smoke))
                for job,result in zip(('collect','persist','editorial-queue'),results):
                    expression=expression.replace('needs.'+job+'.result',repr(result))
                expression=expression.replace('&&',' and ').replace('||',' or ').replace('true','True')
                actual=eval(expression,{'__builtins__':{}},{})
                if smoke:self.assertFalse(actual,results)
                elif 'failure' in results or 'cancelled' in results:self.assertTrue(actual,results)

    def test_other_production_controls_remain_disabled(self):
        self.assertIn("if: github.event_name == 'workflow_dispatch'\n",self.workflow)
        for job,next_job in [('persist','editorial-queue'),('editorial-queue','operational-failure-alert')]:
            section=self.workflow.split('  '+job+':\n',1)[1].split('  '+next_job+':\n',1)[0]
            self.assertIn('    if: false\n',section)
        collect=self.workflow.split('  collect:\n',1)[1].split('  persist:\n',1)[0]
        self.assertIn('      contents: read',collect)
        self.assertNotIn('contents: write',collect)
        self.assertNotIn('issues: write',collect)
        self.assertNotIn('pages: write',self.workflow)
        policy=json.loads((o.m.ROOT/'publication-policy.json').read_text())
        self.assertFalse(policy['enabled'])
        self.assertEqual(policy['approved_dossiers'],{})

    def test_reports_are_attempted_even_when_collection_fails(self):
        collect=self.workflow.split('  collect:\n',1)[1].split('  persist:\n',1)[0]
        self.assertEqual(collect.count('        if: always()'),2)
        self.assertIn('name: phase2b-safe-state',collect)
        self.assertIn('name: phase2b-safe-reports',collect)
        self.assertNotIn('replay.json',collect)


if __name__=='__main__':unittest.main()
