"""Canonical typed kernel (M64 compatibility layer)."""
from m60 import (Registry, ctor as C, var as V, INT, BOOL, pair as PAIR,
                 listof as LIST, unify, resolve as substitute, value_type as typ,
                 evaluate, infer)
from m61_discovery import discover
