"""Equal-budget, seeded replay controls (simulated outcomes, not real synthesis)."""
import random, tempfile
from pathlib import Path
from .portfolio import Portfolio

def compare(outcomes,steps=30,seed=17):
    if not outcomes or any(not v for v in outcomes.values()):raise ValueError("missing outcome streams")
    names=sorted(outcomes);results={}
    for policy in ("adaptive","round_robin","random"):
        with tempfile.TemporaryDirectory() as d:
            p=Portfolio(Path(d)/"db")
            for n in names:p.register(n)
            rng=random.Random(seed);idx={n:0 for n in names};cost=gain=0
            for step in range(steps):
                n=(p.select()["direction"] if policy=="adaptive" else
                   names[step%len(names)] if policy=="round_robin" else rng.choice(names))
                c,g,valid=outcomes[n][min(idx[n],len(outcomes[n])-1)]
                idx[n]+=1;p.record(n,c,g,valid)
                cost+=c
                if valid:gain+=g
            results[policy]={"cost":cost,"validated_gain":gain,"allocations":idx}
    return results
