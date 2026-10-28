import os
import sys
import unittest
from rulegen.process_isolation import run_isolated, IsolatedExecutionError

class ProcessIsolationTests(unittest.TestCase):
    def test_success(self):
        output=run_isolated([sys.executable,'-c','print(42)'],timeout_seconds=3)
        self.assertEqual(output.strip(),b'42')
    def test_timeout(self):
        with self.assertRaisesRegex(IsolatedExecutionError,'timeout'):
            run_isolated([sys.executable,'-c','import time;time.sleep(2)'],timeout_seconds=0.05)
    def test_nonzero_exit(self):
        with self.assertRaises(IsolatedExecutionError):
            run_isolated([sys.executable,'-c','raise SystemExit(7)'],timeout_seconds=3)
    def test_invalid_contract(self):
        for args in ([],['echo',42]):
            with self.assertRaises(ValueError):
                run_isolated(args,timeout_seconds=1)
        for timeout in (0,-1,float('nan'),True):
            with self.assertRaises(ValueError):
                run_isolated([sys.executable],timeout_seconds=timeout)
    @unittest.skipUnless(os.name=='posix','POSIX only')
    def test_memory_limit(self):
        with self.assertRaises(IsolatedExecutionError):
            run_isolated([sys.executable,'-c','x=bytearray(200*1024*1024)'],timeout_seconds=3,memory_bytes=64*1024*1024)
