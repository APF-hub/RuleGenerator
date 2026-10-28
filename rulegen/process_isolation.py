"""Opt-in OS process boundary for bounded external computation.

This is a subprocess primitive, not yet wired to synthesis backends.
POSIX memory ceilings are best-effort RLIMIT_AS; Windows is unsupported.
"""
import os
import subprocess
import sys


class IsolatedExecutionError(RuntimeError):
    """A child process failed or exceeded its execution contract."""


def run_isolated(argv, *, timeout_seconds, memory_bytes=None):
    """Run an executable without a shell and return captured stdout.

    The caller must provide a trusted executable and arguments. The child is
    terminated on timeout. Resource ceilings apply only on POSIX systems.
    """
    if not isinstance(argv, (list, tuple)) or not argv or not all(
        isinstance(arg, str) for arg in argv
    ):
        raise ValueError("argv must be a nonempty sequence of strings")
    from .cancellation import make_deadline
    import math
    if (isinstance(timeout_seconds, bool) or
        not isinstance(timeout_seconds, (int, float)) or
        not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
        raise ValueError("timeout_seconds must be finite and positive")
    if memory_bytes is not None:
        if type(memory_bytes) is not int or memory_bytes <= 0:
            raise ValueError("memory_bytes must be a positive integer")
        if os.name != "posix":
            raise NotImplementedError("memory limits require POSIX")
    def limit_memory():
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    try:
        completed = subprocess.run(
            argv, shell=False, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
            preexec_fn=limit_memory if memory_bytes is not None else None,
        )
    except subprocess.TimeoutExpired as exc:
        raise IsolatedExecutionError("execution timeout") from exc
    except OSError as exc:
        raise IsolatedExecutionError("failed to start isolated process") from exc
    if completed.returncode != 0:
        raise IsolatedExecutionError("isolated process failed: exit " +
                                     str(completed.returncode))
    return completed.stdout
