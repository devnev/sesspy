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
import threading
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

class Test_SessionFactory(unittest.TestCase):

    def test_calls_factory_and_adapter(self):
        source_factory = mock.Mock(spec=[])
        adapter_factory = mock.Mock(spec=[])

        sf = session.SessionFactory(
            source_factory, adapter_factory,
            opener_factory=None, local_openers=False,
        )
        self.assertEqual(source_factory.called, False)
        self.assertEqual(adapter_factory.called, False)

        for i in range(5):
            source_factory.reset_mock()
            adapter_factory.reset_mock()
            source_instance = mock.Mock(spec=[])
            adapted_instance = mock.Mock(spec=['open', 'commit', 'abort'])
            source_factory.return_value = source_instance
            adapter_factory.return_value = adapted_instance

            s = sf()
            self.assertEqual(source_factory.call_args_list, [
                ((), {}),
            ])
            self.assertEqual(adapter_factory.call_args_list, [
                ((source_instance,), {})
            ])
            self.assertEqual(s.instance_opener, adapted_instance)

    def test_calls_all_factories(self):
        source_factory = mock.Mock(spec=[])
        adapter_factory = mock.Mock(spec=[])
        opener_factory = mock.Mock(spec=[])

        sf = session.SessionFactory(
            source_factory,
            adapter_factory,
            opener_factory,
            local_openers=False,
        )
        self.assertEqual(source_factory.called, False)
        self.assertEqual(adapter_factory.called, False)
        self.assertEqual(opener_factory.called, False)

        for i in range(5):
            source_factory.reset_mock()
            adapter_factory.reset_mock()
            opener_factory.reset_mock()
            source_instance = mock.Mock(spec=[])
            adapted_instance = mock.Mock(spec=['open', 'commit', 'abort'])
            opener_instance = mock.Mock(spec=['open', 'commit', 'abort'])
            source_factory.return_value = source_instance
            adapter_factory.return_value = adapted_instance
            opener_factory.return_value = opener_instance

            s = sf()
            self.assertEqual(source_factory.call_args_list, [
                ((), {}),
            ])
            self.assertEqual(adapter_factory.call_args_list, [
                ((source_instance,), {})
            ])
            self.assertEqual(opener_factory.call_args_list, [
                ((adapted_instance,), {})
            ])
            self.assertEqual(s.instance_opener, opener_instance)

    def test_keeps_local_opener(self):
        source_factory = mock.Mock(spec=[])
        adapter_factory = mock.Mock(spec=[])
        opener_factory = mock.Mock(spec=[])
        source_instance = mock.Mock(spec=[])
        adapted_instance = mock.Mock(spec=['open', 'commit', 'abort'])
        opener_instance = mock.Mock(spec=['open', 'commit', 'abort'])
        source_factory.return_value = source_instance
        adapter_factory.return_value = adapted_instance
        opener_factory.return_value = opener_instance

        sf = session.SessionFactory(
            source_factory,
            adapter_factory,
            opener_factory,
        )
        self.assertEqual(source_factory.called, False)
        self.assertEqual(adapter_factory.called, False)
        self.assertEqual(opener_factory.called, False)

        for i in range(5):
            s = sf()
            self.assertEqual(source_factory.call_count, 1)
            self.assertEqual(adapter_factory.call_count, 1)
            self.assertEqual(opener_factory.call_count, 1)
            self.assertEqual(s.instance_opener, opener_instance)

    def test_kept_opener_is_local(self):
        source_factory = mock.Mock(spec=[])
        adapter_factory = mock.Mock(spec=[])
        opener_factory = mock.Mock(spec=[])
        source_instance = mock.Mock(spec=[])
        adapted_instance = mock.Mock(spec=['open', 'commit', 'abort'])
        opener_instance = mock.Mock(spec=['open', 'commit', 'abort'])
        source_factory.return_value = source_instance
        adapter_factory.return_value = adapted_instance
        opener_factory.return_value = opener_instance

        sf = session.SessionFactory(
            source_factory,
            adapter_factory,
            opener_factory,
        )

        s = sf()
        self.assertEqual(s.instance_opener, opener_instance)

        new_opener = mock.Mock(spec=['open', 'commit', 'abort'])
        opener_factory.return_value = new_opener

        ts = [None]
        def run():
            ts[0] = sf()
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()

        self.assertEqual(source_factory.call_count, 2)
        self.assertEqual(adapter_factory.call_count, 2)
        self.assertEqual(opener_factory.call_count, 2)
        self.assertEqual(ts[0].instance_opener, new_opener)

if __name__ == '__main__':
    unittest.main()
