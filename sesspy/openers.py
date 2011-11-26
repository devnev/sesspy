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

import warnings

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

    def __init__(self, open_fn, commit_fn=None, abort_fn=None, close_fn=None):
        self.open_fn, self.close_fn = open_fn, close_fn
        self.commit_fn, self.abort_fn = commit_fn, abort_fn

    def open(self):
        return self.open_fn()

    def commit(self, session):
        if self.commit_fn is not None:
            self.commit_fn(session)

    def abort(self, session):
        if self.abort_fn is not None:
            self.abort_fn(session)

    def close(self):
        if self.close_fn is not None:
            self.close_fn()

class CountingOpenerBase(object):
    def __init__(self, session_opener):
        assert not issubclass(CountingOpenerBase, type(self)), \
                "CountingOpenerBase is abstract"
        self.session_opener = session_opener
        self.count = 0
        self.session = None

    def open(self):
        if self.session is None:
            self.session = self.session_opener.open()
        self.count += 1
        return self.session

    def commit(self, session):
        if self.count <= 0:
            warnings.warn("Got commit for session with count %d <= 0" % self.count)
        if session is not self.session:
            warnings.warn("Got commit for unrecognized session %r (instead of %r)" %
                        session, self.session)
        self.count -= 1

    def abort(self, session):
        if self.count <= 0:
            warnings.warn("Got abort for session with count %d <= 0" % self.count)
        if session is not self.session:
            warnings.warn("Got abort for unrecognized session %r (instead of %r)" %
                        session, self.session)
        self.count -= 1

class CountingOpener(CountingOpenerBase):
    def __init__(self, session_opener):
        super(CountingOpener, self).__init__(session_opener)

    def commit(self, session):
        super(CountingOpener, self).commit(session)
        if self.count == 0:
            self.session_opener.commit(self.session)
            self.session = None

    def abort(self, session):
        super(CountingOpener, self).abort(session)
        if self.count == 0:
            self.session_opener.abort(self.session)
            self.session = None

    def close(self):
        if self.count > 0:
            warnings.warn("Closing in-use session")
            self.session_opener.abort(self.session)
            self.session = None

class LazyCountingOpener(CountingOpenerBase):
    def __init__(self, session_opener):
        super(LazyCountingOpener, self).__init__(session_opener)

    def abort(self, session):
        super(CountingOpener, self).abort(session)
        if self.count == 0:
            self.session_opener.abort(self.session)
            self.session = None

    def close(self):
        if self.count > 0:
            warnings.warn("Closing in-use session")
            self.session_opener.abort(self.session)
        elif self.session is not None:
            self.session_opener.commit(self.session)
        self.session = None

def combine_openers(*openers):
    def factory(start):
        for opener in openers:
            start = opener(start)
        return start
    return factory
