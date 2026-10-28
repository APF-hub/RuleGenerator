import unittest
from rulegen.functional_synthesis import synthesize_functional

class GenerationLimitTests(unittest.TestCase):
    def test_cap(self):
        result=synthesize_functional([({'x':1},999)],tier='algebra',budget=100,max_nodes=5,max_generated=5)
        self.assertTrue(result['exhausted'])
    def test_initial_pool(self):
        result=synthesize_functional([({'x':1},999)],tier='algebra',budget=100,max_nodes=5,max_generated=1)
        self.assertEqual(result['checks'],0)
        self.assertTrue(result['exhausted'])
    def test_existing_success(self):
        result=synthesize_functional([({'x':2},2)],tier='algebra',budget=20,max_nodes=1,max_generated=20)
        self.assertIsNotNone(result['program'])
