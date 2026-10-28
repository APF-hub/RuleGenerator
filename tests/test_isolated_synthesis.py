import unittest
from rulegen.isolated_synthesis import synthesize_functional_isolated
from rulegen.process_isolation import IsolatedExecutionError

class IsolatedSynthesisTests(unittest.TestCase):
    def test_identity(self):
        result=synthesize_functional_isolated([({'x':1},1),({'x':2},2)],tier='algebra',budget=30,max_nodes=2)
        self.assertIsNotNone(result['program'])
        self.assertLessEqual(result['checks'],30)
    def test_generation_exhaustion(self):
        result=synthesize_functional_isolated([({'x':1},999)],tier='algebra',budget=100,max_nodes=5,max_generated=1)
        self.assertTrue(result['exhausted'])
    def test_invalid_request(self):
        with self.assertRaises(ValueError):
            synthesize_functional_isolated([({'x':1},1)],budget=0)
    def test_invalid_observation_rejected(self):
        with self.assertRaises(IsolatedExecutionError):
            synthesize_functional_isolated([('bad',1)],tier='algebra')
