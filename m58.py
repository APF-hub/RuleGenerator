"""M58: persistent, scoped nogood learning for finite constraint problems.

Each clause is an OR of equality literals (variable index, allowed value).
No learned nogood is used outside its exact problem fingerprint.
"""
import hashlib, json, sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS nogoods (problem TEXT, assignment TEXT, PRIMARY KEY(problem,assignment));
CREATE TABLE IF NOT EXISTS sessions (name TEXT PRIMARY KEY, problem TEXT, frontier TEXT, solution TEXT, visits INTEGER);
CREATE TABLE IF NOT EXISTS policy (context TEXT, variable INTEGER, value INTEGER, success INTEGER DEFAULT 0, failure INTEGER DEFAULT 0, PRIMARY KEY(context,variable,value));
"""

def encode(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))

def fingerprint(x):
    return hashlib.sha256(encode(x).encode()).hexdigest()

def solve(db_path, domains, clauses, budget=1000, session="default", learn=True):
    """Return best found solution and a persistent checkpoint, using at most budget node visits."""
    if budget < 0: raise ValueError("negative budget")
    domains = [sorted(set(d)) for d in domains]
    clauses = sorted(set(tuple(sorted((int(i), int(v)) for i,v in clause)) for clause in clauses))
    for clause in clauses:
        for i,v in clause:
            if i < 0 or i >= len(domains) or v not in domains[i]:
                raise ValueError("invalid clause literal")
    problem = fingerprint([domains,clauses])
    context = fingerprint([domains,len(domains)])
    db = sqlite3.connect(str(db_path))
    db.executescript(DDL)
    row = db.execute("SELECT problem,frontier,solution,visits FROM sessions WHERE name=?", (session,)).fetchone()
    if row and row[0] != problem: raise ValueError("session belongs to another problem")
    frontier = json.loads(row[1]) if row else [[]]
    solution = json.loads(row[2]) if row and row[2] != "null" else None
    total = row[3] if row else 0
    checks = skips = added = 0
    while frontier and checks < budget and solution is None:
        pairs = frontier.pop()
        partial = dict(pairs)
        if learn:
            known = db.execute("SELECT assignment FROM nogoods WHERE problem=?", (problem,)).fetchall()
            if any(all(partial.get(i) == v for i,v in json.loads(a)) for (a,) in known):
                skips += 1
                continue
        checks += 1
        total += 1
        violated = next((cl for cl in clauses if all(i in partial and partial[i] != v for i,v in cl)), None)
        if violated is not None:
            explanation = sorted((i,partial[i]) for i,v in violated)
            if learn:
                added += db.execute("INSERT OR IGNORE INTO nogoods VALUES(?,?)", (problem,encode(explanation))).rowcount
            for i,v in pairs:
                db.execute("""INSERT INTO policy(context,variable,value,failure) VALUES(?,?,?,1)
                  ON CONFLICT(context,variable,value) DO UPDATE SET failure=failure+1""", (context,i,v))
            continue
        if len(partial) == len(domains):
            solution = pairs
            for i,v in pairs:
                db.execute("""INSERT INTO policy(context,variable,value,success) VALUES(?,?,?,1)
                  ON CONFLICT(context,variable,value) DO UPDATE SET success=success+1""", (context,i,v))
            break
        i = next(i for i in range(len(domains)) if i not in partial)
        counts = db.execute("SELECT value,success,failure FROM policy WHERE context=? AND variable=?", (context,i)).fetchall()
        score = {v:(s+1)/(s+f+2) for v,s,f in counts}
        values = sorted(domains[i], key=lambda v:(-score.get(v,0.5),v))
        frontier.extend([sorted(pairs+[[i,v]]) for v in reversed(values)])
    db.execute("INSERT OR REPLACE INTO sessions VALUES(?,?,?,?,?)",
               (session,problem,encode(frontier),encode(solution),total))
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM nogoods WHERE problem=?", (problem,)).fetchone()[0]
    db.close()
    return {"solution":dict(solution) if solution is not None else None,
            "complete":solution is not None or not frontier, "visits_this_call":checks,
            "visits_total":total, "pruned":skips, "new_nogoods":added,
            "stored_nogoods":count, "frontier_size":len(frontier)}

if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as directory:
        db = Path(directory)/"knowledge.sqlite"
        domains = [[0,1] for _ in range(7)]
        clauses = [[(0,1),(1,0)],[(1,1)]]
        print(solve(db,domains,clauses,budget=2))
        print(solve(db,domains,clauses,budget=100))
