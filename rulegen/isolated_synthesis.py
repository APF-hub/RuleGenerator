"""Opt-in process-isolated functional synthesis (cold search only)."""
import json
import subprocess
import sys

from .process_isolation import IsolatedExecutionError


def synthesize_functional_isolated(rows, *, tier="math", budget=2000,
                                   max_nodes=5, max_generated=10000,
                                   timeout_seconds=10, memory_bytes=None):
    """Enforce wall-clock deadline and optional POSIX address-space ceiling.

    Does not support registry reuse; only JSON-serializable observations.
    """
    if type(budget) is not int or type(max_nodes) is not int or type(max_generated) is not int:
        raise ValueError("limits must be integers")
    if any(not 1<=n<=100000 for n in (budget,max_nodes,max_generated)):
        raise ValueError("limits out of range")
    if tier not in ("math","algebra"):
        raise ValueError("unsupported tier")
    if not isinstance(rows,(list,tuple)) or not 1<=len(rows)<=1000:
        raise ValueError("invalid observations")
    import math
    if (type(timeout_seconds) not in (int,float) or
        not math.isfinite(timeout_seconds) or timeout_seconds<=0):
        raise ValueError("timeout must be finite and positive")
    if memory_bytes is not None and (type(memory_bytes) is not int or memory_bytes<=0):
        raise ValueError("memory_bytes must be positive")
    import os
    if memory_bytes is not None and os.name!="posix":
        raise NotImplementedError("memory limit requires POSIX")
    request={"rows":rows,"tier":tier,"budget":budget,
             "max_nodes":max_nodes,"max_generated":max_generated}
    payload=json.dumps(request,allow_nan=False).encode()
    if len(payload)>1048576:
        raise ValueError("request too large")
    def limit_memory():
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    try:
        completed=subprocess.run([sys.executable,"-m","rulegen.synthesis_worker"],
            input=payload,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=timeout_seconds,check=False,
            preexec_fn=limit_memory if memory_bytes is not None else None)
    except subprocess.TimeoutExpired as exc:
        raise IsolatedExecutionError("isolated synthesis timeout") from exc
    except OSError as exc:
        raise IsolatedExecutionError("failed to launch synthesis worker") from exc
    if completed.returncode!=0:
        raise IsolatedExecutionError("synthesis worker failed (exit "+str(completed.returncode)+")")
    if len(completed.stdout)>1048576:
        raise IsolatedExecutionError("worker response too large")
    try:
        result=json.loads(completed.stdout)
    except (ValueError,UnicodeError) as exc:
        raise IsolatedExecutionError("invalid worker response") from exc
    if not isinstance(result,dict) or type(result.get("checks")) is not int or not 0<=result["checks"]<=budget:
        raise IsolatedExecutionError("invalid worker accounting")
    return result
