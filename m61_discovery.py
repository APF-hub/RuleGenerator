"""M61 standalone discovery layer for the compact M60 GitHub registry.
Searches executable bodies from observations, then validates a polymorphic type.
"""
from itertools import product
from m60 import Registry, var, pair, value_type, infer, evaluate, unify, strict_equal

def shape(t, counter=None):
    counter = [0] if counter is None else counter
    if t[0] == "ctor" and t[1] in ("Pair", "List", "Fn"):
        return ("ctor",t[1],*(shape(x,counter) for x in t[2:]))
    counter[0]+=1
    return var("t"+str(counter[0]))

def discover(registry, name, training, validation, max_nodes=5):
    if not training or not validation: raise ValueError("need separate splits")
    if set(map(repr,training)) & set(map(repr,validation)):
        raise ValueError("overlapping observations")
    input_type=shape(value_type(training[0][0]))
    pool={1:[["arg",0]]}
    checks=pruned=0
    for n in range(1,max_nodes+1):
        if n>1:
            pool[n]=[]
            for op,arity in (("fst",1),("snd",1),("pair",2)):
                for sizes in product(range(1,n),repeat=arity):
                    if sum(sizes)!=n-1: continue
                    for children in product(*(pool[s] for s in sizes)):
                        expression=[op,*children]
                        try: infer(expression,[input_type])
                        except (TypeError,IndexError):pruned+=1;continue
                        pool[n].append(expression)
        for body in pool[n]:
            try:
                output_type=infer(body,[input_type])
            except (TypeError,IndexError):
                pruned+=1;continue
            checks+=1
            try:
                if not all(strict_equal(evaluate(body,[x]),y) for x,y in training):continue
                accepted=registry.admit(name,body,[input_type],output_type,
                    [([x],y) for x,y in training],
                    [([x],y) for x,y in validation])
            except (TypeError,ValueError,IndexError):
                accepted=False
            if accepted:
                return {"admitted":True,"body":body,"signature":[input_type,output_type],
                        "checks":checks,"type_pruned":pruned}
    return {"admitted":False,"checks":checks,"type_pruned":pruned}

def benchmark(path):
    r=Registry(path)
    result=discover(r,"swap",
        [((1,True),(True,1)),((2,False),(False,2))],
        [(([1,2],False),(False,[1,2]))])
    if result["admitted"]:
        result["held_out"]=r.call("swap",False,[3,4])==([3,4],False)
    return result

if __name__=="__main__":
    import json,sys
    print(json.dumps(benchmark(sys.argv[1] if len(sys.argv)>1 else "m61.sqlite3"),indent=2))
