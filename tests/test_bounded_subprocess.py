import os
import sys
import unittest
from rulegen.bounded_subprocess import run_bounded
from rulegen.process_isolation import IsolatedExecutionError

@unittest.skipUnless(os.name=='posix','POSIX process groups required')
class BoundedSubprocessTests(unittest.TestCase):
    def test_success_and_input(self):
        result=run_bounded([sys.executable,'-c','import sys;print(len(sys.stdin.buffer.read()))'],b'x'*100000,timeout_seconds=3)
        self.assertEqual(result.strip(),b'100000')
    def test_stdout_ceiling(self):
        with self.assertRaisesRegex(IsolatedExecutionError,'output limit'):
            run_bounded([sys.executable,'-c','print("x"*5000)'],b'',timeout_seconds=3,max_output_bytes=128)
    def test_stderr_ceiling(self):
        with self.assertRaisesRegex(IsolatedExecutionError,'output limit'):
            run_bounded([sys.executable,'-c','import sys;sys.stderr.write("x"*5000)'],b'',timeout_seconds=3,max_output_bytes=128)
    def test_timeout(self):
        with self.assertRaisesRegex(IsolatedExecutionError,'timeout'):
            run_bounded([sys.executable,'-c','import time;time.sleep(5)'],b'',timeout_seconds=0.05)
