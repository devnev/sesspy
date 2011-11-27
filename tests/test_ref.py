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
from sesspy import ref

class Test_ComponentRef_descriptor(unittest.TestCase):
    def test_clsget(self):
        ref1 = ref.ComponentRef("component")
        class A(object):
            r = ref1
        self.assertEqual(ref1.ref, A.r.ref)

    def test_objget(self):
        ref1 = ref.ComponentRef("component")
        class A(object):
            r = ref1
        a = A()
        self.assertEqual(ref1.ref, a.r.ref)

    def test_clsset(self):
        ref1 = ref.ComponentRef("component")
        ref2 = ref.ComponentRef("component2")
        class A(object):
            r = ref1
        a = A()
        A.r = ref2
        self.assertEqual(ref2.ref, A.r.ref)
        self.assertEqual(ref2.ref, a.r.ref)

    def test_objset(self):
        ref1 = ref.ComponentRef("component")
        ref2 = ref.ComponentRef("component2")
        class A(object):
            r = ref1
        a = A()
        a.r = ref2
        self.assertEqual(ref1.ref, A.r.ref)
        self.assertEqual(ref2.ref, a.r.ref)

class Test_ComponentRef_descriptor_slots(unittest.TestCase):
    def setUp(self):
        import sys
        self.oldreclimit = sys.getrecursionlimit()
        sys.setrecursionlimit(60)

    def tearDown(self):
        import sys
        sys.setrecursionlimit(self.oldreclimit)

    def test_clsget(self):
        ref1 = ref.ComponentRef("component", name="r")
        class A(object):
            __slots__ = ('r',)
            r = ref1
        self.assertEqual(ref1.ref, A.r.ref)
        ref2 = ref.ComponentRef("component2", name="s")
        A.r = ref2
        self.assertEqual(ref2.ref, A.r.ref)

    def test_objget_selfname(self):
        ref1 = ref.ComponentRef("component", name="r")
        class A(object):
            __slots__ = ('r',)
            r = ref1
        a = A()
        self.assertEqual(a.r.ref, ref1.ref)

    def test_objget_badname(self):
        ref1 = ref.ComponentRef("component", name="s")
        class A(object):
            __slots__ = ('r',)
            r = ref1
        a = A()
        self.assertEqual(ref1.ref, a.r.ref)

    def test_objget_goodname(self):
        ref1 = ref.ComponentRef("component", name="s")
        class A(object):
            __slots__ = ('r', 's')
            r = ref1
        a = A()
        self.assertEqual(ref1.ref, a.r.ref)

    def test_objset_selfname(self):
        ref1 = ref.ComponentRef("component", name='r')
        ref2 = ref.ComponentRef("component2")
        class A(object):
            __slots__ = ('r',)
            r = ref1
        a = A()
        def assign():
            a.r = ref2
        self.assertRaises(AttributeError, assign)

    def test_objset_badname(self):
        ref1 = ref.ComponentRef("component", name='s')
        ref2 = ref.ComponentRef("component2")
        class A(object):
            __slots__ = ('r',)
            r = ref1
        a = A()
        def assign():
            a.r = ref2
        self.assertRaises(AttributeError, assign)

    def test_objset_goodname(self):
        ref1 = ref.ComponentRef("component", name='s')
        ref2 = ref.ComponentRef("component2")
        class A(object):
            __slots__ = ('r','s')
            r = ref1
        a = A()
        a.r = ref2
        self.assertEqual(A.r.ref, ref1.ref)
        self.assertEqual(a.r.ref, ref2.ref)

class Test_ComponentRef_resolve(unittest.TestCase):
    def test_componentconfig(self):
        cc = mock.Mock(spec=[])
        assert callable(cc)
        ref1 = ref.ComponentRef(cc)
        self.assertEqual(ref1.resolve(), cc)

    def test_import(self):
        import sys
        cc = mock.Mock(spec=[])
        assert callable(cc)
        mod = mock.Mock()
        mod.config = cc
        sys.modules['__test_component_ref'] = mod
        try:
            ref1 = ref.ComponentRef('__test_component_ref.config')
            self.assertEqual(ref1.resolve(), cc)
            self.assertEqual(ref1.ref, cc)
        finally:
            del sys.modules['__test_component_ref']

    def test_registry_direct(self):
        cc = mock.Mock(spec=[])
        assert callable(cc)
        reg = dict(component=cc)
        ref1 = ref.ComponentRef("component", reg=reg)
        self.assertEqual(ref1.resolve(), cc)
        self.assertEqual(ref1.ref, cc)

    def test_registry_ref(self):
        cc = mock.Mock(spec=[])
        assert callable(cc)
        directref = ref.ComponentRef(cc)
        reg = dict(component=directref)
        ref1 = ref.ComponentRef("component", reg=reg)
        self.assertEqual(ref1.resolve(), cc)
        self.assertEqual(ref1.ref, cc)

    def test_registry_badref(self):
        reg = dict()
        ref1 = ref.ComponentRef("component2", reg=reg)
        self.assertRaises(ref.ResolveError, ref1.resolve)

    def test_badimport(self):
        import sys
        modname = '__test_component_ref'
        mod = mock.Mock(spec=[])
        sys.modules[modname] = mod
        try:
            ref1 = ref.ComponentRef(modname+'.config')
            self.assertRaises(ref.ResolveError, ref1.resolve)
        finally:
            del sys.modules[modname]

    def test_badcomponent(self):
        badcomp = object()
        assert not callable(badcomp)
        ref1 = ref.ComponentRef(badcomp)
        self.assertRaises(ref.ResolveError, ref1.resolve)

if __name__ == '__main__':
    unittest.main()
