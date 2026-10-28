"""F2-F4: observation-conditioned priorities and bounded experience learning.

The learned policy changes enumeration order, not the candidate vocabulary.
Training labels are from completed search outcomes; held-out tasks are separate.
"""
from collections import defaultdict
from .engine import synthesize
from .task_features import extract_features, suggested_operators


def feature_key(features):
    if features.get("pair_swap_consistent"):return "pair_swap"
    if features.get("constant_delta") is not None:return "constant_delta"
    return features["input_type"]+"->"+features["output_type"]


class ExperiencePolicy:
    def __init__(self):
        self.counts=defaultdict(lambda:defaultdict(lambda:[0,0]))

    def observe(self,features,program,checks):
        if program is None:return
        key=feature_key(features)
        def walk(expr):
            if expr[0]=="call":
                self.counts[key][expr[1]][0]+=1
                self.counts[key][expr[1]][1]+=checks
                for child in expr[2:]:walk(child)
        walk(program)

    def priorities(self,features):
        key=feature_key(features)
        scored=self.counts.get(key,{})
        # More successful uses, then fewer mean checks, then stable name.
        learned=sorted(scored,key=lambda op:(-scored[op][0],
                          scored[op][1]/scored[op][0],op))
        return tuple(dict.fromkeys([*learned,*suggested_operators(features)]))


def guided_synthesize(registry,rows,*,policy=None,mode="feature",**limits):
    features=extract_features(rows)
    if mode=="baseline":priority=None
    elif mode=="feature":priority=suggested_operators(features)
    elif mode=="learned":
        if policy is None:raise ValueError("learned mode requires policy")
        priority=policy.priorities(features)
    else:raise ValueError("unknown mode")
    result=synthesize(registry,rows,operator_priority=priority,**limits)
    if mode=="learned" and result["program"] is not None:
        policy.observe(features,result["program"],result["checks"])
    return dict(result,features=features,mode=mode,operator_priority=priority)
