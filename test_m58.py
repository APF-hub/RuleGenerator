import tempfile
import unittest
from pathlib import Path
from m58 import solve

class NogoodTests(unittest.TestCase):
    def test_sat(self):
        with tempfile.TemporaryDirectory() as d:
            r=solve(Path(d)/"db",[[0,1],[0,1]],[[(0,1)],[(1,0)]])
            self.assertEqual(r["solution"],{0:1,1:0})
    def test_unsat(self):
        with tempfile.TemporaryDirectory() as d:
            r=solve(Path(d)/"db",[[0,1]],[[(0,0)],[(0,1)]])
            self.assertTrue(r["complete"])
            self.assertIsNone(r["solution"])
    def test_resume(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/"db"
            a=solve(db,[[0,1]]*4,[[(0,1)]],budget=1)
            b=solve(db,[[0,1]]*4,[[(0,1)]],budget=100)
            self.assertEqual(b["visits_total"],a["visits_total"]+b["visits_this_call"])
            self.assertEqual(b["solution"][0],1)
    def test_problem_scope(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/"db"
            solve(db,[[0,1]],[[(0,1)]],budget=1)
            with self.assertRaises(ValueError):
                solve(db,[[0,1]],[[(0,0)]],budget=1)

if __name__ == "__main__":
    unittest.main()
