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

class SingletonOpener(object):

    def __init__(self, instance):
        self.instance = instance

    def open(self):
        return self.instance

    def commit(self, component):
        pass

    def abort(self, component):
        pass

class FunctionOpener(object):

    def __init__(self, open_fn, commit_fn=None, abort_fn=None):
        self.open_fn, self.commit_fn, self.abort_fn = \
                open_fn, commit_fn, abort_fn

    def open(self):
        return self.open_fn()

    def commit(self, component):
        if self.commit_fn is not None:
            self.commit_fn(component)

    def abort(self, component):
        if self.abort_fn is not None:
            self.abort_fn(component)

class CountingOpener(object):
    def __init__(self, instance_opener):
        self.instance_opener = instance_opener
        self.count = 0
        self.instance = None

    def open(self):
        if self.instance is None:
            self.instance = self.instance_opener.open()
        self.count += 1
        return self.instance

    def commit(self, instance):
        assert self.instance is not None
        assert self.instance is instance
        assert self.count > 0
        self.count -= 1
        if self.count == 0:
            self.instance_opener.commit(self.instance)
            self.instance = None

    def abort(self, instance):
        assert self.instance is not None
        assert self.instance is instance
        assert self.count > 0
        self.count -= 1
        if self.count == 0:
            self.instance_opener.abort(self.instance)
            self.instance = None

