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

from threading import RLock
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

class Local(object):
    __slots__ = '_local__key', '_local__lock'

    def __new__(cls, *args, **kw):
        if cls != Local:
            raise TypeError("This class does not support inheritence")
        if args or kw:
            raise TypeError("Initialization arguments are not supported")

        self = object.__new__(cls)
        key = 'dip.local.' + str(id(self))
        object.__setattr__(self, '_local__key', key)
        object.__setattr__(self, '_local__lock', RLock())

        return self

    def __getattribute__(self, name):
        key = object.__getattribute__(self, '_local__key')
        d = current_thread().__dict__.get(key)

        if name == '__dict__':
            # return attribute dict directly
            if d is None:
                # create a new __dict__ if necessary
                lock = object.__getattribute__(self, '_local__lock')
                with lock:
                    d = current_thread().__dict__.get(key)
                    if d is None:
                        current_thread().__dict__[key] = d = {}
            return d

        if d is not None:
            # lookup up attribute
            try:
                return d[name]
            except KeyError:
                pass

        raise AttributeError("Local has no attribute %r" % name)

    def __setattr__(self, name, value):
        key = object.__getattribute__(self, '_local__key')
        lock = object.__getattribute__(self, '_local__lock')
        with lock:
            d = current_thread().__dict__.get(key)
            # make a shallow copy or a new dict
            d = dict(d) if d is not None else {}
            d[name] = value
            current_thread().__dict__[key] = d

    def __delattr__(self, name):
        key = object.__getattribute__(self, '_local__key')
        lock = object.__getattribute__(self, '_local__lock')
        with lock:
            d = current_thread().__dict__.get(key)
            # make a shallow copy or a new dict
            d = dict(d) if d is not None else {}
            try:
                del d[name]
            except KeyError:
                raise AttributeError("Local has no attribute %r" % name)
            current_thread().__dict__[key] = d

