"""Protocol fixtures, not a model-quality evaluation; no server or inference."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from local_review import run


class LocalReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'source.txt').write_text('A request must release its owned resource on cancellation.\n')
        self.args = argparse.Namespace(root=self.root, output=self.root/'result', mode='implementation',
            claim='cancellation cleans up', input=['source.txt'], model='fixture:local',
            port=11434, context=8192, predict=256, timeout=5)
        self.calls = []

    def transport(self, port, endpoint, payload, timeout):
        self.calls.append(endpoint)
        if endpoint == 'version': return {'version': 'fixture'}
        if endpoint == 'tags': return {'models': [{'name': 'fixture:local', 'digest': 'sha256:fixture'}]}
        if endpoint == 'show': return {'model_info': {'architecture': 'fixture'}, 'details': {'parameter_size': 'fixture'}}
        return {'model': 'fixture:local', 'done': True, 'done_reason': 'stop', 'thinking': 'MUST NOT BE RETAINED',
                'response': json.dumps({'verdict': 'insufficient_evidence', 'reason': 'No cleanup observation',
                                       'evidence': ['source.txt:1'], 'next_action': 'Inspect the release owner'})}

    def check_bad(self, transport):
        code, result = run(self.args, transport)
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'unavailable_or_invalid')
        self.assertTrue((self.args.output/'result.json').is_file())
        return result

    def test_valid_review_is_advice_and_drops_hidden_reasoning(self):
        code, result = run(self.args, self.transport)
        self.assertEqual(code, 0)
        self.assertEqual(result['acceptance'], 'requires_source_inspection')
        self.assertNotIn('MUST NOT BE RETAINED', (self.args.output/'result.json').read_text())
        self.assertEqual(self.calls.count('generate'), 1)

    def test_absent_server_preserves_failure(self):
        def absent(*args): raise ConnectionRefusedError('fixture server absent')
        self.assertIn('ConnectionRefusedError', self.check_bad(absent)['error'])

    def test_cloud_tag_never_contacts_server(self):
        self.args.model = 'fixture:cloud'
        self.check_bad(self.transport)
        self.assertEqual(self.calls, [])

    def test_remote_metadata_never_generates(self):
        def remote(port, endpoint, payload, timeout):
            if endpoint == 'show': return {'remote_host': 'https://example.invalid'}
            return self.transport(port, endpoint, payload, timeout)
        self.check_bad(remote)
        self.assertNotIn('generate', self.calls)

    def test_unknown_model_never_generates(self):
        self.args.model = 'not-installed:local'
        self.check_bad(self.transport)
        self.assertNotIn('generate', self.calls)

    def test_context_overflow_is_not_silent_truncation(self):
        self.args.context = 500
        self.check_bad(self.transport)
        self.assertEqual(self.calls, [])

    def test_stale_source_is_rejected(self):
        def stale(*args):
            result = self.transport(*args)
            if args[1] == 'generate': (self.root/'source.txt').write_text('changed')
            return result
        self.check_bad(stale)

    def test_length_limit_is_not_completion(self):
        def limited(*args):
            result = self.transport(*args)
            if args[1] == 'generate': result['done_reason'] = 'length'
            return result
        self.check_bad(limited)

    def test_malformed_result_is_rejected(self):
        def malformed(*args):
            result = self.transport(*args)
            if args[1] == 'generate': result['response'] = '{}'
            return result
        self.check_bad(malformed)

    def test_malformed_endpoint_still_retains_diagnostics(self):
        for endpoint, bad in [('version', None), ('tags', {'models': [None]}),
                              ('show', {'model_info': {}, 'details': []})]:
            with self.subTest(endpoint=endpoint):
                self.args.output = self.root / endpoint
                def malformed(port, ep, payload, timeout):
                    if ep == endpoint: return bad
                    return self.transport(port, ep, payload, timeout)
                self.check_bad(malformed)

    def test_model_replacement_is_rejected(self):
        def replaced(*args):
            result = self.transport(*args)
            if args[1] == 'tags' and self.calls.count('tags') == 2:
                result['models'][0]['digest'] = 'changed'
            return result
        self.check_bad(replaced)

    def test_external_input_is_rejected(self):
        self.args.input = ['../outside.txt']
        self.check_bad(self.transport)
        self.assertEqual(self.calls, [])

    def test_existing_output_is_preserved(self):
        self.args.output.mkdir()
        (self.args.output/'result.json').write_text('prior evidence')
        with self.assertRaises(FileExistsError): run(self.args, self.transport)
        self.assertEqual((self.args.output/'result.json').read_text(), 'prior evidence')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LocalReviewTest)
    if suite.countTestCases() == 0:
        raise SystemExit('required local-review tests were not selected')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful() or bool(result.skipped))
