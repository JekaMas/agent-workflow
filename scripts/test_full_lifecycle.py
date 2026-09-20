"""Native disposable sync/archive paths; never archives consumer changes."""
import json
import shutil
import subprocess
import unittest
import test_openspec_workflow as fixtures
from test_openspec_workflow import child_environment, CHANGE

PURPOSE='Preserve bounded fixture behavior and explicit rejection cases through synchronized and archived specifications.'

class Lifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.OpenSpecWorkflowIntegrationTest.setUpClass()

    def setUp(self):
        self.fx=fixtures.OpenSpecWorkflowIntegrationTest();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.fx.project()
        self.root=self.fx.root
        self.delta=self.fx.change/'specs/workflow-mechanics/spec.md'
        self.delta.write_text('# Workflow mechanics\n\n## Purpose\n'+PURPOSE+'\n\n'+self.delta.read_text())
        self.main=self.root/'openspec/specs/workflow-mechanics/spec.md'
        self.unrelated=self.root/'openspec/specs/unrelated/spec.md'
        self.unrelated.parent.mkdir(parents=True)
        self.unrelated.write_text('unrelated sentinel: no writes authorized here\n')
        self.unrelated_before=self.unrelated.read_bytes()

    def validate(self,success=True):
        result=subprocess.run([self.fx.tool,'validate','workflow-mechanics','--type','spec','--strict','--json','--no-interactive'],cwd=self.root,env=child_environment(),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0 if success else 1,result.stderr)
        self.assertEqual(json.loads(result.stdout)['items'][0]['valid'],success)
        self.assertEqual(self.unrelated_before,self.unrelated.read_bytes())

    def sync_added(self):
        status=self.fx.native('status','--change',CHANGE,'--json')
        self.assertIn(str(self.delta),status['artifactPaths']['specs']['existingOutputPaths'])
        self.fx.native('instructions','specs','--change',CHANGE,'--json')
        self.main.parent.mkdir(parents=True,exist_ok=True)
        self.main.write_text(self.delta.read_text().replace('## ADDED Requirements','## Requirements'))
        self.validate()

    def archive(self):
        self.fx.native('instructions','archive','--change',CHANGE,'--json')
        result=self.fx.native('archive',CHANGE,'--json','--yes')
        self.assertFalse(self.fx.change.exists())
        self.assertEqual(1,len(list((self.root/'openspec/changes/archive').glob('*'+CHANGE))))
        self.validate()
        return result

    def test_direct_archive_preserves_main_and_unrelated(self):
        self.archive()
        self.assertIn('Report local validation outcome',self.main.read_text())

    def test_sync_then_archive_is_idempotent(self):
        self.sync_added();before=self.main.read_bytes()
        self.archive();self.assertEqual(before,self.main.read_bytes())

    def test_iterate_spec_then_archive_modified_requirement(self):
        self.sync_added()
        old='The fixture SHALL report whether its local validation succeeded.'
        new='The fixture SHALL report both successful and failed local validation outcomes.'
        self.assertIn(old,self.delta.read_text())
        self.delta.write_text(self.delta.read_text().replace('## ADDED Requirements','## MODIFIED Requirements').replace(old,new))
        self.fx.native('instructions','specs','--change',CHANGE,'--json')
        self.fx.native('instructions','apply','--change',CHANGE,'--json')
        self.archive()
        self.assertIn(new,self.main.read_text())
        self.assertNotIn(old,self.main.read_text())

    def test_archive_success_does_not_hide_invalid_main_then_repair(self):
        self.delta.write_text(self.delta.read_text().replace(PURPOSE,'Too brief.'))
        self.fx.native('archive',CHANGE,'--json','--yes')
        self.validate(False)
        self.main.write_text(self.main.read_text().replace('Too brief.',PURPOSE))
        self.validate()

    def test_bulk_selection_preserves_unselected_incomplete_change(self):
        second=self.fx.change.parent/'second-complete'
        pending=self.fx.change.parent/'unselected-pending'
        shutil.copytree(self.fx.change,second);shutil.copytree(self.fx.change,pending)
        tasks=pending/'tasks.md';tasks.write_text(tasks.read_text().replace('[x]','[ ]'))
        self.archive()
        self.fx.native('instructions','archive','--change','second-complete','--json')
        self.fx.native('archive','second-complete','--json','--yes')
        self.assertFalse(second.exists());self.assertTrue(pending.exists())
        self.assertEqual(2,len(list((self.root/'openspec/changes/archive').iterdir())))
        self.validate()

    def test_incomplete_check_blocks_closure_before_archive(self):
        tasks=self.fx.change/'tasks.md';tasks.write_text(tasks.read_text().replace('[x]','[ ]'))
        code,result=self.fx.verify(require_complete=True,require_guidance=True)
        self.assertNotEqual(code,0)
        self.assertEqual(result['status'],'incomplete_tasks')
        self.assertTrue(self.fx.change.exists())
        self.assertFalse((self.root/'openspec/changes/archive').exists())

if __name__=='__main__':unittest.main()
