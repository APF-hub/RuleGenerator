"""Domain-independent experiment ledger for observation-to-program reconstruction.

Every run stores its adapter identity, observation digest, executable candidate,
loss, and budget. This is reusable for future image/time-series adapters.
"""
import hashlib
import json
import sqlite3

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

class ExperimentStore:
    def __init__(self, database):
        self.owns_connection=not isinstance(database,sqlite3.Connection)
        self.db=sqlite3.connect(str(database)) if self.owns_connection else database
        self.db.execute("""CREATE TABLE IF NOT EXISTS reconstruction_experiments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adapter TEXT NOT NULL, observation_sha256 TEXT NOT NULL,
            program TEXT NOT NULL, loss REAL NOT NULL,
            evaluations INTEGER NOT NULL, budget INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        self.db.commit()
    def record(self, adapter, observation, result, budget):
        if not adapter or budget<1 or result.evaluations>budget or result.loss<0:
            raise ValueError('invalid experiment')
        fingerprint=hashlib.sha256(canonical(observation).encode()).hexdigest()
        with self.db:
            cursor=self.db.execute("""INSERT INTO reconstruction_experiments(
                adapter,observation_sha256,program,loss,evaluations,budget)
                VALUES(?,?,?,?,?,?)""",
                (adapter,fingerprint,canonical(result.program),result.loss,
                 result.evaluations,budget))
        return cursor.lastrowid
    def best(self, adapter, observation):
        fingerprint=hashlib.sha256(canonical(observation).encode()).hexdigest()
        row=self.db.execute("""SELECT id,program,loss,evaluations,budget
            FROM reconstruction_experiments
            WHERE adapter=? AND observation_sha256=?
            ORDER BY loss ASC,id ASC LIMIT 1""",(adapter,fingerprint)).fetchone()
        if row is None:return None
        return dict(id=row[0],program=json.loads(row[1]),loss=row[2],
                    evaluations=row[3],budget=row[4])
    def close(self):
        if self.owns_connection:self.db.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
