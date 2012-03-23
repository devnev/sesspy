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
from sesspy import sqlalchemy

class Test_DbConnection(unittest.TestCase):

    def test_creates_singletonfactory(self):
        connection_factory = mock.Mock(spec=[])
        connection = mock.Mock(spec=[])
        connection_factory.return_value = connection
        engine_args = dict(param=mock.Mock(spec=[]))
        db_uri = '__test_uri'

        component = sqlalchemy.db_connection(
            db_uri, engine_args,
            connection_factory=connection_factory,
        )
        self.assertEqual(connection_factory.called, False)

        sess = component()
        self.assertEqual(connection_factory.call_args_list, [
            ((db_uri,), engine_args),
        ])

        conn = sess.open()
        self.assertEqual(conn, connection)
        self.assertEqual(connection_factory.call_count, 1)

        sess.commit()
        self.assertEqual(connection_factory.call_count, 1)

        conn = sess.open()
        self.assertEqual(conn, connection)
        self.assertEqual(connection_factory.call_count, 1)

        sess.abort()
        self.assertEqual(connection_factory.call_count, 1)

    def test_registers_singletonfactory(self):
        registry = mock.Mock(spec=['register_component'])
        registry.register_component = mock.Mock(spec=[])
        connection_factory = mock.Mock(spec=[])
        connection = mock.Mock(spec=[])
        connection_factory.return_value = connection
        db_uri = '__test_uri'
        component_name = 'component1'

        component = sqlalchemy.db_connection(
            db_uri, name=component_name, registry=registry,
            connection_factory=connection_factory,
        )
        self.assertEqual(connection_factory.called, False)
        self.assertEqual(registry.register_component.call_args_list, [
            ((component_name, component), {}),
        ])

    def test_calls_engine_args(self):
        connection_factory = mock.Mock(spec=[])
        connection = mock.Mock(spec=[])
        connection_factory.return_value = connection
        db_uri = mock.Mock(spec=[])
        db_uri_result = '__test_uri'
        db_uri.return_value = db_uri_result
        engine_args = mock.Mock(spec=[])
        engine_args_result = dict(param=mock.Mock(spec=[]))
        engine_args.return_value = engine_args_result

        component = sqlalchemy.db_connection(
            db_uri, engine_args,
            connection_factory=connection_factory,
        )
        self.assertEqual(connection_factory.called, False)

        sess = component()
        self.assertEqual(connection_factory.call_args_list, [
            ((db_uri_result,), engine_args_result),
        ])
        self.assertEqual(db_uri.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(engine_args.call_args_list, [
            ((), {}),
        ])

    def test_calls_factory_with_empty_engine_args(self):
        connection_factory = mock.Mock(spec=[])
        connection = mock.Mock(spec=[])
        connection_factory.return_value = connection
        db_uri = '__test_uri'

        component = sqlalchemy.db_connection(
            db_uri, connection_factory=connection_factory,
        )
        self.assertEqual(connection_factory.called, False)

        sess = component()
        self.assertEqual(connection_factory.call_args_list, [
            ((db_uri,), {}),
        ])

class Test_Transactions(unittest.TestCase):

    def setUp(self):
        self.transaction = mock.Mock(spec=['commit', 'rollback'])
        self.connection = mock.Mock(spec=['begin', 'close'])
        self.connection.begin.return_value = self.transaction
        self.engine = mock.Mock(spec=['connect'])
        self.engine.connect.return_value = self.connection
        self.engine_factory = mock.Mock(spec=[])
        self.engine_factory.return_value = self.engine
        self.db_uri = '__test_uri'
        self.component = sqlalchemy.transactional_db_connection(
            self.db_uri, connection_factory=self.engine_factory,
        )

    def test_connection_is_opened(self):
        self.assertEqual(self.engine_factory.called, False)

        sess = self.component()
        self.assertEqual(self.engine_factory.call_count, 1)
        self.assertEqual(self.engine.called, False)
        self.assertEqual(self.engine.connect.called, False)

    def test_transaction_is_begun(self):
        sess = self.component()
        conn = sess.open()
        self.assertEqual(self.engine.connect.call_count, 1)
        self.assertEqual(self.connection.called, False)
        self.assertEqual(self.connection.begin.call_count, 1)
        self.assertEqual(self.connection.close.called, False)
        self.assertEqual(self.transaction.called, False)
        self.assertEqual(self.transaction.commit.called, False)
        self.assertEqual(self.transaction.rollback.called, False)

    def test_transaction_is_committed(self):
        sess = self.component()
        conn = sess.open()
        sess.commit()
        self.assertEqual(self.connection.close.call_count, 1)
        self.assertEqual(self.transaction.called, False)
        self.assertEqual(self.transaction.commit.call_count, 1)
        self.assertEqual(self.transaction.rollback.called, False)

    def test_transaction_is_aborted(self):
        sess = self.component()
        conn = sess.open()
        sess.abort()
        self.assertEqual(self.transaction.commit.called, False)
        self.assertEqual(self.transaction.rollback.call_count, 1)
        self.assertEqual(self.connection.close.call_count, 1)

    def test_recursive_session_is_opened_once(self):
        sess1 = self.component()
        conn1 = sess1.open()
        sess2 = self.component()
        conn2 = sess2.open()
        self.assertEqual(self.engine.connect.call_count, 1)
        self.assertEqual(self.connection.begin.call_count, 1)
        self.assertEqual(self.connection.close.called, False)
        self.assertEqual(self.transaction.commit.called, False)
        self.assertEqual(self.transaction.rollback.called, False)

    def test_recursive_session_is_closed_once(self):
        sess1 = self.component()
        conn1 = sess1.open()
        sess2 = self.component()
        conn2 = sess2.open()

        sess2.commit()
        self.assertEqual(self.connection.close.called, False)
        self.assertEqual(self.transaction.commit.called, False)
        self.assertEqual(self.transaction.rollback.called, False)

        sess1.commit()
        self.assertEqual(self.connection.close.call_count, 1)
        self.assertEqual(self.transaction.commit.call_count, 1)
        self.assertEqual(self.transaction.rollback.called, False)

if __name__ == '__main__':
    unittest.main()
