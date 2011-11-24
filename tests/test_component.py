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
from sesspy import component

class Test_ComponentRef_descriptor(unittest.TestCase):
    def test_clsget(self):
        ref = component.ComponentRef("component", None, None)
        class A(object):
            r = ref
        self.assertEqual(ref.ref, A.r.ref)

    def test_objget(self):
        ref = component.ComponentRef("component", None, None)
        class A(object):
            r = ref
        a = A()
        self.assertEqual(ref.ref, a.r.ref)

    def test_clsset(self):
        ref = component.ComponentRef("component", None, None)
        ref2 = component.ComponentRef("component2", None, None)
        class A(object):
            r = ref
        a = A()
        A.r = ref2
        self.assertEqual(ref2.ref, A.r.ref)
        self.assertEqual(ref2.ref, a.r.ref)

    def test_objset(self):
        ref = component.ComponentRef("component", None, None)
        ref2 = component.ComponentRef("component2", None, None)
        class A(object):
            r = ref
        a = A()
        a.r = ref2
        self.assertEqual(ref.ref, A.r.ref)
        self.assertEqual(ref2.ref, a.r.ref)

class Test_ComponentRef_resolve(unittest.TestCase):
    def test_componentconfig(self):
        cc = mock.Mock(component.ComponentConfig)
        ref = component.ComponentRef(cc)
        self.assertEqual(ref.resolve(), cc)

    def test_import(self):
        import sys
        cc = mock.Mock(component.ComponentConfig)
        mod = mock.Mock()
        mod.config = cc
        sys.modules['__test_component_ref'] = mod
        ref = component.ComponentRef('__test_component_ref.config')
        try:
            self.assertEqual(ref.resolve(), cc)
            self.assertEqual(ref.ref, cc)
        finally:
            del sys.modules['__test_component_ref']

    def test_registry_direct(self):
        cc = mock.Mock(component.ComponentConfig)
        reg = dict(component=cc)
        ref = component.ComponentRef("component", reg=reg)
        self.assertEqual(ref.resolve(), cc)
        self.assertEqual(ref.ref, cc)

    def test_registry_ref(self):
        cc = mock.Mock(component.ComponentConfig)
        directref = component.ComponentRef(cc)
        reg = dict(component=directref)
        ref = component.ComponentRef("component", reg=reg)
        self.assertEqual(ref.resolve(), cc)
        self.assertEqual(ref.ref, cc)

if __name__ == '__main__':
    unittest.main()
