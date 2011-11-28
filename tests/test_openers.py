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

from __future__ import with_statement

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

    def test_close_aborts_if_open(self):
        instance_opener = mock.Mock()
        instance = mock.Mock(spec=[])
        instance_opener.open.return_value = instance

        opener = openers.CountingOpener(instance_opener)
        self.assertEqual(instance_opener.method_calls, [])

        inst = opener.open()
        self.assertEqual(inst, instance)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        with mock.patch('warnings.warn') as warn:
            opener.close()
            self.assertEqual(instance_opener.method_calls, [
                ('open', (), {}),
                ('abort', (instance,), {}),
            ])
            self.assertEqual(warn.call_count, 1)
            opener.commit(inst)
            self.assertEqual(warn.call_count, 2)

        instance_opener.reset_mock()

        instance2 = mock.Mock(spec=())
        instance_opener.open.return_value = instance2
        inst = opener.open()
        self.assertEqual(inst, instance2)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.commit(inst)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
            ('commit', (instance2,), {}),
        ])

        with mock.patch('warnings.warn') as warn:
            opener.close()
            self.assertEqual(instance_opener.method_calls, [
                ('open', (), {}),
                ('commit', (instance2,), {}),
            ])
            self.assertEqual(warn.called, False)

class Test_LazyCountingOpener(unittest.TestCase):

    def test_reopen_keeps(self):
        instance_opener = mock.Mock()
        instance = mock.Mock(spec=[])
        instance_opener.open.return_value = instance

        opener = openers.LazyCountingOpener(instance_opener)
        self.assertEqual(instance_opener.method_calls, [])

        inst = opener.open()
        self.assertEqual(inst, instance)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.commit(inst)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        inst2 = opener.open()
        self.assertEqual(inst2, instance)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.commit(inst)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

    def test_abort_aborts(self):
        instance_opener = mock.Mock()
        instance = mock.Mock(spec=[])
        instance_opener.open.return_value = instance

        opener = openers.LazyCountingOpener(instance_opener)
        self.assertEqual(instance_opener.method_calls, [])

        inst = opener.open()
        self.assertEqual(inst, instance)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.abort(inst)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
            ('abort', (instance,), {}),
        ])

    def test_close_commits(self):
        instance_opener = mock.Mock()
        instance = mock.Mock(spec=[])
        instance_opener.open.return_value = instance

        opener = openers.LazyCountingOpener(instance_opener)
        self.assertEqual(instance_opener.method_calls, [])

        inst = opener.open()
        self.assertEqual(inst, instance)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.commit(inst)
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
        ])

        opener.close()
        self.assertEqual(instance_opener.method_calls, [
            ('open', (), {}),
            ('commit', (instance,), {}),
        ])

if __name__ == '__main__':
    unittest.main()
