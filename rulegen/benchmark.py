"""Deterministic policy comparisons on predeclared experiment outcomes.

Replay is a policy simulator, not empirical evidence that real synthesis improves.
Each direction has an ordered sequence of measured outcomes. No lookahead is used.
"""
from pathlib import Path
import random
import tempfile
from .portfolio import Portfolio

def compare(outcomes, steps=24, seed=17, exploration_every=3):
    names=sorted(outcomes)
    if not names or any(not outcomes[k] for k in names):raise ValueError('missing outcomes')
    result={}
    for policy in ('adaptive','round_robin','random'):
        with tempfile.TemporaryDirectory() as directory:
            p=Portfolio(Path(directory)/'allocation.sqlite',exploration_every)
            for name in names:p.register(name)
            rng=random.Random(seed);cursor={k:0 for k in names};cost=reward=0.
            for step in range(steps):
                if policy=='adaptive':name=p.select()['direction']
                elif policy=='round_robin':name=names[step%len(names)]
                else:name=rng.choice(names)
                record=outcomes[name][min(cursor[name],len(outcomes[name])-1)]
                cursor[name]+=1
                c,g,validated=record
                p.record(name,c,g,validated)
                cost+=c;reward+=g if validated else 0
            result[policy]={'cost':cost,'validated_gain':reward,'gain_per_cost':reward/cost,
                            'allocations':cursor}
    return result
