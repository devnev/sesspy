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
from sesspy import dec, component

class Test_FunctionDec(unittest.TestCase):
    def test_func_called_with_ctx(self):
        func = mock.Mock(spec=['__name__','__doc__','__module__'])
        func.__name__ = 'func'
        func.__doc__ = 'doc'
        func.__module__ = __name__
        ret = mock.Mock()
        func.return_value = ret

        comp = mock.Mock()
        ctx = mock.Mock(spec=component.LocalContext)
        ctx.__enter__ = mock.Mock()
        ctx.__enter__.return_value = comp
        ctx.__exit__ = mock.Mock()
        ctx.__exit__.return_value = None
        ref = mock.Mock(spec=component.ComponentRef)
        ref.return_value = ctx

        decf = dec.ComponentInjector(ref, func, 'component')

        self.assertEqual(decf(), ret)
        self.assertTrue(ref.called)
        self.assertEqual(func.call_args_list, [
            ((), {'component':comp})
        ])
        self.assertEqual(ctx.__enter__.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(ctx.__exit__.call_args_list, [
            ((None, None, None), {}),
        ])

    def test_func_called_given_comp(self):
        func = mock.Mock()
        func.__name__ = 'func'
        func.__doc__ = 'doc'
        func.__module__ = __name__
        ret = mock.Mock()
        func.return_value = ret

        comp = mock.Mock()
        ctx = mock.Mock(spec=component.LocalContext)
        ctx.__enter__ = mock.Mock()
        ctx.__enter__.return_value = comp
        ctx.__exit__ = mock.Mock()
        ctx.__exit__.return_value = None
        ref = mock.Mock(spec=component.ComponentRef)
        ref.return_value = ctx
        comp2 = mock.Mock()

        decf = dec.ComponentInjector(ref, func, 'component')

        self.assertEqual(decf(component=comp2), ret)
        self.assertEqual(func.call_args_list, [
            ((), {'component':comp2})
        ])
        self.assertEqual(ctx.method_calls, [])
        self.assertFalse(ctx.__enter__.called)
        self.assertFalse(ctx.__exit__.called)

class Test_MethodDec(unittest.TestCase):
    def test_func_called_with_ctx(self):
        func = mock.Mock(spec=['__name__','__doc__','__module__','__get__'])
        func.__name__ = 'func'
        func.__doc__ = 'doc'
        func.__module__ = __name__
        func.__get__ = mock.Mock()
        bound = mock.Mock(spec=['__name__','__doc__','__module__'], name='bound')
        bound.__name__ = 'func'
        bound.__doc__ = 'doc'
        bound.__module__ = __name__
        func.__get__.return_value = bound
        ret = mock.Mock()
        func.return_value = ret
        bound.return_value = ret

        comp = mock.Mock()
        ctx = mock.Mock(spec=component.LocalContext)
        ctx.__enter__ = mock.Mock()
        ctx.__enter__.return_value = comp
        ctx.__exit__ = mock.Mock()
        ctx.__exit__.return_value = None
        ref = mock.Mock(spec=component.ComponentRef)
        ref.__get__ = mock.Mock()
        ref.__get__.return_value = ref
        ref.return_value = ctx

        class C(object):
            method = dec.ComponentInjector(ref, func, 'component')
        c = C()

        self.assertEqual(func.__get__.called, False)
        m = c.method
        self.assertEqual(func.__get__.called, True)

        r = m()
        self.assertEqual(r, ret)
        self.assertEqual(func.called, False)
        self.assertEqual(bound.call_args_list, [
            ((), {'component':comp})
        ])
        self.assertEqual(ctx.__enter__.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(ctx.__exit__.call_args_list, [
            ((None, None, None), {}),
        ])

    def test_func_called_with_object_ctx(self):
        func = mock.Mock(spec=['__name__','__doc__','__module__','__get__'])
        func.__name__ = 'func'
        func.__doc__ = 'doc'
        func.__module__ = __name__
        func.__get__ = mock.Mock()
        bound = mock.Mock(spec=['__name__','__doc__','__module__'], name='bound')
        bound.__name__ = 'func'
        bound.__doc__ = 'doc'
        bound.__module__ = __name__
        func.__get__.return_value = bound
        ret = mock.Mock()
        func.return_value = ret
        bound.return_value = ret

        comp = mock.Mock()
        ctx = mock.Mock(spec=component.LocalContext)
        ctx.__enter__ = mock.Mock()
        ctx.__enter__.return_value = comp
        ctx.__exit__ = mock.Mock()
        ctx.__exit__.return_value = None
        conf = mock.Mock(spec=component.ComponentConfig)
        conf.local_context.return_value = ctx
        conf2 = mock.Mock(spec=component.ComponentConfig)
        conf2.local_context.return_value = ctx
        ref = component.ComponentRef(conf)

        class C(object):
            cref = ref
            method = dec.ComponentInjector(cref, func, 'component')

        c = C()
        self.assertEqual(func.__get__.called, False)

        c.cref = conf2

        m = c.method
        self.assertEqual(func.__get__.called, True)

        r = m()
        self.assertEqual(r, ret)
        self.assertEqual(func.called, False)
        self.assertEqual(bound.call_args_list, [
            ((), {'component':comp})
        ])
        self.assertEqual(conf.local_context.called, False)
        self.assertEqual(conf2.local_context.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(ctx.__enter__.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(ctx.__exit__.call_args_list, [
            ((None, None, None), {}),
        ])

class Test_DecHelper(unittest.TestCase):
    def test_builds_injector(self):
        inj = mock.Mock()
        ret = mock.Mock()
        inj.return_value = ret
        ref = mock.Mock()
        func = mock.Mock()

        res = dec.with_component(ref, "component", inj)(func)
        self.assertEqual(res, ret)
        self.assertEqual(inj.call_args_list, [
            ((ref, func, "component"), {}),
        ])

    def test_builds_injector_refkw(self):
        inj = mock.Mock()
        ret = mock.Mock()
        inj.return_value = ret
        ref = "__test_ref"
        func = mock.Mock()

        res = dec.with_component(ref, None, inj)(func)
        self.assertEqual(res, ret)
        self.assertEqual(inj.call_args_list, [
            ((ref, func, ref), {}),
        ])

if __name__ == '__main__':
    unittest.main()
