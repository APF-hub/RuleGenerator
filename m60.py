"""M60: small executable polymorphic operator registry.
The fuller M60 research prototype and tests are distributed in the M60 archive.
"""
import json, sqlite3

def ctor(name,*args):return ("ctor",name,*args)
def var(name):return ("var",name)
INT=ctor("Int"); BOOL=ctor("Bool")
def pair(a,b):return ctor("Pair",a,b)
def listof(a):return ctor("List",a)

def resolve(t,subst):
    if t[0]=="var" and t[1] in subst:return resolve(subst[t[1]],subst)
    return t if t[0]=="var" else ctor(t[1],*(resolve(x,subst) for x in t[2:]))

def unify(a,b,subst=None):
    s={} if subst is None else dict(subst)
    def contains(v,t):
        t=resolve(t,s)
        return t==v if t[0]=="var" else any(contains(v,x) for x in t[2:])
    def go(a,b):
        a=resolve(a,s);b=resolve(b,s)
        if a==b:return
        if a[0]=="var":
            if contains(a,b):raise TypeError("occurs check")
            s[a[1]]=b;return
        if b[0]=="var":go(b,a);return
        if a[1]!=b[1] or len(a)!=len(b):raise TypeError("mismatch")
        for x,y in zip(a[2:],b[2:]):go(x,y)
    go(a,b)
    return s

def value_type(x):
    if type(x)==bool:return BOOL
    if type(x)==int:return INT
    if isinstance(x,tuple) and len(x)==2:return pair(value_type(x[0]),value_type(x[1]))
    if isinstance(x,list):
        if not x:return listof(var("empty"))
        t=value_type(x[0]);s={}
        for v in x[1:]:s=unify(t,value_type(v),s)
        return listof(resolve(t,s))
    raise TypeError("unsupported observation")

def evaluate(body,args):
    tag=body[0]
    if tag=="arg":return args[body[1]]
    if tag=="const":return body[1]
    if tag=="pair":return (evaluate(body[1],args),evaluate(body[2],args))
    if tag=="fst":return evaluate(body[1],args)[0]
    if tag=="snd":return evaluate(body[1],args)[1]
    raise ValueError("unsupported AST")

def infer(body,arg_types):
    tag=body[0]
    if tag=="arg":return arg_types[body[1]]
    if tag=="const":return value_type(body[1])
    if tag=="pair":return pair(infer(body[1],arg_types),infer(body[2],arg_types))
    if tag in ("fst","snd"):
        t=infer(body[1],arg_types)
        a=var("fresh_left");b=var("fresh_right")
        s=unify(t,pair(a,b))
        return resolve(a if tag=="fst" else b,s)
    raise TypeError("unsupported AST")

class Registry:
    def __init__(self,path):
        self.db=sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS operators(name TEXT PRIMARY KEY, body TEXT, args TEXT, output TEXT, evidence TEXT, active INTEGER)")
        self.db.commit()
    def admit(self,name,body,arg_types,out_type,training,validation):
        if not training or not validation:raise ValueError("independent observations required")
        unify(infer(body,arg_types),out_type)
        for inputs,expected in training+validation:
            if len(inputs)!=len(arg_types):return False
            s={}
            for v,t in zip(inputs,arg_types):s=unify(resolve(t,s),value_type(v),s)
            unify(resolve(out_type,s),value_type(expected),s)
            if evaluate(body,inputs)!=expected:return False
        evidence=json.dumps({"train":len(training),"validation":len(validation)})
        self.db.execute("INSERT INTO operators VALUES(?,?,?,?,?,1)",(name,json.dumps(body),json.dumps(arg_types),json.dumps(out_type),evidence))
        self.db.commit()
        return True
    def call(self,name,*args):
        row=self.db.execute("SELECT body,args,output FROM operators WHERE name=? AND active=1",(name,)).fetchone()
        if not row:raise KeyError(name)
        body,arg_types,out_type=json.loads(row[0]),json.loads(row[1]),json.loads(row[2])
        s={}
        if len(args)!=len(arg_types):raise TypeError("arity")
        for x,t in zip(args,arg_types):s=unify(resolve(t,s),value_type(x),s)
        result=evaluate(body,args)
        unify(resolve(out_type,s),value_type(result))
        return result
    def retire(self,name):
        self.db.execute("UPDATE operators SET active=0 WHERE name=?",(name,));self.db.commit()
