# -*- coding: utf-8 -*-
#
# Copyright 2011 Mark Nevill
# This file is part of sesspy.
# 
# sesspy is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# sesspy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with sesspy.  If not, see <http://www.gnu.org/licenses/>.

if __name__ == '__main__':
    import sys
    import os, os.path
    sys.path.insert(
        0,
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(
                    os.path.abspath(__file__)
                )
            )
        )
    )

import unittest
import mock
from sesspy import openers

class Test_FunctionOpener(unittest.TestCase):
    def test_openonly(self):
        open = mock.Mock()
        inst = mock.Mock()
        open.return_value = inst
        opener = openers.FunctionOpener(open)

        self.assertEqual(opener.open(), inst)
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.call_args, ((), {}))
        self.assertEqual(inst.method_calls, [])

        opener.commit(inst)
        opener.abort(inst)
        self.assertEqual(inst.call_count, 0)
        self.assertEqual(inst.method_calls, [])
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.method_calls, [])

    def test_opencommit(self):
        open = mock.Mock()
        inst = mock.Mock()
        commit = mock.Mock()
        abort = mock.Mock()
        open.return_value = inst
        opener = openers.FunctionOpener(open, commit, abort)

        self.assertEqual(opener.open(), inst)
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.call_args, ((), {}))
        self.assertEqual(open.method_calls, [])

        opener.commit(inst)
        self.assertEqual(commit.call_count, 1)
        self.assertEqual(commit.call_args, ((inst,), {}))
        self.assertEqual(commit.method_calls, [])
        self.assertEqual(abort.call_count, 0)
        self.assertEqual(abort.method_calls, [])
        self.assertEqual(inst.call_count, 0)
        self.assertEqual(inst.method_calls, [])
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.method_calls, [])

    def test_openabort(self):
        open = mock.Mock()
        inst = mock.Mock()
        commit = mock.Mock()
        abort = mock.Mock()
        open.return_value = inst
        opener = openers.FunctionOpener(open, commit, abort)

        self.assertEqual(opener.open(), inst)
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.call_args, ((), {}))
        self.assertEqual(open.method_calls, [])

        opener.abort(inst)
        self.assertEqual(abort.call_count, 1)
        self.assertEqual(abort.call_args, ((inst,), {}))
        self.assertEqual(abort.method_calls, [])
        self.assertEqual(commit.call_count, 0)
        self.assertEqual(commit.method_calls, [])
        self.assertEqual(inst.call_count, 0)
        self.assertEqual(inst.method_calls, [])
        self.assertEqual(open.call_count, 1)
        self.assertEqual(open.method_calls, [])

class Test_CountingOpener(unittest.TestCase):

    def test_oc(self):
        self.buildtest_semiopen_endclosed('oc', 'oc')

    def test_oa(self):
        self.buildtest_semiopen_endclosed('oa', 'oa')

    def test_oocc(self):
        self.buildtest_semiopen_endclosed('oocc', 'oc')

    def test_ooaa(self):
        self.buildtest_semiopen_endclosed('ooaa', 'oa')

    def test_ooac(self):
        self.buildtest_semiopen_endclosed('ooac', 'oc')

    def test_ooca(self):
        self.buildtest_semiopen_endclosed('ooca', 'oa')

    def test_ooccoc(self):
        self.buildtest_semiopen_endclosed('ooccoc', 'ococ')

    def test_ooccoa(self):
        self.buildtest_semiopen_endclosed('ooccoa', 'ocoa')

    def buildtest_semiopen_endclosed(self, combination, expect=None):
        count = 0
        for x in combination:
            assert x in ('o', 'a', 'c')
            if x == 'o':
                count += 1
            else:
                count -= 1
                assert count >= 0, "combination is not semi-open"
        assert count == 0, "combination does not end closed"

        instance_opener = mock.Mock()
        instance = mock.Mock()
        instance_opener.open.return_value = instance
        method_calls = []

        opener = openers.CountingOpener(instance_opener)
        self.assertEqual(instance_opener.method_calls, method_calls)

        count = 0
        for x in combination:
            if x == 'o':
                if count == 0:
                    method_calls.append(('open', (), {}))
                count += 1
                self.assertEqual(opener.open(), instance)
            elif x == 'c':
                opener.commit(instance)
                count -= 1
                if count == 0:
                    method_calls.append(('commit', (instance,), {}))
            elif x == 'a':
                opener.abort(instance)
                count -= 1
                if count == 0:
                    method_calls.append(('abort', (instance,), {}))
            self.assertEqual(instance_opener.method_calls, method_calls)

        self.assertEqual(instance.call_count, 0)
        self.assertEqual(instance.method_calls, [])

        if expect is not None:
            expect = list(map(dict(o='open',c='commit',a='abort').get, expect))
            calls = [m[0] for m in instance_opener.method_calls]
            self.assertEqual(expect, calls)

if __name__ == '__main__':
    unittest.main()
