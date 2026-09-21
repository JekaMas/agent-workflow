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
        for op,name in b.operation_names(self.profile).items():
            self.assertIn(name,(self.root/f'.claude/commands/opsx/{op}.md').read_text())

    def test_specialists_resolve_from_both_clients_in_fresh_clone(self):
        self.adopt()
        self.git(self.root,'add','.')
        self.git(self.root,'commit','-qm','adopt')
        clone=self.base/'fresh'
        self.git(self.base,'clone','-q',str(self.root),str(clone))
        self.git(clone,'-c','protocol.file.allow=always','submodule','update','--init')
        for name,(description,language) in b.SPECIALIST_SKILLS.items():
            if language == 'rust':
                self.assertFalse((clone/f'.agents/skills/{name}').exists());continue
            route=clone/f'.agents/skills/{name}/SKILL.md'
            target=f'.agents/workflow/skills/{name}/SKILL.md'
            self.assertIn(target,route.read_text())
            self.assertTrue((clone/target).is_file())
            self.assertIn(str(route.relative_to(clone)),(clone/f'.claude/commands/{name}.md').read_text())
        self.assertTrue((clone/'.agents/workflow/skills/golang-optimization/../golang-performance-diagnostics/references/cpu-cache-analysis.md').is_file())
        from check_opsx_routes import inspect
        self.assertEqual([],inspect(clone)['errors'])
        config=clone/'openspec/config.yaml'
        config.write_text(config.read_text().replace('Never mark a required','Always mark a required'))
        self.assertIn('shared integration drift: openspec/config.yaml',inspect(clone)['errors'])

    def test_language_selection_and_removal_boundary(self):
        self.profile['languages']=['rust','python'];self.adopt()
        self.assertTrue((self.root/'.agents/skills/event-sequence-pbt/SKILL.md').is_file())
        self.assertTrue((self.root/'.agents/skills/sdd-rust/SKILL.md').is_file())
        self.assertFalse((self.root/'.agents/skills/golang-testing').exists())
        self.profile['languages']=[]
        with self.assertRaisesRegex(ValueError,'removing managed routes'):self.adopt()
        self.assertTrue((self.root/'.agents/skills/sdd-rust/SKILL.md').is_file())

    def test_specialist_collision_does_not_overwrite(self):
        p=self.root/'.agents/skills/event-sequence-pbt/SKILL.md'
        p.parent.mkdir(parents=True);p.write_text('project oracle contract')
        with self.assertRaisesRegex(ValueError,'unmanaged'):self.adopt()
        self.assertEqual('project oracle contract',p.read_text())
        self.assertFalse((self.root/'.agents/workflow').exists())

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

class ExistingAdoptionTests(unittest.TestCase):
    setUp = BootstrapTests.setUp
    git = BootstrapTests.git
    def test_detects_real_modules_without_build_vendor_or_links(self):
        for name in ['go.mod', 'crates/tool/Cargo.toml', 'vendor/ignore/go.mod', 'target/Cargo.toml']:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('fixture')
        (self.root/'link').symlink_to(self.source, target_is_directory=True)
        result=b.discover_profile(self.root)
        self.assertEqual(['go','rust'], result['languages'])
        self.assertEqual({'go':['.'],'rust':['crates/tool']}, result['module_roots'])

    def test_reviewed_existing_setup_preserves_active_artifacts(self):
        config=self.root/'openspec/config.yaml';config.parent.mkdir();config.write_text('schema: spec-driven\ncontext: Existing domain rules live in AGENTS.md\n')
        task=self.root/'openspec/changes/active/tasks.md';task.parent.mkdir(parents=True);task.write_text('- [ ] Preserve active work\n')
        plan=b.prepare_migration(self.root,self.profile,self.rev,str(self.source))
        before=task.read_bytes()
        b.repo_apply(self.root,self.profile,self.source,self.rev,str(self.source),True,plan)
        self.assertEqual(before,task.read_bytes())
        self.assertTrue((self.root/'AGENTS.md').read_text().startswith('Keep domain constraints.'))
        b.status(self.root)

    def test_stale_migration_refuses_before_any_setup(self):
        plan=b.prepare_migration(self.root,self.profile,self.rev,str(self.source))
        (self.root/'AGENTS.md').write_text('New domain contract\n')
        with self.assertRaisesRegex(ValueError,'stale'):
            b.repo_apply(self.root,self.profile,self.source,self.rev,str(self.source),True,plan)
        self.assertFalse((self.root/'.agents/workflow').exists())
        self.assertEqual('New domain contract\n',(self.root/'AGENTS.md').read_text())

    def test_changed_profile_and_revision_reject_plan(self):
        plan=b.prepare_migration(self.root,self.profile,self.rev,str(self.source))
        for profile,revision in [({**self.profile,'languages':['rust']},self.rev),(self.profile,'another-revision')]:
            with self.assertRaisesRegex(ValueError,'stale'):
                b.check_migration(self.root,profile,revision,str(self.source),plan)

    def test_custom_schema_is_not_replaced(self):
        config=self.root/'openspec/config.yaml';config.parent.mkdir();config.write_text('schema: custom-schema\n')
        with self.assertRaisesRegex(ValueError,'dedicated migration'):
            b.prepare_migration(self.root,self.profile,self.rev,str(self.source))
        self.assertFalse((self.root/'.agents').exists())

    def test_reviewed_alias_cannot_overwrite_another_owner(self):
        owner=self.root/'owned';owner.mkdir();target=owner/'SKILL.md';target.write_text('Preserve owner')
        alias=self.root/'.agents/skills/openspec-explore';alias.parent.mkdir(parents=True);alias.symlink_to(owner, target_is_directory=True)
        plan=b.prepare_migration(self.root,self.profile,self.rev,str(self.source))
        with self.assertRaisesRegex(ValueError,'output alias'):
            b.repo_apply(self.root,self.profile,self.source,self.rev,str(self.source),True,plan)
        self.assertEqual('Preserve owner',target.read_text())
        self.assertFalse((self.root/'.agents/workflow').exists())

    def test_empty_new_git_repository(self):
        root=self.base/'empty';root.mkdir();self.git(root,'init','-q')
        profile=b.discover_profile(root)
        b.repo_apply(root,profile,self.source,self.rev,str(self.source),True)
        b.status(root)

    def test_cli_prepare_outputs_inspectable_files_without_target_edits(self):
        config=self.root/'openspec/config.yaml';config.parent.mkdir();config.write_text('schema: spec-driven\n')
        before=self.git(self.root,'status','--porcelain')
        plan=self.base/'review.json';preview=self.base/'proposed'
        result=subprocess.run(['python3','-B',str(b.SOURCE/'scripts/bootstrap.py'),'prepare','--repo',str(self.root),'--source',str(self.source),'--source-url',str(self.source),'--plan-out',str(plan),'--preview-dir',str(preview)],capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual(before,self.git(self.root,'status','--porcelain'))
        self.assertTrue((preview/'openspec/config.yaml').is_file())
        self.assertIn('before',json.loads(plan.read_text()))

if __name__=='__main__': unittest.main()
