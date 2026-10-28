import tempfile
import unittest
from pathlib import Path
from rulegen.operator_library import OperatorLibrary
from rulegen.engine import INT

class OperatorLibraryTests(unittest.TestCase):
    def test_functional_lifecycle_and_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"lib.sqlite"
            definition={"params":[{"name":"x","type":["Int"]}],
                        "return_type":["Int"],
                        "body":{"op":"call","name":"+","args":[
                            {"op":"var","name":"x"},{"op":"literal","value":1}]}}
            with OperatorLibrary(path,backend="functional",tier="algebra") as lib:
                result=lib.admit("inc",definition,[([2],3)],[([5],6)])
                self.assertEqual(result["validation_count"],1)
                self.assertIn("inc",lib.active())
            with OperatorLibrary(path,backend="functional",tier="algebra") as lib:
                self.assertIn("inc",lib.active())
                self.assertEqual(lib.status("inc")["status"],"active")
                lib.retire("inc")
                self.assertNotIn("inc",lib.active())
                self.assertEqual(lib.status("inc")["status"],"retired")
    def test_legacy_lifecycle(self):
        with OperatorLibrary(":memory:",backend="legacy") as lib:
            definition={"args":[INT],"out":INT,
                        "body":["call","add",["arg",0],["const",1]]}
            self.assertTrue(lib.admit("inc",definition,[([2],3)],[([5],6)]))
            self.assertIn("inc",lib.active())
            self.assertEqual(lib.status("inc")["status"],"active")
            lib.retire("inc")
            self.assertNotIn("inc",lib.active())
    def test_unknown_backend(self):
        with self.assertRaises(ValueError):
            OperatorLibrary(":memory:",backend="unknown")

if __name__=="__main__":unittest.main()
