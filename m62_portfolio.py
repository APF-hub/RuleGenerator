"""M62: persistent budget allocation from observed evidence, not predicted future value."""
import sqlite3,json
class Portfolio:
 def __init__(self,path,exploration_every=3):
  if exploration_every<1:raise ValueError("invalid interval")
  self.db=sqlite3.connect(str(path));self.interval=exploration_every
  self.db.executescript("""CREATE TABLE IF NOT EXISTS directions(name TEXT PRIMARY KEY,spent REAL DEFAULT 0, trials INTEGER DEFAULT 0, gain REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY, name TEXT, mode TEXT);
CREATE TABLE IF NOT EXISTS outcomes(id INTEGER PRIMARY KEY, name TEXT,cost REAL,gain REAL,validated INTEGER,metadata TEXT);""")
 def register(self,name):
  self.db.execute("INSERT OR IGNORE INTO directions(name) VALUES(?)",(name,));self.db.commit()
 def select(self):
  rows=self.db.execute("SELECT name,spent,trials,gain FROM directions ORDER BY name").fetchall()
  if not rows:raise ValueError("no directions")
  n=self.db.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
  explore=n%self.interval==0
  if explore:chosen=min(rows,key=lambda r:(r[1],r[2],r[0]))
  else:
   untried=[r for r in rows if r[2]==0]
   chosen=min(untried,key=lambda r:r[0]) if untried else max(rows,key=lambda r:(r[3]/max(r[1],1e-9),-r[1],r[0]))
  mode="explore" if explore else "exploit"
  self.db.execute("INSERT INTO decisions(name,mode) VALUES(?,?)",(chosen[0],mode));self.db.commit()
  return {"direction":chosen[0],"mode":mode}
 def record(self,name,cost,gain,validated=False,metadata=None):
  if cost<=0 or gain<0:raise ValueError("invalid measurements")
  if not self.db.execute("SELECT 1 FROM directions WHERE name=?",(name,)).fetchone():raise KeyError(name)
  with self.db:
   self.db.execute("UPDATE directions SET spent=spent+?,trials=trials+1,gain=gain+? WHERE name=?",(cost,gain if validated else 0,name))
   self.db.execute("INSERT INTO outcomes(name,cost,gain,validated,metadata) VALUES(?,?,?,?,?)",(name,cost,gain,int(bool(validated)),json.dumps(metadata or {})))
 def report(self):
  return [dict(zip(("name","spent","trials","validated_gain"),r)) for r in self.db.execute("SELECT name,spent,trials,gain FROM directions ORDER BY name")]
