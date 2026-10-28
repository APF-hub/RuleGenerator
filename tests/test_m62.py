import tempfile, unittest
from pathlib import Path
from rulegen.portfolio import Portfolio
from rulegen.engine import Registry, execute
from rulegen.discovery import discover

class PortfolioTests(unittest.TestCase):
 def test_exploration_and_persistence(self):
  with tempfile.TemporaryDirectory() as d:
   p=Portfolio(Path(d)/'p.db',exploration_every=3)
   p.register('a');p.register('b')
   self.assertEqual(p.select()['direction'],'a')
   p.record('a',10,0.9,False)
   self.assertEqual(p.select()['direction'],'b')
   p.record('b',5,2,True)
   self.assertEqual(p.select()['direction'],'b')
   p.record('b',5,1,True)
   self.assertEqual(p.select()['mode'],'explore')
   q=Portfolio(Path(d)/'p.db',exploration_every=3)
   self.assertEqual(sum(x['experiments'] for x in q.report()),3)
   self.assertEqual(next(x for x in q.report() if x['name']=='a')['observed_gain'],0)
 def test_no_unvalidated_gain(self):
  with tempfile.TemporaryDirectory() as d:
   p=Portfolio(Path(d)/'p.db');p.register('x');p.record('x',2,100,False)
   self.assertEqual(p.report()[0]['observed_gain'],0)
 def test_discovery_and_restart(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'rules.db';r=Registry(db)
   out=discover(r,'identity',[(1,1),(2,2)],[(False,False),([1,2],[1,2])],max_nodes=2)
   self.assertTrue(out['admitted'],out)
   self.assertTrue(execute(['call','identity',['const',True]],None,Registry(db).active()))
 def test_negative_validation(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(Path(d)/'rules.db')
   self.assertFalse(discover(r,'wrong',[(1,1),(2,2)],[(False,True)],max_nodes=2)['admitted'])
if __name__=='__main__':unittest.main()
