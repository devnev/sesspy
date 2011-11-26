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

import sys
import warnings

class Session(object):
    def __init__(self, instance_opener):
        self.instance_opener = instance_opener
        self.instance = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc, type, tb):
        if exc is None:
            self.commit()
        else:
            self.abort()

    def open(self):
        assert self.instance is None
        self.instance = self.instance_opener.open()
        return self.instance

    def commit(self):
        assert self.instance is not None
        instance = self.instance
        self.instance = None
        self.instance_opener.commit(instance)

    def abort(self):
        assert self.instance is not None
        instance = self.instance
        self.instance = None
        self.instance_opener.abort(instance)

class LocalOpeners(object):
    def __init__(self):
        from .local import Local
        self.openers = Local()

    def __getitem__(self, config):
        try:
            return getattr(self.openers, str(id(config)))
        except AttributeError:
            raise KeyError(str(sys.exc_info()[1])), None, sys.exc_info()[2]

    def __setitem__(self, config, opener):
        setattr(self.openers, str(id(config)), opener)

    def close_remaining(self):
        for cid, opener in list(self.openers.__dict__.items()):
            if hasattr(opener, 'close'):
                try:
                    opener.close()
                except Exception:
                    e = sys.exc_info()[1]
                    warnings.warn("An exception was raised while closing openers: " + str(e))
            del self.openers.__dict__[cid]

    def clear(self):
        self.openers.__dict__.clear()

default_local_openers = LocalOpeners()

class SessionFactoryBase(object):

    def __init__(self, local_openers=None):
        if local_openers is None:
            local_openers = default_local_openers
        self.local_openers = local_openers

    def create_opener(self):
        assert False, "SessionFactoryBase.create_opener is abstract"

    def local_session(self):
        if self.local_openers is False:
            return Session(self.create_opener())
        try:
            opener = self.local_openers[self]
        except KeyError:
            opener = self.create_opener()
            self.local_openers[self] = opener
        return Session(opener)

    __call__ = local_session

class Singleton(SessionFactoryBase):

    def __init__(self, instance,
                 opener_factory=None,
                 local_openers=None):
        super(Singleton, self).__init__(local_openers)

        self.instance = instance

        if opener_factory is None:
            from . import openers
            opener_factory = openers.SingletonOpener
        self.opener_factory = opener_factory

    def create_opener(self):
        return self.opener_factory(self.instance)

class SingletonFactory(SessionFactoryBase):

    def __init__(self, factory,
                 noretry_exceptions=None,
                 instance_opener=None,
                 local_openers=None,
                 args=None, kwargs=None):
        super(SingletonFactory, self).__init__(local_openers)

        self.factory = factory
        self.instance = None
        self.factory_args = (args, kwargs)

        if instance_opener is None:
            from . import openers
            instance_opener = SingletonOpener
        self.instance_opener = instance_opener

        self.noretry_exceptions = noretry_exceptions
        self.exception = None
        import threading
        self.factory_lock = threading.Lock()

    def create(self):
        args, kwargs = self.factory_args
        args, kwargs = (args or ()), (kwargs or {})
        if self.noretry_exceptions is not None:
            try:
                instance = self.factory(*args, **kwargs)
            except self.noretry_exceptions:
                self.exception = sys.exc_info()[1]
                raise
        else:
            instance = self.factory(*args, **kwargs)
        return instance

    def get(self):
        if self.exception is not None:
            raise self.exception
        elif self.instance is not None:
            return self.instance

        with self.factory_lock:
            if self.exception is not None:
                raise self.exception
            elif self.instance is not None:
                return self.instance

            self.instance = self.create()
            return self.instance

    def create_opener(self):
        return self.instance_opener(self.get())
