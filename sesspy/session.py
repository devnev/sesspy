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
from . import six

_INSTANCE_SENTINEL = object()

class SessionStateException(Exception):
    """
    Raised when a session call is made that is not valid in the current state.
    """
    pass

class Session(object):
    """
    Encapsulate a thread-local session for a particular resource.
    """

    def __init__(self, instance_opener):
        self.instance_opener = instance_opener
        self.instance = _INSTANCE_SENTINEL

    def __enter__(self):
        return self.open()

    def __exit__(self, exc, typ, tb):
        if exc is None:
            self.commit()
        else:
            self.abort()

    def open(self, raise_failure=True):
        """
        Begin a session and return the corresponding resource/connection.

        If a session has already been opened, a :exc:`SessionStateException` is
        raised, unless ``raise_failure`` is false, in which case ``None`` is
        returned.
        """
        if self.instance is not _INSTANCE_SENTINEL:
            if raise_failure:
                raise SessionStateException(
                    "called open on already open session object"
                )
            return
        self.instance = self.instance_opener.open()
        return self.instance

    def commit(self, raise_failure=True):
        """
        End the started session, finalizing any changes.

        The semantics of finalizing depends on the resource. The object
        returned by ``open`` should not be used after this call, as the connection
        to the resource may be closed.

        If no session has been opened, a :exc:`SessionStateException` is
        raised, unless ``raise_failure`` is false, in which case ``None`` is
        returned.
        """
        if self.instance is _INSTANCE_SENTINEL:
            if raise_failure:
                raise SessionStateException(
                    "called commit on unopened session object"
                )
            return
        instance = self.instance
        self.instance = _INSTANCE_SENTINEL
        self.instance_opener.commit(instance)

    def abort(self, raise_failure=True):
        """
        End the started session, discarding any changes.

        The semantics of rolling back changes depends on the resource. The
        object returned by ``open`` should not be used after this call, as the
        connection to the resource may be closed.

        If no session has been opened, a :exc:`SessionStateException` is
        raised, unless ``raise_failure`` is false, in which case ``None`` is
        returned.
        """
        if self.instance is _INSTANCE_SENTINEL:
            if raise_failure:
                raise SessionStateException(
                    "called abort on unopened session object"
                )
            return
        instance = self.instance
        self.instance = _INSTANCE_SENTINEL
        self.instance_opener.abort(instance)

class LocalOpeners(object):
    def __init__(self):
        from .local import Local
        self.openers = Local()

    def __getitem__(self, config):
        try:
            return getattr(self.openers, str(id(config)))
        except AttributeError:
            six.reraise(KeyError,
                        KeyError(str(sys.exc_info()[1])),
                        sys.exc_info()[2])

    def __setitem__(self, config, opener):
        setattr(self.openers, str(id(config)), opener)

    def close_remaining(self):
        """
        Close any remaining openers for the current thread, and remove them
        from this :class:`LocalOpeners` instance.

        This is particularly useful in conjunction with
        :class:`.LazyCountingOpener`.
        """

        for cid, opener in list(self.openers.__dict__.items()):
            del self.openers.__dict__[cid]
            if not hasattr(opener, 'close'):
                continue
            try:
                opener.close()
            except Exception:
                exc = sys.exc_info()[1]
                warnings.warn("An exception was raised while closing openers: "
                              + str(exc))

    def clear(self):
        self.openers.__dict__.clear()

default_local_openers = LocalOpeners()

class SessionFactory(object):
    """
    A session factory helper that combines various common steps to build
    sessions.

    :param source_factory: A callable for (lazily) creating a source, e.g.
        establishing a connection.
    :param adapter_factory: A callable that takes a single source instance and
        wraps it with an opener interface.
    :param opener_factory: If not ``None``, a callable that takes the adapted
        source and returns another opener.
    :param local_openers: A cache for thread-local openers. This is required
        for e.g. counting openers, and may be ``None`` or ``True`` for the
        default opener cache. ``False`` implies no cache.
    """

    def __init__(self,
                 source_factory, adapter_factory,
                 opener_factory=None, local_openers=None):
        self.source_factory = source_factory
        self.adapter_factory = adapter_factory
        self.opener_factory = opener_factory
        if local_openers is None or local_openers is True:
            local_openers = default_local_openers
        elif local_openers is False:
            local_openers = None
        self.local_openers = local_openers

    def create_opener(self):
        source = self.source_factory()
        opener = self.adapter_factory(source)
        if self.opener_factory is not None:
            opener = self.opener_factory(opener)
        return opener

    def open_session(self):
        if self.local_openers is None:
            opener = self.create_opener()
        else:
            opener = None
            try:
                opener = self.local_openers[self]
            except KeyError:
                pass
            if not opener:
                opener = self.create_opener()
                self.local_openers[self] = opener
        return Session(opener)

    __call__ = open_session
