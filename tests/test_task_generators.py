import unittest
from rulegen.engine import execute, typecheck, typ
from rulegen.task_generators import generate_task, ast_complexity


class GeneratedTaskTests(unittest.TestCase):
    def test_seeded_arithmetic_complexity_and_semantics(self):
        for layers in (1,2,3):
            task=generate_task(42,family="arithmetic",complexity=layers)
            self.assertEqual(task,generate_task(42,family="arithmetic",complexity=layers))
            self.assertEqual(task["generator_complexity"]["nodes"],1+2*layers)
            self.assertEqual(task["generator_complexity"]["depth"],1+layers)
            self.assertEqual(task["generator_complexity"]["calls"],layers)
            rows=task["training"]+task["validation"]+task["test"]
            self.assertEqual(len({repr(x) for x,_ in rows}),len(rows))
            for x,y in rows:
                self.assertEqual(execute(task["generator_program"],x),y)
                self.assertEqual(typecheck(task["generator_program"],typ(x)),typ(y))

    def test_pair_generator(self):
        task=generate_task(19,family="pair")
        self.assertEqual(task["generator_complexity"],
                         {"nodes":6,"depth":3,"calls":3})
        for x,y in task["training"]+task["validation"]+task["test"]:
            self.assertEqual(y,(x[1],x[0]))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            generate_task(1,complexity=0)
        with self.assertRaises(ValueError):
            generate_task(1,family="pair",complexity=2)
        with self.assertRaises(ValueError):
            generate_task(1,training_count=2002)
