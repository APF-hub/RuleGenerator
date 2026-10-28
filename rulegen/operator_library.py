"""Shared operator lifecycle interface, preserving backend-specific type safety.

Legacy and functional ASTs are deliberately not coerced into one another.
The facade standardizes admission, inspection and retirement, not discovery.
"""
from .engine import Registry
from .functional_registry import FunctionalRegistry

class OperatorLibrary:
    def __init__(self,path,backend="functional",tier="math"):
        if backend=="functional":
            self.registry=FunctionalRegistry(path,tier=tier)
        elif backend=="legacy":
            self.registry=Registry(path)
        else:
            raise ValueError("unknown operator backend")
        self.backend=backend

    def close(self):
        self.registry.close()

    def __enter__(self):
        return self

    def __exit__(self,*_):
        self.close()

    def active(self):
        return self.registry.active()

    def admit(self,name,definition,training,validation,*,tolerance=1e-9):
        """Promote a verified operator using its native AST and type checker.

        Functional definition: {'params','return_type','body'}.
        Legacy definition: {'body','args','out'}.
        """
        if self.backend=="functional":
            candidate={"name":name,"definition":definition,"status":"candidate"}
            return self.registry.promote(candidate,training,validation,tolerance=tolerance)
        if tolerance!=1e-9:
            raise ValueError("legacy backend does not support numeric tolerance")
        return self.registry.admit(name,definition["body"],definition["args"],
                                   definition["out"],training,validation)

    def retire(self,name):
        self.registry.retire(name)

    def status(self,name):
        if self.backend=="functional":
            return self.registry.evidence(name)
        row=self.registry.db.execute(
            "SELECT evidence,status FROM operators WHERE name=?",(name,)
        ).fetchone()
        if row is None:return None
        import json
        return {"evidence":json.loads(row[0]),"status":row[1]}
