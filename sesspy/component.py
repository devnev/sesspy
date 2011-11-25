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

from __future__ import absolute_import

try:
    str_ = basestring
except NameError:
    str_ = str

class ResolveError(ValueError):
    pass

class ComponentError(Exception):
    pass

class ComponentRef(object):
    def __init__(self, ref, name=None, obj=None, reg=None):
        self.ref = ref
        self.name = name
        self.obj = obj
        if reg is None:
            from .registry import default_registry
            reg = default_registry
        self.reg = reg

    def copy(self, **kwargs):
        kwargs.setdefault('ref', self.ref)
        kwargs.setdefault('obj', self.obj)
        kwargs.setdefault('reg', self.reg)
        return ComponentRef(**kwargs)

    @property
    def dictkey(self):
        return self.name or '_%s__%s__%s' % (
            __name__.replace('.', '__'),
            self.__class__.__name__,
            id(self),
        )

    def __get__(self, obj, type):
        if obj is None:
            return self
        elif hasattr(obj, '__slots__'):
            # handle types with __slots__: self.name must refer to another slot
            if not self.name:
                return self
            elif getattr(type, self.name, None) is self:
                raise TypeError("ComponentRef slot name %s refers to itself" % self.name)
            else:
                return getattr(obj, self.name, self)
        else:
            # otherwise try and get instance from __dict__, fall back to self
            try:
                d = obj.__dict__
            except AttributeError:
                return self
            else:
                return d.get(self.dictkey, self)

    def __set__(self, obj, ref):
        # convert ref to ComponentRef and bind to obj
        if isinstance(ref, ComponentRef):
            ref = ref.copy(obj=obj)
        else:
            ref = self.copy(ref=ref, obj=obj)

        # set new ref on obj
        if hasattr(obj, '__slots__'):
            # handle types with __slots__: self.name must refer to another slot
            if not self.name:
                raise TypeError("No slot name set for slotted ComponentRef owner")
            elif getattr(type, self.name, None) is self:
                raise TypeError("ComponentRef slot name %s refers to itself" % self.name)
            else:
                setattr(obj, self.name, ref)
        else:
            # otherwise add to obj's __dict__
            obj.__dict__[self.dictkey] = ref

    def resolve(self, obj=None):
        if obj is not None and obj is not self.obj:
            return self.__get__(obj).resolve()

        if hasattr(self.ref, 'local_context'):
            resolved = self.ref
        elif isinstance(self.ref, str_) and '.' in self.ref:
            _imp, _from = self.ref.rsplit('.', 1)
            _temp = __import__(_imp, fromlist=[_from])
            resolved = getattr(_temp, _from)
        elif isinstance(self.ref, str_) and self.reg is not None:
            resolved = self.reg[self.ref]
            if hasattr(resolved, 'resolve'):
                resolved = resolved.resolve()
        else:
            resolved = None

        if not hasattr(resolved, 'local_context'):
            raise ResolveError("Component ref %r does not resolve to component config" % self.ref)
        self.ref = resolved

        return resolved

    def __call__(self):
        return self.resolve().local_context()

class LocalContext(object):
    def __init__(self, instance_opener):
        self.instance_opener = instance_opener
        self.instance = None

    def __enter__(self):
        self.instance = self.instance_opener.open()
        return self.instance

    def __exit__(self, exc, type, tb):
        if exc is None:
            self.instance_opener.commit(self.instance)
        else:
            self.instance_opener.abort(self.instance)

class ComponentConfig(object):
    def __init__(self, component=None, global_opener=None,
                 global_opener_factory=None,
                 local_opener_factory=None):
        self.component = component
        self.global_opener = global_opener
        self.global_opener_factory = global_opener_factory
        self.local_opener_factory = local_opener_factory
        from .local import Local
        self.locals = Local()

    def local_context(self):
        if self.global_opener is None and self.global_opener_factory is not None:
            if self.component is not None:
                self.global_opener = self.global_opener_factory(self.component)
            else:
                self.global_opener = self.global_opener_factory()

        opener = getattr(self.locals, 'opener', None)
        if opener is None and self.local_opener_factory is not None:
            if self.global_opener is not None:
                opener = self.local_opener_factory(self.global_opener)
            if self.component is not None:
                opener = self.local_opener_factory(self.component)
            else:
                opener = self.local_opener_factory()
            self.locals.opener = opener
        if opener is None and self.global_opener is not None:
            opener = self.global_opener
        if opener is None and self.component is not None:
            from .openers import SingletonOpener
            opener = SingletonOpener(self.component)
        if opener is None:
            raise ComponentError("Unable to create context for %r" % self)

        return LocalContext(opener)
