"""M74 typed, pure functional core for executable learned programs.

Small first-order evaluator with lexical binding and bounded collection
operators. No Python eval, imports, mutation, IO or arbitrary callbacks in
program documents. Definitions are ASTs, never executable source strings.
"""
import json
import math
from dataclasses import dataclass

def T(name,*args):return (name,*args)
REAL=T("Real"); INT=T("Int"); BOOL=T("Bool")
def LIST(a):return T("List",a)
def FN(a,b):return T("Fn",a,b)

TIERS={
 "algebra":{"+","-","*","/","<","="},
 "math":{"+","-","*","/","<","=","sin","cos","exp","sqrt"},
 "functional":{"+","-","*","/","<","=","sin","cos","exp","sqrt","map","fold"},
}
def strict_equal(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,(list,tuple)):
        return len(a)==len(b) and all(strict_equal(x,y) for x,y in zip(a,b))
    return a==b

def literal_type(x):
    if type(x) is bool:return BOOL
    if type(x) is int:return INT
    if type(x) is float and math.isfinite(x):return REAL
    raise TypeError("unsupported literal")

def assignable(actual,expected):
    return actual==expected or (actual==INT and expected==REAL)

@dataclass(frozen=True)
class Closure:
    name:str
    body:object
    environment:dict

class Core:
    def __init__(self,tier="algebra",definitions=None,max_steps=100000):
        if tier not in TIERS:raise ValueError("unknown vocabulary tier")
        self.tier=tier
        self.definitions={} if definitions is None else dict(definitions)
        self.max_steps=max_steps
    def infer(self,node,environment=None):
        env={} if environment is None else dict(environment)
        if not isinstance(node,dict):raise TypeError("expected AST object")
        op=node.get("op")
        if op=="literal":return literal_type(node["value"])
        if op=="var":return env[node["name"]]
        if op=="let":
            t=self.infer(node["value"],env)
            return self.infer(node["body"],{**env,node["name"]:t})
        if op=="lambda":
            t=tuple(node["type"])
            return FN(t,self.infer(node["body"],{**env,node["name"]:t}))
        if op=="apply":
            fn=self.infer(node["fn"],env);arg=self.infer(node["arg"],env)
            if fn[0]!="Fn" or not assignable(arg,fn[1]):raise TypeError("application mismatch")
            return fn[2]
        if op=="if":
            if self.infer(node["condition"],env)!=BOOL:raise TypeError("condition must be Bool")
            a=self.infer(node["then"],env);b=self.infer(node["else"],env)
            if a==b:return a
            if {a,b}=={INT,REAL}:return REAL
            raise TypeError("branch type mismatch")
        if op=="list":
            elements=node["items"]
            if not elements:raise TypeError("empty list requires explicit type")
            t=self.infer(elements[0],env)
            for element in elements[1:]:
                other=self.infer(element,env)
                if not (assignable(other,t) or assignable(t,other)):raise TypeError("heterogeneous list")
                if other==REAL:t=REAL
            return LIST(t)
        if op=="call":
            name=node["name"];args=[self.infer(a,env) for a in node["args"]]
            if name in self.definitions:
                definition=self.definitions[name]
                expected=[tuple(p["type"]) for p in definition["params"]]
                if len(args)!=len(expected) or not all(assignable(a,b) for a,b in zip(args,expected)):
                    raise TypeError("learned operator signature mismatch")
                return tuple(definition["return_type"])
            if name not in TIERS[self.tier]:raise TypeError("primitive unavailable: "+name)
            if name in {"+","-","*","/"}:
                if len(args)!=2 or any(a not in (INT,REAL) for a in args):raise TypeError("numeric arguments required")
                return REAL if name=="/" or REAL in args else INT
            if name=="<":
                if len(args)!=2 or any(a not in (INT,REAL) for a in args):raise TypeError("numeric arguments required")
                return BOOL
            if name=="=":
                if len(args)!=2 or args[0]!=args[1]:raise TypeError("equality type mismatch")
                return BOOL
            if name in {"sin","cos","exp","sqrt"}:
                if len(args)!=1 or args[0] not in (INT,REAL):raise TypeError("numeric argument required")
                return REAL
            if name=="map":
                if len(args)!=2 or args[0][0]!="Fn" or args[1][0]!="List" or not assignable(args[1][1],args[0][1]):
                    raise TypeError("map expects function and list")
                return LIST(args[0][2])
            if name=="fold":
                if len(args)!=3 or args[0][0]!="Fn" or args[0][2][0]!="Fn" or args[2][0]!="List":
                    raise TypeError("fold expects curried binary function, initial value and list")
                if not assignable(args[1],args[0][1]) or not assignable(args[2][1],args[0][2][1]) or not assignable(args[0][2][2],args[1]):
                    raise TypeError("fold signature mismatch")
                return args[1]
        raise TypeError("invalid expression")
    def execute(self,node,environment=None):
        self.infer(node,{k:self._runtime_type(v) for k,v in (environment or {}).items()})
        steps=[0]
        def run(n,env):
            steps[0]+=1
            if steps[0]>self.max_steps:raise RuntimeError("evaluation step limit")
            op=n["op"]
            if op=="literal":return n["value"]
            if op=="var":return env[n["name"]]
            if op=="let":
                v=run(n["value"],env);return run(n["body"],{**env,n["name"]:v})
            if op=="lambda":return Closure(n["name"],n["body"],env.copy())
            if op=="apply":return apply(run(n["fn"],env),run(n["arg"],env))
            if op=="if":return run(n["then"] if run(n["condition"],env) else n["else"],env)
            if op=="list":return [run(x,env) for x in n["items"]]
            if op=="call":
                name=n["name"];args=[run(x,env) for x in n["args"]]
                if name in self.definitions:
                    definition=self.definitions[name]
                    params=definition["params"]
                    if len(params)!=len(args):raise TypeError("arity")
                    return run(definition["body"],dict(zip((p["name"] for p in params),args)))
                if name=="+":return args[0]+args[1]
                if name=="-":return args[0]-args[1]
                if name=="*":return args[0]*args[1]
                if name=="/":return args[0]/args[1]
                if name=="<":return args[0]<args[1]
                if name=="=":return strict_equal(*args)
                if name=="sin":return math.sin(args[0])
                if name=="cos":return math.cos(args[0])
                if name=="exp":return math.exp(args[0])
                if name=="sqrt":return math.sqrt(args[0])
                if name=="map":return [apply(args[0],x) for x in args[1]]
                if name=="fold":
                    acc=args[1]
                    for x in args[2]:acc=apply(apply(args[0],acc),x)
                    return acc
            raise ValueError("invalid program")
        def apply(fn,arg):
            if not isinstance(fn,Closure):raise TypeError("not a function")
            return run(fn.body,{**fn.environment,fn.name:arg})
        return run(node,dict(environment or {}))
    def _runtime_type(self,value):
        if isinstance(value,list):
            if not value:raise TypeError("cannot infer empty list type")
            t=self._runtime_type(value[0])
            if any(self._runtime_type(v)!=t for v in value[1:]):raise TypeError("heterogeneous list")
            return LIST(t)
        return literal_type(value)
    def validate_definition(self,name,definition):
        if name in TIERS["functional"] or name in self.definitions:raise ValueError("operator name reserved")
        params=definition["params"]
        if len({p["name"] for p in params})!=len(params):raise ValueError("duplicate parameter")
        signature={p["name"]:tuple(p["type"]) for p in params}
        if self.infer(definition["body"],signature)!=tuple(definition["return_type"]):
            raise TypeError("operator result type mismatch")
        self.definitions[name]=json.loads(json.dumps(definition))
