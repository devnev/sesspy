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

try:
    # python 2.6+
    from threading import current_thread
except ImportError:
    # python 2.5
    from threading import currentThread as current_thread

try:
    # python 2.6+
    from collections import MutableMapping as _dict_base
except ImportError:
    # python 2.5
    from UserDict import DictMixin as _dict_base

# explicit object inheritence as DictMixin is an old-style class
class LocalDict(_dict_base, object):
    __slots__ = '_local__key', '_local__init'

    def __init__(self, *args, **kwargs):
        self._local__key = '%s.%s<%s>' % (
            __name__, type(self).__name__, str(id(self))
        )
        self._local__init = dict(*args, **kwargs)

    def _get_dict(self):
        res = current_thread().__dict__.get(self._local__key)
        return self._local__init if res is None else res
    def _getset_dict(self):
        res = current_thread().__dict__.get(self._local__key)
        if res is None:
            res = self._local__init.copy()
            current_thread().__dict__[self._local__key] = res
        return res

    def __getitem__(self, name):
        return self._get_dict()[name]
    def __setitem__(self, name, value):
        self._getset_dict()[name] = value
    def __delitem__(self, name):
        if name in self._get_dict():
            del self._getset_dict()[name]
        else:
            del {}[name]
    def __len__(self):
        return len(self._get_dict())
    def __contains__(self, name):
        return name in self._get_dict()
    def __iter__(self):
        return iter(self._get_dict())
    def keys(self):
        return self._get_dict().keys()
    def copy(self):
        return self._get_dict().copy()

class Local(object):
    __slots__ = '_local__dict'

    def __new__(cls):
        if cls != Local:
            raise TypeError("This class does not support inheritence")

        self = object.__new__(cls)
        object.__setattr__(self, '_local__dict', LocalDict())

        return self

    def __getattribute__(self, name):
        attrdict = object.__getattribute__(self, '_local__dict')

        try:
            # look up attribute
            return attrdict[name]
        except KeyError:
            if name != '__dict__':
                # convert exception to AttributeError
                raise AttributeError("Local has no attribute %r" % name)

        # for __dict__, fall back to returning attrdict
        assert name == '__dict__'
        return attrdict

    def __setattr__(self, name, value):
        attrdict = object.__getattribute__(self, '_local__dict')
        attrdict[name] = value

    def __delattr__(self, name):
        attrdict = object.__getattribute__(self, '_local__dict')
        try:
            del attrdict[name]
        except KeyError:
            raise AttributeError("Local has no attribute %r" % name)

