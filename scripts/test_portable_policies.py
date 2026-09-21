"""Shared validator policy and failed selection checks in disposable roots."""
import tempfile
import unittest
from pathlib import Path
import skill_packages as skills
from workflow_publication import inspect

class PolicyTests(unittest.TestCase):
    def test_nested_references_are_consumer_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package=root/'skill';ref=package/'references/nested/topic.md'
            ref.parent.mkdir(parents=True);ref.write_text('Evidence')
            body='Read references/nested/topic.md'
            skills.configure(root)
            self.assertEqual([],skills.validate_skill_references(package,body))
            skills.configure(root,{'flat_references':True,'direct_references':True})
            self.assertTrue(any('nested reference' in error for error in skills.validate_skill_references(package,body)))
            ref.unlink()
            self.assertTrue(any('unresolved routed reference' in error for error in skills.validate_skill_references(package,body)))

    def test_outside_policy_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'outside'):
                inspect(Path(directory),{'roots':['../another-repo']})
            with self.assertRaisesRegex(ValueError,'outside'):
                skills.configure(Path(directory),{'skills_path':'../another-repo'})

if __name__=='__main__':unittest.main()
