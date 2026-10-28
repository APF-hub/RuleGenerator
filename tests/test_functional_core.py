import unittest
import math
from rulegen.functional import Core, INT, REAL, LIST

def lit(x):
    return {"op": "literal", "value": x}

def var(x):
    return {"op": "var", "name": x}

def call(name, *args):
    return {"op": "call", "name": name, "args": list(args)}

class FunctionalCoreTests(unittest.TestCase):
    def test_arithmetic(self):
        p = call("*", call("+", lit(2), lit(3)), lit(4))
        self.assertEqual(Core().execute(p), 20)

    def test_math_tier(self):
        p = call("sin", lit(0.5))
        with self.assertRaises(TypeError):
            Core("algebra").infer(p)
        self.assertAlmostEqual(Core("math").execute(p), math.sin(0.5))

    def test_lambda(self):
        fn = {"op":"lambda","name":"x","type":INT,"body":call("+",var("x"),lit(1))}
        p = {"op":"apply","fn":fn,"arg":lit(4)}
        self.assertEqual(Core().execute(p), 5)

    def test_map(self):
        fn = {"op":"lambda","name":"x","type":INT,"body":call("*",var("x"),lit(2))}
        p = call("map", fn, {"op":"list","items":[lit(1),lit(2),lit(3)]})
        self.assertEqual(Core("functional").infer(p), LIST(INT))
        self.assertEqual(Core("functional").execute(p), [2,4,6])

    def test_operator_definition(self):
        c = Core("math")
        definition = {
            "params":[{"name":"a","type":REAL},{"name":"f","type":REAL},{"name":"t","type":REAL}],
            "return_type":REAL,
            "body":call("*",var("a"),call("sin",call("*",var("f"),var("t")))
        }
        c.validate_definition("wave",definition)
        self.assertAlmostEqual(c.execute(call("wave",lit(0.4),lit(2.0),lit(0.5))),0.4*math.sin(1))

    def test_reject_unknown(self):
        with self.assertRaises(TypeError):
            Core().infer(call("unknown",lit(1)))

    def test_step_limit(self):
        with self.assertRaises(RuntimeError):
            Core(max_steps=2).execute(call("+",lit(1),lit(2)))

if __name__ == "__main__":
    unittest.main()
