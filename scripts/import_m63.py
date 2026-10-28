#!/usr/bin/env python3
"""Import the exact tested M63 archive into the repository; refuse unsafe paths.

Usage: python scripts/import_m63.py /path/to/rule-discovery-m63.zip
Run from the repository root, then run tests and commit the resulting changes.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib, sys

FILES = [
    "rulegen/__init__.py", "rulegen/engine.py", "rulegen/discovery.py",
    "rulegen/portfolio.py", "rulegen/typedholes.py", "rulegen/benchmark.py",
    "tests/test_m62.py", "tests/test_m63.py", "pyproject.toml"
]
def main(archive):
    root=Path(__file__).resolve().parents[1]
    with ZipFile(archive) as z:
        for rel in FILES:
            entry="rule-discovery-m63/"+rel
            payload=z.read(entry)
            dest=root/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(payload)
            print(hashlib.sha256(payload).hexdigest(),rel)
    print("Imported exact M63 source bytes. Run: python -m unittest discover -s tests -v")
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/import_m63.py M63.zip")
    main(sys.argv[1])
