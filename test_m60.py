import tempfile, unittest
from m60 import Registry,var,pair,unify,listof
class TestM60(unittest.TestCase):
 def test_occurs(self):
  with self.assertRaises(TypeError):unify(var("a"),listof(var("a")))
 def test_swap(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(d+"/db")
   a,b=var("a"),var("b")
   self.assertTrue(r.admit("swap",["pair",["arg",1],["arg",0]],[a,b],pair(b,a),[([1,True],(True,1))],[([[1,2],False],(False,[1,2]))]))
   self.assertEqual(Registry(d+"/db").call("swap",2,False),(False,2))
   r.retire("swap")
   with self.assertRaises(KeyError):r.call("swap",1,2)
if __name__=="__main__":unittest.main()
