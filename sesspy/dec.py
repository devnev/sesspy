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

from .component import ComponentRef

try:
    str_ = basestring
except NameError:
    str_ = str

class ComponentInjector(object):
    def __init__(self, ref, func, arg_kw):
        for attr in ('__name__', '__doc__', '__module__'):
            if hasattr(func, attr):
                setattr(self, attr, getattr(func, attr))
            self.__dict__.update(getattr(func, '__dict__', {}))
        self.func = func
        if not isinstance(ref, ComponentRef):
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

    def __get__(self, obj, type=None):
        if hasattr(self.func, '__get__'):
            # when accessing methods, return new instance with bound method
            return self.copy(func=self.func.__get__(obj, type))
        else:
            return self

    def __call__(self, *args, **kwargs):
        if self.arg_kw not in kwargs:
            with self.ref() as instance:
                kwargs[self.arg_kw] = instance
                return self.func(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)

def with_component(ref, arg_kw=None):
    if arg_kw is None:
        if isinstance(ref, str_) and '.' not in ref:
            arg_kw = ref
        else:
            raise ValueError("arg_kw must not be None unless ref is a registry reference")
    def decorator(func):
        return ComponentInjector(ref, func, arg_kw)
    return decorator
