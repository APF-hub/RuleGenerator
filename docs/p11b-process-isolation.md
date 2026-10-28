# P11b: isolated subprocess baseline

`run_isolated(argv, timeout_seconds=..., memory_bytes=...)` provides an opt-in subprocess boundary for trusted executables. It disables shell invocation and stdin, terminates the direct child on timeout, and applies a POSIX address-space ceiling when requested. Windows memory enforcement is explicitly unsupported.

**Not yet a synthesis sandbox.** The three synthesis backends still execute in-process. This primitive does not yet serialize observations, reopen registries safely, or return structured synthesis results. It does not constrain descendant processes, stdout/stderr volume, filesystem or network access, CPU time, or all forms of memory use. POSIX `RLIMIT_AS` is an address-space limit, not an RSS measurement. Do not run untrusted code through this primitive.

Next: introduce a constrained synthesis worker protocol with validated inputs, read-only registry access, bounded output, process-group termination, and platform-specific enforcement before making any hard isolation claims.
