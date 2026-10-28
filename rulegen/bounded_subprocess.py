"""Bounded, timed subprocess communication for trusted worker processes."""
import os
import selectors
import signal
import subprocess
import time

from .process_isolation import IsolatedExecutionError


def run_bounded(argv, payload, *, timeout_seconds, memory_bytes=None,
                max_output_bytes=1048576):
    """Bound combined stdout/stderr and terminate POSIX process groups.

    Requires POSIX for process-group enforcement. Not a hostile-code sandbox.
    """
    if os.name != "posix":
        raise NotImplementedError("bounded process-group runner requires POSIX")
    if type(max_output_bytes) is not int or max_output_bytes<1:
        raise ValueError("positive output limit required")
    def limits():
        if memory_bytes is not None:
            import resource
            resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    try:
        proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,start_new_session=True,
                              preexec_fn=limits if memory_bytes is not None else None)
    except OSError as exc:
        raise IsolatedExecutionError("failed to launch isolated worker") from exc
    def kill_group():
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    sel=selectors.DefaultSelector()
    output=bytearray()
    try:
        # The request is capped at 1 MiB. Write it before collecting output;
        # this is safe for the current worker, which reads all stdin first.
        proc.stdin.write(payload)
        proc.stdin.close()
        for pipe in (proc.stdout,proc.stderr):
            os.set_blocking(pipe.fileno(),False)
            sel.register(pipe,selectors.EVENT_READ)
        deadline=time.monotonic()+timeout_seconds
        while sel.get_map():
            remaining=deadline-time.monotonic()
            if remaining<=0:
                raise IsolatedExecutionError("isolated synthesis timeout")
            events=sel.select(min(remaining,0.1))
            for key,_ in events:
                chunk=os.read(key.fileobj.fileno(),min(65536,max_output_bytes+1-len(output)))
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                output.extend(chunk)
                if len(output)>max_output_bytes:
                    raise IsolatedExecutionError("worker output limit exceeded")
        remaining=deadline-time.monotonic()
        if remaining<=0:
            raise IsolatedExecutionError("isolated synthesis timeout")
        try:code=proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise IsolatedExecutionError("isolated synthesis timeout") from exc
        if code!=0:
            raise IsolatedExecutionError("synthesis worker failed (exit "+str(code)+")")
        return bytes(output)
    except BaseException:
        kill_group()
        proc.wait()
        raise
    finally:
        sel.close()
        for pipe in (proc.stdout,proc.stderr):
            pipe.close()
