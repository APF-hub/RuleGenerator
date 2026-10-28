import tempfile,unittest
from m60 import Registry, strict_equal
from m61_discovery import discover,benchmark

class M61DiscoveryTests(unittest.TestCase):
    def test_swap_discovered_and_persisted(self):
        with tempfile.TemporaryDirectory() as d:
            path=d+"/db"
            result=benchmark(path)
            self.assertTrue(result["admitted"],result)
            self.assertTrue(result["held_out"])
            self.assertEqual(Registry(path).call("swap",True,4),(4,True))
    def test_invalid_validation_prevents_admission(self):
        with tempfile.TemporaryDirectory() as d:
            registry=Registry(d+"/db")
            result=discover(registry,"invalid",
                [((1,True),(True,1))],
                [((2,False),(2,False))])
            self.assertFalse(result["admitted"])
    def test_type_sensitive_observation_equality(self):
        self.assertFalse(strict_equal((1, True), (True, 1)))
        self.assertFalse(strict_equal([1, True], [True, 1]))
        self.assertTrue(strict_equal((1, True), (1, True)))
    def test_training_validation_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            registry=Registry(d+"/db")
            rows=[((1,True),(True,1))]
            with self.assertRaises(ValueError):
                discover(registry,"invalid",rows,rows)

if __name__=="__main__":unittest.main()
