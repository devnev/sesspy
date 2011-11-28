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

if __name__ == '__main__':
    unittest.main()
