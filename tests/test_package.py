import tempfile, unittest
from pathlib import Path
from rulegen.discovery import benchmark
from rulegen.engine import Registry, PAIR, INT, BOOL
from rulegen.typedholes import candidates
from rulegen.benchmark import compare

class PackageTests(unittest.TestCase):
 def test_discovery(self):
  with tempfile.TemporaryDirectory() as d:
   r=benchmark(Path(d)/"db")
   self.assertTrue(r["admitted"],r)
   self.assertTrue(r["held_out"])
 def test_holes(self):
  cs=list(candidates(PAIR(INT,BOOL),PAIR(BOOL,INT),5))
  self.assertIn(["pair",["snd",["arg",0]],["fst",["arg",0]]],cs)
 def test_controls(self):
  r=compare({"a":[(2,1,True)],"b":[(2,0,False)]},steps=6)
  self.assertEqual(set(r),{"adaptive","round_robin","random"})
  self.assertTrue(all(x["cost"]==12 for x in r.values()))
if __name__=="__main__":unittest.main()
