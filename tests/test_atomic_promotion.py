"""Platform P1: transaction failure and persistence invariants."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rulegen.evidence import Evidence
from rulegen.functional_registry import FunctionalRegistry

def lit(value):
    return {"op":"literal","value":value}

class AtomicPromotionTests(unittest.TestCase):
    def candidate(self):
        return {"status":"candidate","name":"inc",
                "definition":{"params":[{"name":"x","type":["Int"]}],
                              "return_type":["Int"],
                              "body":{"op":"call","name":"+",
                                      "args":[{"op":"var","name":"x"},lit(1)]}}}

    def test_ledger_failure_rolls_back_operator_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"lib.db"
            with FunctionalRegistry(path,tier="algebra") as lib:
                with patch.object(lib.evidence_ledger,"append_in_transaction",
                                  side_effect=sqlite3.OperationalError("injected failure")):
                    with self.assertRaises(sqlite3.OperationalError):
                        lib.promote(self.candidate(),[([2],3)],[([5],6)])
                self.assertNotIn("inc",lib.active())
                self.assertEqual(lib.evidence_ledger.count("validation"),0)
                lib.promote(self.candidate(),[([2],3)],[([5],6)])
                self.assertEqual(lib.evidence_ledger.count("validation"),1)
            with FunctionalRegistry(path,tier="algebra") as lib:
                self.assertIn("inc",lib.active())
                self.assertEqual(lib.evidence_ledger.count("validation"),1)

    def test_evidence_requires_caller_transaction(self):
        with sqlite3.connect(":memory:") as db:
            ledger=Evidence(db)
            with self.assertRaises(RuntimeError):
                ledger.append_in_transaction("validation","scope",{},{"ok":True})
            self.assertEqual(ledger.count(),0)
            ledger.append("validation","scope",{},{"ok":True})
            self.assertEqual(ledger.count("validation"),1)

if __name__=="__main__":
    unittest.main()
