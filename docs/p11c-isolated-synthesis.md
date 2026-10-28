# P11c: isolated functional synthesis baseline

`rulegen.isolated_synthesis.synthesize_functional_isolated` starts a Python subprocess with a validated JSON request and returns a structured synthesis result. It supports **cold functional synthesis only**: no registry path, operator reuse, learned definitions or shared SQLite connection crosses the process boundary. Request size is capped at 1 MiB and limits are validated.

The parent enforces a wall-clock timeout and optionally sets POSIX `RLIMIT_AS` for the worker. This is a trusted-code isolation baseline, not a secure sandbox for hostile programs. Child output is buffered by `subprocess.run` before its size is checked, so output memory is **not** strictly bounded. Descendant processes and external resources are not sandboxed. Worker errors are reported without leaking raw stderr. Future work: bounded streaming output, process-group termination, registry snapshots and backend parity.
