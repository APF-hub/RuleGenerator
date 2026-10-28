"""Cooperative cancellation for synchronous synthesis loops."""

class SynthesisCancelled(Exception):
    """Raised when a caller requests cancellation of a synthesis run."""


def check_cancel(cancel):
    """Accept a threading.Event-like object or a zero-argument predicate."""
    if cancel is None:
        return
    requested = cancel.is_set() if hasattr(cancel, 'is_set') else cancel()
    if requested:
        raise SynthesisCancelled('synthesis cancelled')
