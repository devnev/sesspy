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

import sys
from . import six

class ResolveError(LookupError):
    """
    Raised when a ComponentRef is unable to resolve its ref.
    """
    pass

class ComponentRef(object):
    """
    Reference wrapper for lazy loading of components.

    The reference may be a component, another reference, a component registry
    key or an import path.

    If used as a class attribute, any valid reference may be assigned to that
    attribute for instances of that class, and a new ComponentRef will be
    created for that instance. In this case it is recommended to set the "name"
    parameter to the attribute name (for slotted types, a free slot).

    When a refernce cannot be resolved, a ResolveError is raised.
    """

    def __init__(self, ref, name=None, reg=None, obj=None):
        self.ref = ref
        self.name = name
        if reg is None:
            from .registry import default_registry
            reg = default_registry
        self.reg = reg
        self.obj = obj

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

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        elif hasattr(obj, '__slots__'):
            # handle types with __slots__: self.name must refer to another slot
            if owner is None:
                owner = type(obj)
            if not self.name:
                return self
            elif getattr(owner, self.name, None) is self:
                # avoid recursion
                return self
            else:
                return getattr(obj, self.name, self)
        else:
            # otherwise try and get instance from __dict__, fall back to self
            try:
                attrdict = obj.__dict__
            except AttributeError:
                return self
            else:
                return attrdict.get(self.dictkey, self)

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
                raise AttributeError("ComponentRef is read-only")
            elif getattr(type(obj), self.name, None) is self:
                # avoid recursion
                raise AttributeError("ComponentRef is read-only")
            else:
                setattr(obj, self.name, ref)
        else:
            # otherwise add to obj's __dict__
            obj.__dict__[self.dictkey] = ref

    def resolve(self, obj=None):
        if obj is not None and obj is not self.obj:
            return self.__get__(obj).resolve()

        if callable(self.ref):
            resolved = self.ref
        elif isinstance(self.ref, six.string_types) and '.' in self.ref:
            try:
                _imp, _from = self.ref.rsplit('.', 1)
                _temp = __import__(_imp, fromlist=[_from])
                resolved = getattr(_temp, _from)
            except (ImportError, AttributeError):
                # XXX: only want to catch AttributeError for getattr call
                exc = sys.exc_info()[1]
                exc = ResolveError("Failed to import ref %r: %s"
                                   % (self.ref, exc))
                six.reraise(ResolveError, exc, sys.exc_info()[2])
        elif isinstance(self.ref, six.string_types) and self.reg is not None:
            try:
                resolved = self.reg[self.ref]
            except KeyError:
                exc = sys.exc_info()[1]
                exc = ResolveError("Failed to lookup ref %r: %s"
                                 % (self.ref, exc))
                six.reraise(ResolveError, exc, sys.exc_info()[2])
            if hasattr(resolved, 'resolve'):
                # in case of reference-to-reference, try "transitive" resolve
                resolved = resolved.resolve()
        else:
            resolved = None

        if not callable(resolved):
            raise ResolveError("Component ref %r does not resolve to"
                               " a session factory" % self.ref)
        self.ref = resolved

        return resolved

    def __call__(self):
        session_factory = self.resolve()
        return session_factory()

