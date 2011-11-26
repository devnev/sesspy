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

    def commit(self, instance):
        pass

    def abort(self, instance):
        pass

class FunctionOpener(object):

    def __init__(self, open_fn, commit_fn=None, abort_fn=None):
        self.open_fn, self.commit_fn, self.abort_fn = \
                open_fn, commit_fn, abort_fn

    def open(self):
        return self.open_fn()

    def commit(self, session):
        if self.commit_fn is not None:
            self.commit_fn(session)

    def abort(self, session):
        if self.abort_fn is not None:
            self.abort_fn(session)

class CountingOpener(object):
    def __init__(self, session_opener):
        self.session_opener = session_opener
        self.count = 0
        self.session = None

    def open(self):
        if self.session is None:
            self.session = self.session_opener.open()
        self.count += 1
        return self.session

    def commit(self, session):
        assert self.session is not None
        assert self.session is session
        assert self.count > 0
        self.count -= 1
        if self.count == 0:
            self.session_opener.commit(self.session)
            self.session = None

    def abort(self, session):
        assert self.session is not None
        assert self.session is session
        assert self.count > 0
        self.count -= 1
        if self.count == 0:
            self.session_opener.abort(self.session)
            self.session = None

    def close(self):
        if self.count > 1:
            self.session_opener.abort(self.session)
            self.session = None
            self.count = 0

def combine_openers(*openers):
    def factory(start):
        for opener in openers:
            start = opener(start)
        return start
    return factory
