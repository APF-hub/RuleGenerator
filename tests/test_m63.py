import tempfile,unittest
from pathlib import Path
from rulegen.engine import Registry, INT, BOOL, PAIR, typecheck
from rulegen.typedholes import synthesize_goal,enumerate_goal
from rulegen.benchmark import compare

class TypedHolesTests(unittest.TestCase):
 def test_discovery(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(Path(d)/'db')
   rows=[((1,True),(True,1)),((2,False),(False,2))]
   out=synthesize_goal(r,rows,max_nodes=5)
   self.assertIsNotNone(out['program'],out)
   self.assertGreater(out['stats']['type_pruned'],0)
 def test_incompatible_operator_pruned(self):
  it,stats=enumerate_goal(BOOL,INT,max_nodes=3)
  candidates=list(it)
  self.assertTrue(candidates)
  self.assertGreater(stats['type_pruned'],0)
  for e in candidates:self.assertEqual(typecheck(e,INT),BOOL)
 def test_scope_failures(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(Path(d)/'db')
   rows=[(1,2),(2,3)]
   a=synthesize_goal(r,rows,max_nodes=3,budget=1)
   b=synthesize_goal(r,rows,max_nodes=3,budget=100)
   self.assertGreater(b['failure_skips'],0)
   c=synthesize_goal(r,[(1,3),(2,4)],max_nodes=3,budget=100)
   self.assertEqual(c['failure_skips'],0)
 def test_portfolio_controls(self):
  outcomes={'a':[(2,2,True)]*20,'b':[(2,0,False)]*20,'c':[(2,1,True)]*20}
  x=compare(outcomes,steps=30)
  self.assertEqual(set(x),{'adaptive','round_robin','random'})
  self.assertGreater(x['adaptive']['validated_gain'],x['round_robin']['validated_gain'])
 def test_no_oracle_reward(self):
  outcomes={'a':[(1,100,False)]*10,'b':[(1,1,True)]*10}
  x=compare(outcomes,steps=10)
  self.assertLessEqual(x['adaptive']['validated_gain'],10)
if __name__=='__main__':unittest.main()
