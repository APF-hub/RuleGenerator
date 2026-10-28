import unittest
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.learning_protocol import evaluate_backend
from rulegen.cancellation import SynthesisDeadlineExceeded

class DeadlineTests(unittest.TestCase):
    def test_immediate_deadline_all_backends(self):
        with Registry(':memory:') as lib:
            for backend in ('legacy','legacy-goal'):
                with self.subTest(backend=backend):
                    with self.assertRaises(SynthesisDeadlineExceeded):
                        evaluate_backend(backend,[(1,1)],lib,budget=20,timeout_seconds=0)
        with FunctionalRegistry(':memory:',tier='algebra') as lib:
            with self.assertRaises(SynthesisDeadlineExceeded):
                evaluate_backend('functional',[({'x':1},1)],lib,budget=20,timeout_seconds=0)
    def test_invalid_timeout(self):
        with Registry(':memory:') as lib:
            for value in (-1,float('nan'),float('inf'),True):
                with self.assertRaises(ValueError):
                    evaluate_backend('legacy',[(1,1)],lib,budget=20,timeout_seconds=value)
    def test_no_timeout_preserves_success(self):
        with Registry(':memory:') as lib:
            result=evaluate_backend('legacy',[(1,1),(2,2)],lib,budget=20,max_nodes=1)
            self.assertTrue(result['solved'])
