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

class ConnectionFactory(object):

    def __init__(self, db_uri, **kwargs):
        self.db_uri = db_uri
        self.engine_kwargs = kwargs

    def __call__(self):
        db_uri = self.db_uri
        if callable(db_uri):
            db_uri = db_uri()

        engine = create_engine(db_uri, **self.engine_kwargs)
        return engine

def db_connection(db_uri, engine_args=None,
                  name=None, registry=None,
                  noretry_exceptions=None,
                  connection_factory=ConnectionFactory):
    from . import session, openers

    component = session.SingletonFactory(
        factory=connection_factory(db_uri, **(engine_args or {})),
        instance_opener=openers.SingletonOpener,
        local_openers=False,
        noretry_exceptions=noretry_exceptions,
    )

    if name:
        if registry is None:
            from .registry import default_registry
            registry = default_registry
        registry.register_component(name, component)

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
                noretry_exceptions=None):
    from . import session

    component = session.SingletonFactory(
        factory=ConnectionFactory(db_uri, **engine_args),
        instance_opener=ORMSessionFactory,
        noretry_exceptions=noretry_exceptions,
    )

    if name:
        if registry is None:
            from .registry import default_registry
            registry = default_registry
        registry.register_component(name, component)

    return component

def orm_counting_session(db_uri, engine_args=None,
                         name=None, registry=None,
                         noretry_exceptions=None,
                         counting_opener=None):
    from . import session, openers
    if counting_opener is None:
        counting_opener = openers.CountingOpener

    component = session.SingletonFactory(
        factory=ConnectionFactory(db_uri, **engine_args),
        instance_opener=openers.combine_openers(
            ORMSessionFactory,
            counting_opener,
        ),
        noretry_exceptions=noretry_exceptions,
    )

    if name:
        if registry is None:
            from .registry import default_registry
            registry = default_registry
        registry.register_component(name, component)

    return component

