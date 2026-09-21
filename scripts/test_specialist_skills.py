"""Check portable specialist packages and their local reference graph."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
UI_NAMES=('event-sequence-pbt','golang-testing','golang-performance-diagnostics','golang-optimization')
NAMES=UI_NAMES+('verification-design','sdd-go','sdd-rust')

class SpecialistPackages(unittest.TestCase):
    def test_reference_graph_and_identity(self):
        for name in NAMES:
            root=ROOT/'skills'/name
            body=(root/'SKILL.md').read_text()
            self.assertIn('name: '+name+'\n',body)
            if name in UI_NAMES:
                self.assertIn('$'+name,(root/'agents/openai.yaml').read_text())
            for ref in (root/'references').glob('*.md'):
                self.assertIn('references/'+ref.name,body, str(ref))
            for file in root.rglob('*.md'):
                prose=re.sub(r'```.*?```', '', file.read_text(), flags=re.S)
                for link in re.findall(r'\]\(([^)]+)\)',prose):
                    if '://' in link or link.startswith('#'):continue
                    target=(file.parent/link.split('#')[0]).resolve()
                    self.assertTrue(target.is_file(),f'{file}: {link}')
                    self.assertTrue(target.is_relative_to(ROOT/'skills'),str(target))

    def test_declared_references_exist(self):
        for name in NAMES:
            root=ROOT/'skills'/name
            for relative in re.findall(r'`(references/[^`]+\.md)`', (root/'SKILL.md').read_text()):
                self.assertTrue((root/relative).is_file(), f'{name}: {relative}')

    def test_missing_declared_reference_is_rejected(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            package=root/'skills/verification-design'
            package.mkdir(parents=True)
            (package/'SKILL.md').write_text('Use `references/missing.md`.')
            with patch.dict(globals(), ROOT=root, NAMES=('verification-design',)):
                with self.assertRaisesRegex(AssertionError, 'missing.md'):
                    self.test_declared_references_exist()

    def test_shared_native_config_uses_local_sources(self):
        import json
        from integration import render_config
        profile=json.loads((ROOT/'openspec/workflow-profile.json').read_text())
        self.assertEqual(render_config(profile), (ROOT/'openspec/config.yaml').read_text())
        for relative in profile['integration'].values():
            self.assertTrue((ROOT/relative).is_file(), relative)

if __name__=='__main__':unittest.main()
