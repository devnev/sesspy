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
from sesspy import component

class Test_ComponentRef_descriptor(unittest.TestCase):
    def test_clsget(self):
        ref = component.ComponentRef("component")
        class A(object):
            r = ref
        self.assertEqual(ref.ref, A.r.ref)

    def test_objget(self):
        ref = component.ComponentRef("component")
        class A(object):
            r = ref
        a = A()
        self.assertEqual(ref.ref, a.r.ref)

    def test_clsset(self):
        ref = component.ComponentRef("component")
        ref2 = component.ComponentRef("component2")
        class A(object):
            r = ref
        a = A()
        A.r = ref2
        self.assertEqual(ref2.ref, A.r.ref)
        self.assertEqual(ref2.ref, a.r.ref)

    def test_objset(self):
        ref = component.ComponentRef("component")
        ref2 = component.ComponentRef("component2")
        class A(object):
            r = ref
        a = A()
        a.r = ref2
        self.assertEqual(ref.ref, A.r.ref)
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
        ref = component.ComponentRef("component", name="r")
        class A(object):
            __slots__ = ('r',)
            r = ref
        self.assertEqual(ref.ref, A.r.ref)
        ref2 = component.ComponentRef("component2", name="s")
        A.r = ref2
        self.assertEqual(ref2.ref, A.r.ref)

    def test_objget_selfname(self):
        ref = component.ComponentRef("component", name="r")
        class A(object):
            __slots__ = ('r',)
            r = ref
        a = A()
        self.assertEqual(a.r.ref, ref.ref)

    def test_objget_badname(self):
        ref = component.ComponentRef("component", name="s")
        class A(object):
            __slots__ = ('r',)
            r = ref
        a = A()
        self.assertEqual(ref.ref, a.r.ref)

    def test_objget_goodname(self):
        ref = component.ComponentRef("component", name="s")
        class A(object):
            __slots__ = ('r', 's')
            r = ref
        a = A()
        self.assertEqual(ref.ref, a.r.ref)

    def test_objset_selfname(self):
        ref = component.ComponentRef("component", name='r')
        ref2 = component.ComponentRef("component2")
        class A(object):
            __slots__ = ('r',)
            r = ref
        a = A()
        def assign():
            a.r = ref2
        self.assertRaises(AttributeError, assign)

    def test_objset_badname(self):
        ref = component.ComponentRef("component", name='s')
        ref2 = component.ComponentRef("component2")
        class A(object):
            __slots__ = ('r',)
            r = ref
        a = A()
        def assign():
            a.r = ref2
        self.assertRaises(AttributeError, assign)

    def test_objset_goodname(self):
        ref = component.ComponentRef("component", name='s')
        ref2 = component.ComponentRef("component2")
        class A(object):
            __slots__ = ('r','s')
            r = ref
        a = A()
        a.r = ref2
        self.assertEqual(A.r.ref, ref.ref)
        self.assertEqual(a.r.ref, ref2.ref)

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

class Test_ComponentConfig_context(unittest.TestCase):
    def setUp(self):
        self.obj = mock.Mock()
        self.opener = mock.Mock()
        self.opener.open.return_value = self.obj
        self.opener.commit.return_value = None
        self.opener.abort.return_value = None
        self.factory = mock.Mock()
        self.factory.return_value = self.opener

    def tearDown(self):
        del self.obj
        del self.opener
        del self.factory

    def test_component(self):
        c = component.ComponentConfig(component=self.obj)
        ctx = c.local_context()
        with ctx as o:
            self.assertEqual(o, self.obj)

    def test_global_opener(self):
        c = component.ComponentConfig(global_opener=self.opener)
        ctx = c.local_context()
        with ctx as o:
            self.assertEqual(o, self.obj)
        self.assertEqual(self.opener.method_calls,
                         [('open',), ('commit', (self.obj,))])

    def test_global_factory(self):
        c = component.ComponentConfig(global_opener_factory=self.factory)
        ctx = c.local_context()
        self.assertEqual(self.factory.call_count, 1)
        self.assertEqual(self.factory.call_args, ((), {}))

        with ctx as o:
            self.assertEqual(o, self.obj)
        self.assertEqual(self.opener.method_calls,
                         [('open',), ('commit', (self.obj,))])

        ctx = c.local_context()
        self.assertEqual(self.factory.call_count, 1)

class Test_ComponentConfig_localcontext(unittest.TestCase):
    def setUp(self):
        self.obj = mock.Mock()
        self.opener = mock.Mock()
        self.opener.open.return_value = self.obj
        self.opener.commit.return_value = None
        self.opener.abort.return_value = None
        self.factory = mock.Mock()
        self.factory.return_value = self.opener

    def tearDown(self):
        del self.obj
        del self.opener
        del self.factory

    def test_opener_is_created(self):
        c = component.ComponentConfig(local_opener_factory=self.factory)
        ctx = c.local_context()
        self.assertEqual(self.factory.call_count, 1)
        self.assertEqual(self.factory.call_args, ((), {}))

    def test_opener_is_called(self):
        c = component.ComponentConfig(local_opener_factory=self.factory)
        with c.local_context() as o:
            self.assertEqual(o, self.obj)
            self.assertEqual(self.opener.method_calls,
                             [('open',)])
        self.assertEqual(self.opener.method_calls,
                         [('open',), ('commit', (self.obj,))])

    def test_opener_is_created_once_locally(self):
        c = component.ComponentConfig(local_opener_factory=self.factory)
        ctx = c.local_context()
        ctx = c.local_context()
        self.assertEqual(self.factory.call_count, 1)
        self.assertEqual(self.factory.call_args, ((), {}))

    def test_opener_is_created_once_perthread(self):
        c = component.ComponentConfig(local_opener_factory=self.factory)
        ctx = c.local_context()

        import threading
        t = threading.Thread(target=c.local_context)
        t.start()
        t.join()
        self.assertEqual(self.factory.call_count, 2)
        self.assertEqual(self.factory.call_args, ((), {}))

        ctx = c.local_context()
        self.assertEqual(self.factory.call_count, 2)
        self.assertEqual(self.factory.call_args, ((), {}))

if __name__ == '__main__':
    unittest.main()
