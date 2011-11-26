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

class Test_ConnectionFactory(unittest.TestCase):

    def test_call_creates_engine(self):
        db_uri = 'sqlite:///'
        c = sqlalchemy.ConnectionFactory(db_uri)
        e = c()
        self.assertEqual(str(e.url), db_uri)

    def test_callable_uri_is_called(self):
        db_uri = 'sqlite:///'
        m = mock.Mock(spec=())
        m.return_value = db_uri
        c = sqlalchemy.ConnectionFactory(m)
        self.assertEqual(m.called, False)
        e = c()
        self.assertEqual(m.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(str(e.url), db_uri)

class Test_DbConnection(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
