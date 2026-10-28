import unittest
from rulegen.isolated_synthesis import synthesize_functional_isolated
from rulegen.process_isolation import IsolatedExecutionError

class IsolatedWarmSynthesisTests(unittest.TestCase):
    def test_snapshot_reuse(self):
        increment={'params':[{'name':'a','type':['Int']}], 'return_type':['Int'], 'body':{'op':'call','name':'+','args':[{'op':'var','name':'a'},{'op':'literal','value':1}]}}
        result=synthesize_functional_isolated([({'x':3},4),({'x':7},8)],tier='algebra',max_nodes=2,budget=100,definitions={'increment':increment})
        self.assertIsNotNone(result['program'])
    def test_reject_invalid_snapshot(self):
        with self.assertRaises(IsolatedExecutionError):
            synthesize_functional_isolated([({'x':1},1)],tier='algebra',definitions={'bad':{'params':[],'return_type':['Int'],'body':{'op':'var','name':'missing'}}})
    def test_cold_still_works(self):
        result=synthesize_functional_isolated([({'x':1},1)],tier='algebra',max_nodes=1)
        self.assertIsNotNone(result['program'])
