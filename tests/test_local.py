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
import threading
from sesspy import local

class Test_Local(unittest.TestCase):
    def test_noattr(self):
        l = local.Local()
        self.assertRaises(AttributeError, lambda: l.a)

    def test_attrset(self):
        l = local.Local()
        l.b = 1
        self.assertEqual(hasattr(l, 'b'), True)
        self.assertEqual(l.b, 1)

    def test_attrset_is_local(self):
        l = local.Local()
        l.b = 1
        exc = [None]
        def run():
            try:
                l.b
            except Exception as e:
                exc[0] = e
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
        exc = exc[0]
        self.assertEqual(type(exc), AttributeError)

    def test_attrval_is_local(self):
        l = local.Local()
        l.t = 42
        def run():
            l.t = 7
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()

        self.assertEqual(l.t, 42)

    def test_attrdict_affects_attrs(self):
        l = local.Local()
        o = object()
        l.__dict__['w'] = o
        self.assertEqual(l.w, o)

    def test_attrs_in_attrdict(self):
        l = local.Local()
        o = object()
        l.q = o
        self.assertEqual(l.__dict__['q'], o)

if __name__ == '__main__':
    unittest.main()
