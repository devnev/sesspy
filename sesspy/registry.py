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

from .ref import ComponentRef

class DuplicateComponentError(Exception):
    pass

class ComponentRegistry(object):
    def __init__(self):
        self.configs = {}

    def register_component(self, name, config):
        if name in self.configs:
            raise DuplicateComponentError("Component with name %s already registered" % name)
        self.configs[name] = config
        return config

    def __getitem__(self, name):
        return ComponentRef(self.configs[name], reg=self)

    def get(self, name):
        return ComponentRef(name, reg=self)

default_registry = ComponentRegistry()
