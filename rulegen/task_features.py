"""Task features inferred only from input/output observations, never generator AST."""
from .engine import typ, encode


def extract_features(rows):
    if not rows:raise ValueError("nonempty observations required")
    input_type=encode(typ(rows[0][0]))
    output_type=encode(typ(rows[0][1]))
    if any(encode(typ(x))!=input_type or encode(typ(y))!=output_type for x,y in rows):
        raise ValueError("inconsistent observation types")
    features={"input_type":input_type,"output_type":output_type,
              "same_type":input_type==output_type,
              "examples":len(rows)}
    if all(type(x) is int and type(y) is int for x,y in rows):
        deltas=[y-x for x,y in rows]
        features["constant_delta"]=deltas[0] if len(set(deltas))==1 else None
    if all(isinstance(x,tuple) and len(x)==2 and isinstance(y,tuple)
           and len(y)==2 for x,y in rows):
        features["pair_swap_consistent"]=all(y==(x[1],x[0]) for x,y in rows)
        features["pair_identity_consistent"]=all(y==x for x,y in rows)
        features["pair_first_from_second"]=all(y[0]==x[1] for x,y in rows)
        features["pair_second_from_first"]=all(y[1]==x[0] for x,y in rows)
    return features


def suggested_operators(features):
    """Priorities, not hard filters. Every primitive remains available."""
    if features.get("pair_swap_consistent"):
        return ("pair","snd","fst")
    if features.get("constant_delta") is not None:
        return ("add",)
    if features.get("pair_first_from_second") or features.get("pair_second_from_first"):
        return ("pair","fst","snd")
    return ()
