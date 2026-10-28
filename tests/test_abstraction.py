import math
import unittest
from rulegen.functional import Core
from rulegen.abstraction import propose,validate

def lit(x):
    return {"op":"literal","value":x}

def call(name,*args):
    return {"op":"call","name":name,"args":list(args)}

class AbstractionTests(unittest.TestCase):
    def test_discover_parameterized_wave_shape(self):
        a=call("*",lit(0.4),call("sin",call("*",lit(2.0),lit(0.5))))
        b=call("*",lit(0.7),call("sin",call("*",lit(3.0),lit(0.5))))
        candidate=propose("learned_wave",[(a,{}),(b,{})])
        self.assertEqual(candidate["status"],"candidate")
        self.assertEqual(len(candidate["definition"]["params"]),2)
        report=validate(candidate,[([0.2,4.0],0.2*math.sin(2.0)),
                                   ([0.8,5.0],0.8*math.sin(2.5))])
        self.assertEqual(report["status"],"validated")

    def test_reject_wrong_held_out_examples(self):
        a=call("+",lit(1),lit(2))
        b=call("+",lit(3),lit(2))
        candidate=propose("offset",[(a,{}),(b,{})],Core())
        report=validate(candidate,[([5],99)],Core())
        self.assertEqual(report["status"],"rejected")

    def test_cannot_learn_from_single_example(self):
        with self.assertRaises(ValueError):
            propose("x",[(lit(1),{})])

if __name__=="__main__":
    unittest.main()
