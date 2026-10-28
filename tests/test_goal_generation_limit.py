import unittest
from rulegen.engine import Registry
from rulegen.typedholes import synthesize_goal

class GoalGenerationLimitTests(unittest.TestCase):
    def test_cap(self):
        with Registry(':memory:') as lib:
            result=synthesize_goal(lib,[(1,999)],max_nodes=5,budget=100,max_generated=2)
            self.assertTrue(result['exhausted'])
            self.assertLessEqual(result['stats']['generated'],2)
    def test_identity(self):
        with Registry(':memory:') as lib:
            result=synthesize_goal(lib,[(1,1),(2,2)],max_nodes=1,budget=20,max_generated=10)
            self.assertIsNotNone(result['program'])
    def test_invalid_cap(self):
        with Registry(':memory:') as lib:
            with self.assertRaises(ValueError):
                synthesize_goal(lib,[(1,1)],max_generated=0)
