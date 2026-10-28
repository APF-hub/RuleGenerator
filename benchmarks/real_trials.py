"""Reproducible M67 held-out synthesis allocation smoke benchmark."""
import json
from rulegen.trials import compare_real

TASKS = [
    ([(1,1),(2,2)],[(3,3),(4,4)]),
    ([(1,2),(2,3)],[(3,4),(4,5)]),
    ([((1,True),(True,1)),((2,False),(False,2))],
     [((3,True),(True,3)),((4,False),(False,4))]),
    ([((True,False),(False,True))],[((False,True),(True,False))]),
]
if __name__ == '__main__':
    result=compare_real(TASKS,directions=(1,3,5),evaluations_per_trial=12,seed=11)
    print(json.dumps(result,indent=2))
