"""M68: versioned evidence ledger with sound, narrowly scoped proof certificates.

Only independently checkable *type contradictions* may be used as permanent
nogoods. Observation mismatches are empirical evidence, never logical proofs.
"""
import hashlib
import json
import sqlite3

SCHEMA_VERSION = 1

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",",":"), default=str)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

class Evidence:
    def __init__(self, connection):
        self.db=connection
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS rg_metadata(
            key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS rg_evidence(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL CHECK(kind IN
                ('type_proof','empirical_failure','validation','search_trial')),
            scope TEXT NOT NULL, candidate TEXT NOT NULL,
            payload TEXT NOT NULL, created_at TEXT NOT NULL
                DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
        CREATE INDEX IF NOT EXISTS rg_evidence_scope
            ON rg_evidence(kind,scope,candidate);
        """)
        row=self.db.execute("SELECT value FROM rg_metadata WHERE key='schema_version'").fetchone()
        if row is not None and int(row[0]) != SCHEMA_VERSION:
            raise ValueError("unsupported evidence schema version")
        self.db.execute("INSERT OR IGNORE INTO rg_metadata(key,value) VALUES('schema_version',?)",
                        (str(SCHEMA_VERSION),))
        self.db.commit()

    def append_in_transaction(self,kind,scope,candidate,payload):
        """Insert without committing; caller owns the surrounding transaction."""
        if kind not in ('type_proof','empirical_failure','validation','search_trial'):
            raise ValueError('unknown evidence kind')
        if not self.db.in_transaction:
            raise RuntimeError('evidence insert requires an active transaction')
        self.db.execute(
            'INSERT INTO rg_evidence(kind,scope,candidate,payload) VALUES(?,?,?,?)',
            (kind,scope,canonical(candidate),canonical(payload)))

    def append(self,kind,scope,candidate,payload):
        """Append a standalone event atomically, retaining the original API."""
        if self.db.in_transaction:
            raise RuntimeError("use append_in_transaction inside an existing transaction")
        with self.db:
            self.db.execute("BEGIN")
            self.append_in_transaction(kind,scope,candidate,payload)

    def prove_type_impossible(self, expression, input_type, required_type,
                              operators=None):
        """Verify a closed AST has an impossible required type.

        A certificate is checked again before pruning. No external proof
        strings or untrusted observations are accepted as logical proofs.
        """
        from .engine import typecheck, unify
        ops=operators or {}
        try:
            inferred=typecheck(expression,input_type,ops)
            unify(inferred,required_type)
        except TypeError as error:
            self.append('type_proof',digest([input_type,required_type,ops]),
                        expression,{'reason':str(error)})
            return True
        return False

    def can_prune(self,expression,input_type,required_type,operators=None):
        """Only a matching recorded proof AND fresh independent typecheck prune."""
        from .engine import typecheck, unify
        ops=operators or {}
        scope=digest([input_type,required_type,ops])
        stored=self.db.execute(
            "SELECT 1 FROM rg_evidence WHERE kind='type_proof' AND scope=? AND candidate=? LIMIT 1",
            (scope,canonical(expression))).fetchone()
        if stored is None:return False
        try:
            unify(typecheck(expression,input_type,ops),required_type)
            return False
        except TypeError:
            return True

    def count(self,kind=None):
        if kind is None:
            return self.db.execute('SELECT COUNT(*) FROM rg_evidence').fetchone()[0]
        return self.db.execute('SELECT COUNT(*) FROM rg_evidence WHERE kind=?',(kind,)).fetchone()[0]
