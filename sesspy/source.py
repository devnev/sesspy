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
import threading

class InstanceSource(object):

    def __init__(self, instance):
        self.instance = instance

    def __call__(self):
        return instance

class FactorySource(object):

    def __init__(self, factory, args=None):
        self.factory = factory
        self.args = args

    def __call__(self):
        args, kwargs = (), {}
        if callable(self.args):
            args, kwargs = self.args()
        elif self.args is not None:
            args, kwargs = self.args
        return self.factory(*args, **kwargs)

class GuardedFactorySource(object):

    def __init__(self, factory, noretry_exceptions=None, args=None):
        self.factory = factory
        self.args = args
        self.noretry_exceptions = noretry_exceptions
        self.instance = None
        self.exception = None
        self.factory_lock = threading.Lock()

    def create(self):
        assert self.instance is None

        args, kwargs = (), {}
        if callable(self.args):
            args, kwargs = self.args()
        elif self.args is not None:
            args, kwargs = self.args

        if self.noretry_exceptions is not None:
            try:
                self.instance = self.factory(*args, **kwargs)
            except self.noretry_exceptions:
                self.exception = sys.exc_info()[1]
                raise
        else:
            self.instance = self.factory(*args, **kwargs)

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

            self.create()
            return self.instance

    __call__ = get

class SourceAdapter(object):
    def __init__(self, source, open_fn,
                 commit_fn=None, abort_fn=None):
        self.source = source
        self.open_fn = open_fn
        self.commit_fn = commit_fn
        self.abort_fn = abort_fn

    def open(self):
        return self.open_fn(self.source)

    def commit(self, instance):
        if self.commit_fn is not None:
            self.commit_fn(self.source, instance)

    def abort(self, instance):
        if self.abort_fn is not None:
            self.abort_fn(self.source, instance)

def source_adapter_factory(open_fn, commit_fn=None, abort_fn=None):
    def factory(source):
        return SourceAdapter(source, open_fn, commit_fn, abort_fn)
    return factory

def sessionless_source_adapter(source):
    return SourceAdapter(source, lambda s: s)
