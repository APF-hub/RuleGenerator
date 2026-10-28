"""Durable search sessions for deterministic typed-hole enumeration.

A cursor counts candidates, not evaluation attempts. Replay reconstructs the
iterator; this saves executions, not enumeration time. Grammar/observations
are included in the identity so an altered library cannot reuse a cursor.
"""
import json
from .engine import PRIMS, encode, execute, hash_of, typ
from .typedholes import enumerate_goal


def synthesize_resumable(registry, rows, *, max_nodes=5, budget=100, reuse=True):
    if not rows:
        raise ValueError('observations required')
    if budget < 0:
        raise ValueError('budget must be nonnegative')
    ops = registry.active() if reuse else {}
    identity = hash_of(['session-v1', rows, max_nodes, reuse,
                        [(n, PRIMS[n][0], PRIMS[n][1]) for n in sorted(PRIMS)],
                        [(n, ops[n]) for n in sorted(ops)]])
    registry.db.execute('''CREATE TABLE IF NOT EXISTS search_sessions(
        id TEXT PRIMARY KEY, cursor INTEGER NOT NULL, checks INTEGER NOT NULL,
        program TEXT, completed INTEGER NOT NULL DEFAULT 0)''')
    registry.db.execute('INSERT OR IGNORE INTO search_sessions(id,cursor,checks) VALUES(?,0,0)', (identity,))
    registry.db.commit()
    cursor, prior_checks, saved, completed = registry.db.execute(
        'SELECT cursor,checks,program,completed FROM search_sessions WHERE id=?', (identity,)
    ).fetchone()
    if completed:
        return {'program':json.loads(saved) if saved else None, 'checks':0,
                'total_checks':prior_checks, 'cursor':cursor, 'done':True, 'resumed':True}
    stream, stats = enumerate_goal(typ(rows[0][1]),typ(rows[0][0]),ops,max_nodes)
    checks=0
    last_cursor=cursor
    for index, expression in enumerate(stream):
        if index < cursor:
            continue
        if checks >= budget:
            break
        checks+=1
        last_cursor=index+1
        try:
            matched=all(execute(expression,x,ops)==y for x,y in rows)
        except (ValueError,TypeError,IndexError,RecursionError,OverflowError):
            matched=False
        # Atomic cursor + result commit. An interruption can only cause an
        # extra evaluation before the transaction, never skip an unchecked one.
        with registry.db:
            registry.db.execute('UPDATE search_sessions SET cursor=?, checks=?, program=?, completed=? WHERE id=?',
                (index+1,prior_checks+checks,encode(expression) if matched else None,int(matched),identity))
        if matched:
            return {'program':expression,'checks':checks,'total_checks':prior_checks+checks,
                    'cursor':index+1,'done':True,'resumed':cursor>0}
    else:
        with registry.db:
            registry.db.execute('UPDATE search_sessions SET completed=1 WHERE id=?',(identity,))
        return {'program':None,'checks':checks,'total_checks':prior_checks+checks,
                'cursor':last_cursor,'done':True,'resumed':cursor>0}
    return {'program':None,'checks':checks,'total_checks':prior_checks+checks,
            'cursor':last_cursor,'done':False,'resumed':cursor>0}
