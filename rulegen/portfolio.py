"""Persistent, auditable experimental allocation without predicted discovery value.

Exploration is scheduled by least allocated compute; exploitation by observed
validation improvement per unit cost. No credit is assigned to hypothetical reuse.
"""
import json
import sqlite3

class Portfolio:
    def __init__(self, path, exploration_every=3):
        if exploration_every < 1:
            raise ValueError('exploration_every must be positive')
        self.db=sqlite3.connect(str(path))
        self.exploration_every=exploration_every
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS directions(name TEXT PRIMARY KEY, spent REAL NOT NULL DEFAULT 0,
            experiments INTEGER NOT NULL DEFAULT 0, observed_gain REAL NOT NULL DEFAULT 0,
            discoveries INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE IF NOT EXISTS outcomes(id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            cost REAL NOT NULL, gain REAL NOT NULL, validated INTEGER NOT NULL,
            metadata TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY, value INTEGER NOT NULL);
        ''')
        self.db.commit()
    def register(self, name):
        self.db.execute('INSERT OR IGNORE INTO directions(name) VALUES(?)',(name,))
        self.db.commit()
    def select(self):
        rows=self.db.execute('SELECT name,spent,experiments,observed_gain FROM directions ORDER BY name').fetchall()
        if not rows: raise ValueError('no registered research directions')
        step=self.db.execute("SELECT value FROM state WHERE key='step'").fetchone()
        step=step[0] if step else 0
        explore=(step % self.exploration_every == 0)
        if explore:
            choice=min(rows,key=lambda x:(x[1],x[2],x[0]))
        else:
            # Unknown directions receive a measured trial rather than a fictional return.
            untried=[r for r in rows if r[2]==0]
            choice=min(untried,key=lambda x:x[0]) if untried else max(rows,key=lambda x:(x[3]/max(x[1],1e-9),-x[1],x[0]))
        self.db.execute("INSERT INTO state(key,value) VALUES('step',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(step+1,))
        self.db.commit()
        return {'direction':choice[0],'mode':'explore' if explore else 'exploit','decision':step}
    def record(self,name,cost,gain,validated=False,metadata=None):
        if cost<=0 or gain<0: raise ValueError('cost must be positive; gain nonnegative')
        if self.db.execute('SELECT 1 FROM directions WHERE name=?',(name,)).fetchone() is None:
            raise KeyError(name)
        # Only independently validated improvement contributes to measured gain.
        accepted=float(gain) if validated else 0.0
        with self.db:
            self.db.execute('UPDATE directions SET spent=spent+?, experiments=experiments+1, observed_gain=observed_gain+?, discoveries=discoveries+? WHERE name=?',
                            (cost,accepted,int(bool(validated)),name))
            self.db.execute('INSERT INTO outcomes(name,cost,gain,validated,metadata) VALUES(?,?,?,?,?)',
                            (name,cost,float(gain),int(bool(validated)),json.dumps(metadata or {},sort_keys=True)))
    def report(self):
        return [dict(zip(('name','spent','experiments','observed_gain','discoveries'),r)) for r in
                self.db.execute('SELECT name,spent,experiments,observed_gain,discoveries FROM directions ORDER BY name')]
