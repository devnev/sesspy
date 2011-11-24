# -*- coding: utf-8 -*-
from __future__ import absolute_import

from threading import RLock, current_thread

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

