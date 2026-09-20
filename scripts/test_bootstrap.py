"""Real disposable Git/filesystem qualification; no live repos or global settings."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('bootstrap',Path(__file__).with_name('bootstrap.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class BootstrapTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.base=Path(temp.name);self.root=self.base/'consumer';self.source=self.base/'source';self.home=self.base/'home'
        for path in [self.root,self.source]:
            path.mkdir();self.git(path,'init','-q');self.git(path,'config','user.name','Fixture');self.git(path,'config','user.email','fixture@example.invalid')
        (self.root/'AGENTS.md').write_text('Keep domain constraints.\n')
        self.git(self.root,'add','.');self.git(self.root,'commit','-qm','domain')
        for folder in ['defaults','skills','docs','scripts']:
            shutil.copytree(b.SOURCE/folder,self.source/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        self.git(self.source,'add','.');self.git(self.source,'commit','-qm','source')
        self.rev=self.git(self.source,'rev-parse','HEAD');self.profile={'schema':1,'languages':['go'],'notes':'native commands only'}

    def git(self,root,*args):
        return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()

    def adopt(self,apply=True):
        b.repo_apply(self.root,self.profile,self.source,self.rev,str(self.source),apply)

    def install(self,apply=True):
        b.personal(self.source,self.rev,self.home,None,apply,True)

    def test_preview_does_not_write(self):
        before=self.git(self.root,'status','--porcelain');self.adopt(False);self.install(False)
        self.assertEqual(before,self.git(self.root,'status','--porcelain'))
        self.assertFalse((self.root/'.agents').exists());self.assertFalse(self.home.exists())

    def test_unmanaged_collision_preserves_everything(self):
        p=self.root/'.agents/skills/openspec-apply-change/SKILL.md';p.parent.mkdir(parents=True);p.write_text('custom owner')
        with self.assertRaisesRegex(ValueError,'unmanaged'): self.adopt()
        self.assertEqual('custom owner',p.read_text());self.assertFalse((self.root/'.agents/workflow').exists())

    def test_ignored_workflow_route_rejected_before_writes(self):
        (self.root/'.gitignore').write_text('.claude/\n')
        with self.assertRaisesRegex(ValueError,'workflow files are ignored'): self.adopt()
        self.assertFalse((self.root/'.agents/workflow').exists())

    def test_existing_openspec_not_overwritten(self):
        (self.root/'openspec').mkdir()
        with self.assertRaisesRegex(ValueError,'existing OpenSpec'): self.adopt()

    def test_adoption_and_repeat_preserve_domain_and_exact_pin(self):
        self.adopt();self.adopt();b.status(self.root)
        text=(self.root/'AGENTS.md').read_text()
        self.assertTrue(text.startswith('Keep domain constraints.'))
        self.assertEqual(1,text.count(b.BEGIN));self.assertEqual(self.rev,self.git(self.root,'rev-parse',':.agents/workflow'))
        for op,(name,_) in b.OPERATIONS.items():
            self.assertIn(name,(self.root/f'.claude/commands/opsx/{op}.md').read_text())

    def test_user_edits_outside_block_survive_update(self):
        self.adopt();p=self.root/'AGENTS.md';p.write_text('New rule.\n'+p.read_text());self.adopt()
        self.assertTrue(p.read_text().startswith('New rule.'))

    def test_modified_owned_file_blocks_update(self):
        self.adopt();p=self.root/'docs/SDD_WORKFLOW.md';p.write_text('local change')
        with self.assertRaisesRegex(ValueError,'modified file'): self.adopt()
        self.assertEqual('local change',p.read_text())

    def test_modified_block_blocks_update(self):
        self.adopt();p=self.root/'AGENTS.md';p.write_text(p.read_text().replace('Existing project','Changed project'))
        with self.assertRaisesRegex(ValueError,'modified instruction block'): self.adopt()

    def test_external_target_symlink_rejected(self):
        external=self.base/'outside';external.mkdir();(self.root/'.agents').symlink_to(external)
        with self.assertRaisesRegex(ValueError,'outside target root'): self.adopt()
        self.assertEqual([],list(external.iterdir()))

    def test_personal_backups_and_repeat(self):
        p=self.home/'.codex/AGENTS.md';p.parent.mkdir(parents=True);p.write_text('old defaults')
        self.install();state=json.loads((self.home/'.local/share/agent-workflow/personal-install.json').read_text())
        history=json.loads((Path(state['backup'])/'restore.json').read_text())
        self.assertEqual('old defaults',Path(history['files'][str(p)]['backup']).read_text())
        self.install();self.assertTrue(p.is_symlink());self.assertIn('Personal development',p.read_text())
        self.assertFalse((self.home/'.agents/skills/openspec-apply-change').exists())
        release=(self.home/'.local/share/agent-workflow/current').resolve()
        self.assertTrue((release/'.git').is_dir())
        self.assertEqual('defaults/personal.md',self.git(release,'ls-files','--error-unmatch','defaults/personal.md'))
        self.assertEqual('', self.git(release,'status','--porcelain'))

    def test_untracked_active_skill_refuses_reactivation(self):
        self.install()
        release=(self.home/'.local/share/agent-workflow/current').resolve()
        (release/'skills/sdd-workflow/untracked.md').write_text('unexpected instruction')
        with self.assertRaisesRegex(ValueError,'untracked release'): self.install()

    def test_personal_managed_edit_rejected(self):
        self.install();p=self.home/'.codex/AGENTS.md';p.unlink();p.write_text('local override')
        with self.assertRaisesRegex(ValueError,'modified managed'): self.install()

    def test_personal_revision_upgrade(self):
        self.install();p=self.source/'defaults/personal.md';p.write_text(p.read_text()+'\nNew qualified default.\n')
        self.git(self.source,'add','.');self.git(self.source,'commit','-qm','upgrade');self.rev=self.git(self.source,'rev-parse','HEAD')
        self.install();self.assertIn('New qualified default.',(self.home/'.codex/AGENTS.md').read_text())
        self.assertEqual(2,len(list((self.home/'.local/share/agent-workflow/releases').iterdir())))

    def test_adding_workspace_at_same_revision_is_not_skipped(self):
        self.install();workspace=self.base/'workspace';workspace.mkdir()
        (workspace/'AGENTS.md').write_text('old workspace routing')
        b.personal(self.source,self.rev,self.home,workspace,True,True)
        self.assertTrue((workspace/'AGENTS.md').is_symlink())
        self.assertIn('Multi-repository', (workspace/'AGENTS.md').read_text())

    def test_repo_revision_upgrade(self):
        self.adopt();(self.source/'docs/new.md').write_text('new qualified release')
        self.git(self.source,'add','.');self.git(self.source,'commit','-qm','upgrade');self.rev=self.git(self.source,'rev-parse','HEAD')
        self.adopt();b.status(self.root)
        self.assertTrue((self.root/'.agents/workflow/docs/new.md').exists())

if __name__=='__main__': unittest.main()
