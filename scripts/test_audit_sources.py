import tempfile
import subprocess
from pathlib import Path
import unittest
from audit_sources import audit

class SourceAudit(unittest.TestCase):
    def test_tracked_link_and_untracked_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'repo';repo.mkdir()
            subprocess.run(['git','init','-q',str(repo)],check=True)
            source=repo/'SKILL.md';source.write_text('tracked')
            subprocess.run(['git','-C',str(repo),'add','SKILL.md'],check=True)
            alias=root/'alias';alias.symlink_to(source)
            self.assertEqual('passed',audit([alias])['status'])
            (repo/'other.md').write_text('untracked')
            self.assertEqual('failed',audit([repo])['status'])
            (repo/'.gitignore').write_text('SKILL.md\n')
            self.assertTrue(any('ignored source' in e for e in audit([alias])['errors']))
    def test_empty_inventory_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual('failed', audit([Path(tmp)])['status'])

    def test_export_copy_is_not_git_backed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'SKILL.md';p.write_text('copy')
            self.assertTrue(any('outside Git' in e for e in audit([p])['errors']))

if __name__=='__main__': unittest.main()
