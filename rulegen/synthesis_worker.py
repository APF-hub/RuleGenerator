"""JSON-lines worker for isolated functional synthesis without registry reuse.

Input is a single JSON object on stdin. This protocol deliberately excludes
registry paths and learned operators until read-only registry access is designed.
"""
import json
import sys
from .functional_synthesis import synthesize_functional
from .functional import Core, TIERS


def main():
    try:
        request=json.loads(sys.stdin.buffer.read(1048577))
        if not isinstance(request,dict) or set(request)!={"rows","budget","max_nodes","max_generated","tier","definitions"}:
            raise ValueError("invalid request fields")
        rows=request["rows"]
        if not isinstance(rows,list) or not rows or len(rows)>1000:
            raise ValueError("invalid observations")
        observations=[]
        for row in rows:
            if not isinstance(row,list) or len(row)!=2 or not isinstance(row[0],dict):
                raise ValueError("invalid observation")
            observations.append((row[0],row[1]))
        for key in ("budget","max_nodes","max_generated"):
            if type(request[key]) is not int or not 1<=request[key]<=100000:
                raise ValueError("invalid limit")
        if request["tier"] not in TIERS:
            raise ValueError("unsupported tier")
        definitions=request["definitions"]
        if not isinstance(definitions,dict) or len(definitions)>100:
            raise ValueError("invalid definitions")
        core=Core(request["tier"])
        pending=dict(definitions)
        while pending:
            progress=False
            for name,definition in list(pending.items()):
                try:
                    core.validate_definition(name,definition)
                except (TypeError,KeyError):
                    continue
                del pending[name]
                progress=True
            if not progress:
                raise ValueError("invalid or cyclic definitions")
        class Snapshot:
            def core(self):
                return core
        result=synthesize_functional(observations,registry=Snapshot(),tier=request["tier"],
            budget=request["budget"],max_nodes=request["max_nodes"],
            max_generated=request["max_generated"],reuse=True)
        sys.stdout.write(json.dumps(result,allow_nan=False))
    except (ValueError,TypeError,KeyError) as exc:
        sys.stderr.write(type(exc).__name__+": "+str(exc))
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
