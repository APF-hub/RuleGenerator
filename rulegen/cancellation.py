"""Cooperative cancellation for synchronous synthesis loops."""

import time

class SynthesisDeadlineExceeded(Exception):
    """Raised when a synthesis run exceeds its monotonic deadline."""

class SynthesisCancelled(Exception):
    """Raised when a caller requests cancellation of a synthesis run."""


def check_cancel(cancel, deadline=None):
    """Accept a threading.Event-like object or a zero-argument predicate."""
    if deadline is not None and time.monotonic() >= deadline:
        raise SynthesisDeadlineExceeded("synthesis deadline exceeded")
    if cancel is None:
        return
    requested = cancel.is_set() if hasattr(cancel, 'is_set') else cancel()
    if requested:
        raise SynthesisCancelled('synthesis cancelled')


def make_deadline(timeout_seconds):
    """Return an absolute monotonic deadline; None disables time limiting."""
    if timeout_seconds is None:
        return None
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int,float)):
        raise ValueError("timeout_seconds must be a finite nonnegative number")
    import math
    if not math.isfinite(timeout_seconds) or timeout_seconds<0:
        raise ValueError("timeout_seconds must be a finite nonnegative number")
    return time.monotonic()+timeout_seconds
