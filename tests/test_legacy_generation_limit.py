import unittest
from rulegen.engine import Registry, synthesize

class LegacyGenerationTests(unittest.TestCase):
    def test_limit(self):
        with Registry(':memory:') as registry:
            result=synthesize(registry,[(1,999)],max_nodes=5,budget=100,max_generated=5)
            self.assertTrue(result['exhausted'])
    def test_identity(self):
        with Registry(':memory:') as registry:
            result=synthesize(registry,[(1,1),(2,2)],max_nodes=1,budget=20,max_generated=20)
            self.assertIsNotNone(result['program'])
