"""Protocol and result controls; these fixtures do not claim provider/model quality."""
import argparse
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
from model_review import run, endpoint, payload_for, NoRedirect


class ModelReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'source.txt').write_text('Release the owned resource on cancellation.\n')
        self.env=patch.dict(os.environ,{'FIXTURE_API_KEY':'fixture-secret-value'});self.env.start();self.addCleanup(self.env.stop)
        self.args=argparse.Namespace(root=self.root,output=self.root/'result',mode='implementation',purpose='judge',
            dimension=['implementation_conformance'],claim='cancellation cleans up',input=['source.txt'],provider='deepseek',
            protocol=None,base_url='https://fixture.invalid/v1',api_key_env='FIXTURE_API_KEY',ca_file=None,
            model='fixture-model',context=8192,predict=512,timeout=5,temperature=None)
        self.calls=[]

    def answer(self, verdict='insufficient_evidence'):
        return {'verdict':verdict,'reason':'No observed cleanup','evidence':['source.txt:1'],'next_action':'Inspect release owner',
                'assessments':[{'dimension':'implementation_conformance','verdict':verdict,'reason':'No observation','evidence':['source.txt:1']}]}

    def transport(self,url,headers,payload,timeout,ca_file):
        self.calls.append((url,headers,payload))
        answer=json.dumps(self.answer())
        base={'model':'fixture-model','id':'fixture','usage':{'input_tokens':5,'output_tokens':5}}
        if url.endswith('/messages'):
            return dict(base,stop_reason='end_turn',content=[{'type':'thinking','thinking':'HIDDEN'},{'type':'text','text':answer}])
        if url.endswith('/responses'):
            return dict(base,status='completed',output=[{'type':'reasoning','summary':'HIDDEN'},
                {'type':'message','status':'completed','content':[{'type':'output_text','text':answer}]}])
        return dict(base,choices=[{'finish_reason':'stop','message':{'role':'assistant','content':answer,'reasoning_content':'HIDDEN'}}])

    def bad(self,transport):
        code,result=run(self.args,transport);self.assertEqual(code,2);self.assertEqual(result['status'],'unavailable_or_invalid')
        self.assertTrue((self.args.output/'result.json').is_file());return result

    def test_all_provider_protocols_keep_final_text_and_correct_auth(self):
        for provider in ('deepseek','glm','claude','codex'):
            with self.subTest(provider=provider):
                self.args.provider=provider;self.args.output=self.root/provider
                code,result=run(self.args,self.transport);self.assertEqual(code,0)
                url,headers,payload=self.calls[-1]
                self.assertIn('x-api-key' if provider=='claude' else 'Authorization',headers)
                text=(self.args.output/'result.json').read_text()
                self.assertNotIn('HIDDEN',text);self.assertNotIn('fixture-secret-value',text)
                self.assertEqual(result['acceptance'],'requires_source_inspection')
                self.assertEqual(payload['model'],'fixture-model')
                if provider=='codex':self.assertFalse(payload['store']);self.assertNotIn('temperature',payload)

    def test_failed_api_does_not_retry_or_leak_body(self):
        def failed(*args): raise urllib.error.HTTPError(args[0],401,'fixture-secret-value',None,None)
        result=self.bad(failed);self.assertEqual(result['error'],'HTTP 401; response body omitted')
        self.assertNotIn('fixture-secret-value',(self.args.output/'result.json').read_text())

    def test_missing_key_stops_before_transmission(self):
        self.args.api_key_env='MISSING_FIXTURE_KEY';self.bad(self.transport);self.assertEqual(self.calls,[])

    def test_unsafe_endpoints_and_redirects_are_rejected(self):
        for url in ['http://example.org','https://user:pass@example.org','https://example.org?k=x','https://example.org#x']:
            with self.subTest(url=url):
                self.args.output=self.root/str(len(list(self.root.iterdir())));self.args.base_url=url
                self.bad(self.transport)
        with self.assertRaises(Exception):NoRedirect().redirect_request(None,None,None,None,None,None)
        self.assertEqual(self.calls,[])

    def test_credential_in_packet_is_not_transmitted(self):
        (self.root/'source.txt').write_text('fixture-secret-value')
        self.bad(self.transport);self.assertEqual(self.calls,[])
        self.assertNotIn('fixture-secret-value',(self.args.output/'result.json').read_text())

    def test_packet_overflow_missing_input_and_timeout_validation(self):
        for variant in ('large','outside','nan'):
            with self.subTest(variant=variant):
                self.args.output=self.root/variant
                self.args.input=['../outside'] if variant=='outside' else ['source.txt']
                self.args.context=1 if variant=='large' else 8192
                self.args.timeout=float('nan') if variant=='nan' else 5
                self.bad(self.transport)
        self.assertEqual(self.calls,[])

    def test_changed_source_is_not_fresh(self):
        def changed(*args):
            value=self.transport(*args);(self.root/'source.txt').write_text('changed');return value
        self.bad(changed)

    def test_incomplete_and_unexpected_content_stays_non_success(self):
        for provider in ('deepseek','claude','codex'):
            with self.subTest(provider=provider):
                self.args.provider=provider;self.args.output=self.root/provider
                def incomplete(*args):
                    value=self.transport(*args)
                    if provider=='deepseek':value['choices'][0]['finish_reason']='length'
                    elif provider=='claude':value['stop_reason']='max_tokens'
                    else:value['status']='incomplete'
                    return value
                self.bad(incomplete)

    def test_dimensions_citations_and_aggregate(self):
        for variant in ('missing','duplicate','line','outside','contradiction','badjson','empty'):
            with self.subTest(variant=variant):
                self.args.output=self.root/variant
                def malformed(*args):
                    value=self.transport(*args);answer=self.answer()
                    if variant=='missing':answer.pop('assessments')
                    elif variant=='duplicate':answer['assessments']*=2
                    elif variant=='line':answer['assessments'][0]['evidence']=['source.txt:999']
                    elif variant=='outside':answer['evidence']=['invented.rs:1']
                    elif variant=='contradiction':answer['verdict']='supported'
                    value['choices'][0]['message']['content']='invalid' if variant=='badjson' else '' if variant=='empty' else json.dumps(answer)
                    return value
                self.bad(malformed)

    def test_supported_and_violated_are_still_advice(self):
        for verdict in ('supported','violated'):
            self.args.output=self.root/verdict
            def decisive(*args):
                value=self.transport(*args);value['choices'][0]['message']['content']=json.dumps(self.answer(verdict));return value
            code,result=run(self.args,decisive);self.assertEqual(code,0)
            self.assertEqual(result['acceptance'],'requires_source_inspection')

    def test_violated_result_needs_action_and_model_identity(self):
        for variant in ('no_action','wrong_model','malformed'):
            with self.subTest(variant=variant):
                self.args.output=self.root/variant
                def bad_result(*args):
                    value=self.transport(*args)
                    if variant=='malformed':return []
                    if variant=='wrong_model':value['model']='unselected-model'
                    else:
                        answer=self.answer('violated');answer['next_action']='none'
                        value['choices'][0]['message']['content']=json.dumps(answer)
                    return value
                self.bad(bad_result)

    def test_bounded_citation_ranges_and_incomplete_metadata(self):
        (self.root/'source.txt').write_text('one\ntwo\nthree\n')
        for ref, expected in [('source.txt:1-2',0),('source.txt:3-2',2),('source.txt:1-4',2)]:
            self.args.output=self.root/ref.replace(':','-')
            def ranged(*args):
                value=self.transport(*args);answer=self.answer();answer['evidence']=[ref]
                value['choices'][0]['message']['content']=json.dumps(answer);return value
            self.assertEqual(run(self.args,ranged)[0],expected)
        self.args.output=self.root/'truncated'
        def limited(*args):
            value=self.transport(*args);value['choices'][0]['finish_reason']='length';return value
        result=self.bad(limited)
        self.assertEqual(result['response']['finish_reasons'],['length'])
        self.assertEqual(result['response']['usage']['output_tokens'],5)

    def test_existing_result_is_never_overwritten(self):
        self.args.output.mkdir();p=self.args.output/'result.json';p.write_text('prior evidence')
        with self.assertRaises(FileExistsError):run(self.args,self.transport)
        self.assertEqual(p.read_text(),'prior evidence')


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ModelReviewTest)
    if suite.countTestCases()==0:raise SystemExit('required model-review tests absent')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful() or bool(result.skipped))
