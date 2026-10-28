import threading
import unittest
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.learning_protocol import evaluate_backend
from rulegen.cancellation import SynthesisCancelled

class CancellationTests(unittest.TestCase):
    def test_all_backends_cancel_before_search(self):
        event=threading.Event()
        event.set()
        with Registry(':memory:') as lib:
            for backend in ('legacy','legacy-goal'):
                with self.subTest(backend=backend):
                    with self.assertRaises(SynthesisCancelled):
                        evaluate_backend(backend,[(1,1)],lib,budget=20,cancel=event)
        with FunctionalRegistry(':memory:',tier='algebra') as lib:
            with self.assertRaises(SynthesisCancelled):
                evaluate_backend('functional',[({'x':1},1)],lib,budget=20,cancel=event)
    def test_predicate_cancel(self):
        with Registry(':memory:') as lib:
            with self.assertRaises(SynthesisCancelled):
                evaluate_backend('legacy',[(1,1)],lib,budget=20,cancel=lambda:True)
