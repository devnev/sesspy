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

from __future__ import absolute_import, with_statement

from .ref import ComponentRef
from . import six

class ComponentInjector(object):
    """
    Function decorator that injects a session into the call arguments.

    This can be wrapped around methods or free functions (e.g. using the
    "with_component" helper). When it is called, it will open a session for the
    specified component and inject it into the call arguments with the
    specified keyword. If the keyword argument is already present in the call,
    it is not overridden.
    """

    def __init__(self, ref, func, arg_kw):
        for attr in ('__name__', '__doc__', '__module__'):
            if hasattr(func, attr):
                setattr(self, attr, getattr(func, attr))
            self.__dict__.update(getattr(func, '__dict__', {}))
        self.func = func
        if not callable(ref):
            ref = ComponentRef(ref)
        self.ref = ref
        self.arg_kw = arg_kw
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    def copy(self, **kwargs):
        kwargs.setdefault('ref', self.ref)
        kwargs.setdefault('func', self.func)
        kwargs.setdefault('arg_kw', self.arg_kw)
        return ComponentInjector(**kwargs)

    @property
    def dictkey(self):
        return '_%s__%s__%s' % (
            __name__.replace('.', '__'),
            self.__class__.__name__,
            id(self),
        )

    def __get__(self, obj, owner=None):
        if hasattr(self.func, '__get__'):
            # when accessing methods, return new instance with bound method
            kwargs = dict(func=self.func.__get__(obj, owner))
            if hasattr(self.ref, '__get__'):
                kwargs['ref'] = self.ref.__get__(obj, owner)
            return self.copy(**kwargs)
        else:
            return self

    def __call__(self, *args, **kwargs):
        if self.arg_kw not in kwargs:
            with self.ref() as instance:
                kwargs[self.arg_kw] = instance
                return self.func(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)

def with_component(ref, arg=None, injector=ComponentInjector):
    """
    Helper to wrap a function in a ComponentInjector.
    """
    if arg is None:
        if isinstance(ref, six.string_types) and '.' not in ref:
            arg = ref
        else:
            raise ValueError("arg must not be None unless ref"
                             " is a registry reference")
    def decorator(func):
        return injector(ref, func, arg)
    return decorator
