"""Goal-directed typed-hole enumeration for the M60 AST.
Typed holes are checked before candidate execution.
"""
from itertools import product
from m60 import INT, BOOL, var, pair, listof, unify, resolve, infer

def candidates(input_type, goal, max_nodes=5):
    """Generate small well-typed expressions using arg, pair, fst and snd."""
    levels={1:[["arg",0],["const",0],["const",True]]}
    pruned=0
    for size in range(1,max_nodes+1):
        if size>1:
            levels[size]=[]
            for op in ("fst","snd"):
                for e in levels[size-1]:
                    expr=[op,e]
                    try:infer(expr,[input_type])
                    except TypeError:pruned+=1;continue
                    levels[size].append(expr)
            for left in range(1,size-1):
                right=size-1-left
                for a,b in product(levels[left],levels[right]):
                    levels[size].append(["pair",a,b])
        for expr in levels[size]:
            try:unify(infer(expr,[input_type]),goal)
            except TypeError:
                pruned+=1;continue
            yield expr
