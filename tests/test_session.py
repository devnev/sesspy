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
from sesspy import session

class Test_Session(unittest.TestCase):
    def setUp(self):
        self.opener = mock.Mock(spec=['open', 'commit', 'abort'])
        self.opener.open = mock.Mock()
        self.opener.commit = mock.Mock()
        self.opener.abort = mock.Mock()

    def tearDown(self):
        del self.opener

    def test_init(self):
        s = session.Session(self.opener)
        self.assertEqual(self.opener.open.called, False)
        self.assertEqual(self.opener.commit.called, False)
        self.assertEqual(self.opener.abort.called, False)

    def test_opencommit(self):
        inst = mock.Mock()
        self.opener.open.return_value = inst
        s = session.Session(self.opener)

        i = s.open()
        self.assertEqual(i, inst)
        self.assertEqual(self.opener.open.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(self.opener.commit.called, False)
        self.assertEqual(self.opener.abort.called, False)

        s.commit()
        self.assertEqual(self.opener.open.call_count, 1)
        self.assertEqual(self.opener.commit.call_args_list, [
            ((inst,), {}),
        ])
        self.assertEqual(self.opener.abort.called, False)

    def test_openabort(self):
        inst = mock.Mock()
        self.opener.open.return_value = inst
        s = session.Session(self.opener)

        i = s.open()
        self.assertEqual(i, inst)
        self.assertEqual(self.opener.open.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(self.opener.commit.called, False)
        self.assertEqual(self.opener.abort.called, False)

        s.abort()
        self.assertEqual(self.opener.open.call_count, 1)
        self.assertEqual(self.opener.commit.called, False)
        self.assertEqual(self.opener.abort.call_args_list, [
            ((inst,), {}),
        ])

    def test_guard_noerror(self):
        inst = mock.Mock()
        self.opener.open.return_value = inst
        s = session.Session(self.opener)

        with s as i:
            self.assertEqual(i, inst)
            self.assertEqual(self.opener.open.call_args_list, [
                ((), {}),
            ])
            self.assertEqual(self.opener.commit.called, False)
            self.assertEqual(self.opener.abort.called, False)

        self.assertEqual(self.opener.open.call_count, 1)
        self.assertEqual(self.opener.commit.call_args_list, [
            ((inst,), {}),
        ])
        self.assertEqual(self.opener.abort.called, False)

    def test_guard_exception(self):
        class TestException(Exception):
            pass
        inst = mock.Mock()
        self.opener.open.return_value = inst
        s = session.Session(self.opener)

        try:
            with s as i:
                self.assertEqual(i, inst)
                self.assertEqual(self.opener.open.call_args_list, [
                    ((), {}),
                ])
                self.assertEqual(self.opener.commit.called, False)
                self.assertEqual(self.opener.abort.called, False)
                raise TestException()
        except TestException:
            pass

        self.assertEqual(self.opener.open.call_count, 1)
        self.assertEqual(self.opener.commit.called, False)
        self.assertEqual(self.opener.abort.call_args_list, [
            ((inst,), {}),
        ])

class Test_SingletonFactory(unittest.TestCase):

    def test_call_calls_factory_once(self):
        factory = mock.Mock(spec=[])
        resource = mock.Mock(spec=[])
        factory.return_value = resource

        opener_factory = mock.Mock(spec=[])
        opener = mock.Mock(spec=['open', 'commit', 'abort'])
        opener_factory.return_value = opener

        sf = session.SingletonFactory(
            factory,
            instance_opener=opener_factory,
            local_openers=False,
        )
        self.assertEqual(factory.called, False)
        self.assertEqual(opener_factory.called, False)

        for i in range(1, 5):
            opener = mock.Mock(spec=['open', 'commit', 'abort'])
            opener_factory.return_value = opener
            s = sf()
            self.assertEqual(factory.call_args_list, [
                ((), {}),
            ])
            self.assertEqual(opener_factory.call_args_list,
                [((resource,), {})] * i,
            )
            self.assertEqual(s.instance_opener, opener)

    def test_noretry_exception_is_reraised(self):
        class TestException(Exception):
            pass

        factory = mock.Mock(spec=[])
        factory.side_effect = TestException
        resource = mock.Mock(spec=[])
        factory.return_value = resource

        opener_factory = mock.Mock(spec=[])
        opener = mock.Mock(spec=['open', 'commit', 'abort'])
        opener_factory.return_value = opener

        sf = session.SingletonFactory(
            factory,
            instance_opener=opener_factory,
            noretry_exceptions=TestException,
            local_openers=False,
        )
        self.assertEqual(factory.called, False)
        self.assertEqual(opener_factory.called, False)

        for _ in range(5):
            self.assertRaises(TestException, sf)
            self.assertEqual(factory.call_args_list, [
                ((), {}),
            ])
            self.assertEqual(opener_factory.called, False)

if __name__ == '__main__':
    unittest.main()
