from .cancellation import check_cancel, make_deadline
"""M60: polymorphic typed holes, reusable executable operators, persisted evidence.

This deliberately small engine uses a generic typed combinator basis. Learned
operators are executable ASTs, not Python callbacks or hardcoded task labels.
"""
import hashlib
import itertools
import json
import sqlite3
from dataclasses import dataclass


def C(name, *args): return ('ctor', name, *args)
def V(name): return ('var', name)
INT=C('Int'); BOOL=C('Bool')
def PAIR(a,b): return C('Pair',a,b)
def LIST(a): return C('List',a)
def FN(a,b): return C('Fn',a,b)

def substitute(t, s):
    if t[0]=='var':
        if t[1] in s: return substitute(s[t[1]],s)
        return t
    return ('ctor',t[1],*(substitute(a,s) for a in t[2:]))

def occurs(v,t,s):
    t=substitute(t,s)
    return v==t if t[0]=='var' else any(occurs(v,x,s) for x in t[2:])

def unify(a,b,s=None):
    s={} if s is None else dict(s)
    def walk(a,b):
        a=substitute(a,s);b=substitute(b,s)
        if a==b:return
        if a[0]=='var':
            if occurs(a,b,s):raise TypeError('recursive type')
            s[a[1]]=b;return
        if b[0]=='var':walk(b,a);return
        if a[1]!=b[1] or len(a)!=len(b):raise TypeError('type mismatch')
        for x,y in zip(a[2:],b[2:]):walk(x,y)
    walk(a,b)
    return s

def typ(x):
    if type(x)==bool:return BOOL
    if type(x)==int:return INT
    if isinstance(x,tuple) and len(x)==2:return PAIR(typ(x[0]),typ(x[1]))
    if isinstance(x,list):
        if not x:return LIST(V('empty'))
        t=typ(x[0]);s={}
        for y in x[1:]:s=unify(t,typ(y),s)
        return LIST(substitute(t,s))
    raise TypeError('unsupported observation')

def encode(x):return json.dumps(x,separators=(',',':'),sort_keys=True)
def hash_of(x):return hashlib.sha256(encode(x).encode()).hexdigest()

# Type constructors and polymorphic primitive combinators are initial bias;
# no music- or domain-specific operators are supplied.
PRIMS={
    'fst':([PAIR(V('a'),V('b'))],V('a'),lambda p:p[0]),
    'snd':([PAIR(V('a'),V('b'))],V('b'),lambda p:p[1]),
    'pair':([V('a'),V('b')],PAIR(V('a'),V('b')),lambda a,b:(a,b)),
    'cons':([V('a'),LIST(V('a'))],LIST(V('a')),lambda a,b:[a]+b),
    'append':([LIST(V('a')),LIST(V('a'))],LIST(V('a')),lambda a,b:a+b),
    'eq':([V('a'),V('a')],BOOL,lambda a,b:a==b),
    'add':([INT,INT],INT,lambda a,b:a+b),
}

def fresh(sig,token):
    args,out=sig
    def rename(t):
        if t[0]=='var':return V(token+'_'+t[1])
        return C(t[1],*(rename(a) for a in t[2:]))
    return [rename(a) for a in args],rename(out)

def typecheck(expr,input_t,operators=None):
    operators=operators or {}
    counter=itertools.count()
    def infer(e):
        if e[0]=='input':return input_t
        if e[0]=='const':return typ(e[1])
        if e[0]=='call':
            name=e[1]
            if name in PRIMS:
                a,o,_=PRIMS[name];body=None
            elif name in operators:
                entry=operators[name];a,o,body=entry['args'],entry['out'],entry['body']
            else:raise TypeError('unknown operator')
            a,o=fresh((a,o),'q'+str(next(counter)))
            if len(a)!=len(e)-2:raise TypeError('arity mismatch')
            s={}
            for actual,expected in zip(e[2:],a):
                s=unify(substitute(expected,s),substitute(infer(actual),s),s)
            return substitute(o,s)
        raise TypeError('invalid AST')
    return infer(expr)

def execute(expr,x,operators=None,depth=0):
    if depth>64:raise RecursionError('operator expansion limit')
    operators=operators or {}
    if expr[0]=='input':return x
    if expr[0]=='const':return expr[1]
    if expr[0]=='call':
        name=expr[1]
        args=[execute(e,x,operators,depth+1) for e in expr[2:]]
        if name in PRIMS:return PRIMS[name][2](*args)
        if name in operators:
            entry=operators[name]
            # Operator body is expressed over an explicit positional input tuple.
            return execute(entry['body'],tuple(args),operators,depth+1)
    if expr[0]=='arg':return x[expr[1]]
    raise ValueError('invalid AST')

def check_body(expr,args,operators=None):
    """Typecheck an operator body with positional arguments and fresh instantiation."""
    operators=operators or {}
    def walk(e):
        if e[0]=='arg':return args[e[1]]
        if e[0]=='const':return typ(e[1])
        if e[0]=='call':
            name=e[1]
            if name in PRIMS:a,o,_=PRIMS[name]
            else:
                item=operators[name];a,o=item['args'],item['out']
            a,o=fresh((a,o),str(id(e)))
            if len(a)!=len(e)-2:raise TypeError('arity')
            s={}
            for child,t in zip(e[2:],a):s=unify(substitute(t,s),substitute(walk(child),s),s)
            return substitute(o,s)
        raise TypeError('invalid operator body')
    return walk(expr)

class Registry:
    def __init__(self,path):
        self.db=sqlite3.connect(str(path))
        try:
            from .database_lifecycle import inspect_database
            inspect_database(self.db)
        except BaseException:
            self.db.close()
            raise
        try:
            from .evidence import Evidence
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute('''CREATE TABLE IF NOT EXISTS operators(name TEXT PRIMARY KEY, body TEXT, args TEXT, output TEXT, evidence TEXT, status TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS failures(scope TEXT, candidate TEXT, reason TEXT, PRIMARY KEY(scope,candidate))''')
            self.evidence=Evidence(self.db)
            self.db.commit()
        except BaseException:
            self.db.rollback()
            self.db.close()
            raise
    def close(self):
        self.db.close()
    def __del__(self):
        db=getattr(self, "db", None)
        if db is not None:
            try: db.close()
            except sqlite3.Error: pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        self.close()
    def active(self):
        return {n:{'body':json.loads(b),'args':json.loads(a),'out':json.loads(o)}
                for n,b,a,o in self.db.execute("SELECT name,body,args,output FROM operators WHERE status='active'")}
    def admit(self,name,body,arg_types,out_type,training,validation,*,execution_counter=None):
        if not training or not validation:raise ValueError('independent evidence required')
        if name in PRIMS or name in self.active():raise ValueError('duplicate operator name')
        # Type variables in the output must be constrained by inputs, or be
        # justified by a constant-returning implementation.
        inferred=check_body(body,arg_types,self.active())
        # A signature must be justified by the body, not merely unifiable.
        if encode(inferred) != encode(out_type):
            raise TypeError('operator signature exceeds inferred parametric type')
        # Reject signatures with unrelated output variables only when
        # the body cannot justify them by its inferred type.
        for inputs,expected in training+validation:
            if len(inputs)!=len(arg_types):return False
            s={}
            for val,t in zip(inputs,arg_types):s=unify(substitute(t,s),typ(val),s)
            unify(substitute(out_type,s),typ(expected),s)
            if execution_counter is not None:
                execution_counter["attempted"]+=1
            if execute(body,tuple(inputs),self.active())!=expected:return False
        evidence={'train':len(training),'validation':len(validation),'digest':hash_of([training,validation])}
        self.db.execute('INSERT INTO operators VALUES(?,?,?,?,?,?)',
                        (name,encode(body),encode(arg_types),encode(out_type),encode(evidence),'active'))
        self.db.commit();return True
    def retire(self,name):
        self.db.execute("UPDATE operators SET status='retired' WHERE name=?",(name,));self.db.commit()
    def record_failure(self,scope,expr,reason):
        self.db.execute('INSERT OR IGNORE INTO failures VALUES(?,?,?)',(scope,encode(expr),reason));self.db.commit()
    def failed(self,scope,expr):
        return self.db.execute('SELECT 1 FROM failures WHERE scope=? AND candidate=?',(scope,encode(expr))).fetchone() is not None

def synthesize(registry,rows,max_nodes=4,budget=10000,reuse=True,max_generated=10000,cancel=None,timeout_seconds=None,operator_priority=None):
    """Enumerate typed expressions, pruning invalid types before execution."""
    if not rows:raise ValueError('empty observations')
    if any(type(n) is not int or n<1 for n in (max_nodes,budget,max_generated)):
        raise ValueError('positive integer limits required')
    deadline=make_deadline(timeout_seconds)
    check_cancel(cancel,deadline)
    ti=typ(rows[0][0]);to=typ(rows[0][1]);scope=hash_of(rows)
    ops=registry.active() if reuse else {}
    pool={1:[['input']]+[['const',v] for v in (0,1,True,False)]}
    seen=set();checks=0;type_pruned=0;fail_skipped=0
    generated=len(pool[1])
    if generated>max_generated:
        return {'program':None,'checks':0,'type_pruned':0,'failure_skips':0,'exhausted':True}
    def evaluate_candidate(expr):
        nonlocal checks,type_pruned,fail_skipped
        signature=encode(expr)
        if signature in seen:return False
        seen.add(signature)
        try:unify(typecheck(expr,ti,ops),to)
        except TypeError:
            type_pruned+=1
            return False
        if registry.failed(scope,expr):
            fail_skipped+=1
            return False
        if checks>=budget:return None
        checks+=1
        try:valid=all(execute(expr,x,ops)==y for x,y in rows)
        except (TypeError,ValueError,RecursionError,OverflowError):valid=False
        if valid:return True
        registry.record_failure(scope,expr,'observational_mismatch')
        return False

    operator_names=list(PRIMS)+list(ops)
    if operator_priority is not None:
        priority={name:index for index,name in enumerate(operator_priority)}
        operator_names.sort(key=lambda name:(priority.get(name,len(priority)),name))
    for n in range(1,max_nodes+1):
        check_cancel(cancel,deadline)
        if n==1:
            candidates=pool[1]
        else:
            pool[n]=[]
            # Incremental evaluation: do not discard an entire partially
            # generated layer when the generation cap is reached.
            candidates=None
        if candidates is not None:
            for expr in candidates:
                check_cancel(cancel,deadline)
                verdict=evaluate_candidate(expr)
                if verdict is True:
                    return {'program':expr,'checks':checks,'type_pruned':type_pruned,
                            'failure_skips':fail_skipped,'exhausted':False}
                if verdict is None:
                    return {'program':None,'checks':checks,'type_pruned':type_pruned,
                            'failure_skips':fail_skipped,'exhausted':True}
            continue
        for name in operator_names:
            arity=len(PRIMS[name][0]) if name in PRIMS else len(ops[name]['args'])
            for sizes in itertools.product(range(1,n),repeat=arity):
                if sum(sizes)!=n-1:continue
                for args in itertools.product(*(pool[s] for s in sizes)):
                    check_cancel(cancel,deadline)
                    expr=['call',name,*args]
                    try:typecheck(expr,ti,ops)
                    except TypeError:
                        type_pruned+=1
                        continue
                    if generated>=max_generated:
                        return {'program':None,'checks':checks,'type_pruned':type_pruned,
                                'failure_skips':fail_skipped,'exhausted':True}
                    pool[n].append(expr)
                    generated+=1
                    verdict=evaluate_candidate(expr)
                    if verdict is True:
                        return {'program':expr,'checks':checks,'type_pruned':type_pruned,
                                'failure_skips':fail_skipped,'exhausted':False}
                    if verdict is None:
                        return {'program':None,'checks':checks,'type_pruned':type_pruned,
                                'failure_skips':fail_skipped,'exhausted':True}
    return {'program':None,'checks':checks,'type_pruned':type_pruned,'failure_skips':fail_skipped,'exhausted':False}
