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

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from . import session, source, openers

def _make_callable_engine_args(db_uri, engine_args):
    if not callable(db_uri) and not callable(engine_args):
        return lambda: ((db_uri,), (engine_args or {}))
    if not callable(db_uri):
        db_uri = (lambda _x: (lambda: _x))(db_uri)
    if not callable(engine_args):
        engine_args = (lambda _x: (lambda: _x))(engine_args or {})
    return lambda: ((db_uri(),), engine_args())

def _maybe_register(component, name, registry):
    if name:
        if registry is None:
            from .registry import default_registry
            registry = default_registry
        registry.register_component(name, component)

def db_connection(db_uri, engine_args=None,
                  name=None, registry=None,
                  noretry_exceptions=None,
                  opener=openers.CountingOpener,
                  connection_factory=create_engine):

    args = _make_callable_engine_args(db_uri, engine_args)

    component = session.SessionFactory(
        source_factory=source.GuardedFactorySource(
            connection_factory,
            noretry_exceptions,
            args
        ),
        adapter_factory=source.sessionless_source_adapter,
        opener_factory=opener,
        local_openers=False,
    )

    _maybe_register(component, name, registry)

    return component

class TransactionWrapper(object):

    def __init__(self, connection, transaction):
        self._connection = connection
        self._transaction = transaction

    def __getattr__(self, name):
        return getattr(self.connection, name)

class TransactionFactory(object):

    def __init__(self, engine):
        self.engine = engine

    def open(self):
        connection = self.engine.connect()
        transaction = connection.begin()
        return TransactionWrapper(connection, transaction)

    def commit(self, transaction_wrapper):
        transaction_wrapper._transaction.commit()
        transaction_wrapper._connection.close()

    def abort(self, transaction_wrapper):
        transaction_wrapper._transaction.rollback()
        transaction_wrapper._connection.close()

def transactional_db_connection(db_uri, engine_args=None,
                                name=None, registry=None,
                                noretry_exceptions=None,
                                opener=openers.CountingOpener,
                                connection_factory=create_engine):

    args = _make_callable_engine_args(db_uri, engine_args)

    component = session.SessionFactory(
        source_factory=source.GuardedFactorySource(
            connection_factory,
            noretry_exceptions,
            args
        ),
        adapter_factory=TransactionFactory,
        opener_factory=opener,
    )

    _maybe_register(component, name, registry)

    return component

class ORMSessionFactory(object):

    def __init__(self, connection, session_args=None):
        session_args = session_args or {}
        session_args['bind'] = connection
        self.session_maker = sessionmaker(**session_args)

    def open(self):
        return self.session_maker()

    def commit(self, session):
        session.commit()

    def abort(self, session):
        session.rollback()

def orm_session(db_uri, engine_args=None,
                name=None, registry=None,
                noretry_exceptions=None,
                connection_factory=create_engine):

    args = _make_callable_engine_args(db_uri, engine_args)

    component = session.SessionFactory(
        source_factory=source.GuardedFactorySource(
            connection_factory,
            noretry_exceptions,
            args
        ),
        adapter_factory=ORMSessionFactory,
    )

    _maybe_register(component, name, registry)

    return component

def orm_counting_session(db_uri, engine_args=None,
                         name=None, registry=None,
                         noretry_exceptions=None,
                         counting_opener=openers.CountingOpener,
                         connection_factory=create_engine):

    args = _make_callable_engine_args(db_uri, engine_args)

    component = session.SessionFactory(
        source_factory=source.GuardedFactorySource(
            connection_factory,
            noretry_exceptions,
            args,
        ),
        adapter_factory=ORMSessionFactory,
        opener_factory=counting_opener,
    )

    _maybe_register(component, name, registry)

    return component

