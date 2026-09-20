"""Check portable specialist packages and their local reference graph."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
NAMES=('event-sequence-pbt','golang-testing','golang-performance-diagnostics','golang-optimization')

class SpecialistPackages(unittest.TestCase):
    def test_reference_graph_and_identity(self):
        for name in NAMES:
            root=ROOT/'skills'/name
            body=(root/'SKILL.md').read_text()
            self.assertIn('name: '+name+'\n',body)
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

if __name__=='__main__':unittest.main()
