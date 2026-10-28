"""Persistent evidence-gated library of typed functional AST operators.

Separate from the legacy polymorphic Registry: the two type systems are not
interchangeable. Promotion is explicit, never implied by proposing a pattern.
"""
import hashlib
import json
import sqlite3
from .functional import Core, TIERS

def _json(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def _digest(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()

class FunctionalRegistry:
    def __init__(self,path,tier="math"):
        if tier not in TIERS:raise ValueError("unknown tier")
        self.tier=tier
        self.db=sqlite3.connect(str(path))
        self.db.execute("""CREATE TABLE IF NOT EXISTS functional_operators (
            name TEXT PRIMARY KEY, definition TEXT NOT NULL,
            evidence TEXT NOT NULL, status TEXT NOT NULL)""")
        self.db.commit()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self,*_):
        self.close()

    def active(self):
        rows=self.db.execute("SELECT name,definition FROM functional_operators WHERE status='active' ORDER BY name")
        return {name:json.loads(definition) for name,definition in rows}

    def core(self,max_steps=100000):
        core=Core(self.tier,max_steps=max_steps)
        pending=self.active()
        while pending:
            progressed=False
            for name,definition in list(pending.items()):
                try:core.validate_definition(name,definition)
                except (KeyError,TypeError):
                    continue
                del pending[name]
                progressed=True
            if not progressed:raise ValueError("invalid or cyclic persisted definitions")
        return core

    def evidence(self,name):
        row=self.db.execute("SELECT evidence,status FROM functional_operators WHERE name=?",(name,)).fetchone()
        return None if row is None else {"evidence":json.loads(row[0]),"status":row[1]}

    def promote(self,candidate,training,validation,*,tolerance=1e-9):
        """Require disjoint input sets and exact/finite numeric held-out agreement.

        Evidence rows are (positional_arguments, expected_output). This verifies
        supplied observations, not their real-world independence or provenance.
        """
        if not training or not validation:raise ValueError("training and validation required")
        if tolerance<0:raise ValueError("negative tolerance")
        if candidate.get("status")!="candidate":raise ValueError("only proposals can be promoted")
        name=candidate["name"]
        if self.db.execute("SELECT 1 FROM functional_operators WHERE name=?",(name,)).fetchone():
            raise ValueError("operator name already used")
        core=self.core()
        definition=candidate["definition"]
        core.validate_definition(name,definition)
        train_inputs={_digest(row[0]) for row in training}
        valid_inputs={_digest(row[0]) for row in validation}
        if train_inputs & valid_inputs:raise ValueError("training/validation input overlap")
        params=definition["params"]
        import math
        for args,expected in list(training)+list(validation):
            if len(args)!=len(params):raise ValueError("argument count mismatch")
            result=core.execute({"op":"call","name":name,
                "args":[{"op":"literal","value":v} for v in args]})
            if type(result) is type(expected) and result==expected:continue
            if type(result) in (int,float) and type(expected) in (int,float):
                if math.isfinite(result) and math.isfinite(expected) and abs(result-expected)<=tolerance:continue
            raise ValueError("candidate failed evidence")
        evidence={"training_count":len(training),"validation_count":len(validation),
                  "training_digest":_digest(training),"validation_digest":_digest(validation),
                  "tolerance":tolerance,"tier":self.tier}
        self.db.execute("INSERT INTO functional_operators VALUES (?,?,?,?)",
                        (name,_json(definition),_json(evidence),"active"))
        self.db.commit()
        return evidence

    def retire(self,name):
        self.db.execute("UPDATE functional_operators SET status='retired' WHERE name=?",(name,))
        self.db.commit()
