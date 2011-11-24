# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .component import ComponentConfig, ComponentRef

class DuplicateComponentError(Exception):
    pass

class ComponentRegistry(object):
    def __init__(self):
        self.config_map = {}

    def register_component(self, name, config):
        if name in self.configs:
            raise DuplicateComponentError("Component with name %s already registered" % name)
        self.config_map[name] = config
        return config

    def register_factory(self, name, opener_factory):
        config = ComponentConfig(local_opener_factory=opener_factory)
        return self.register_component(name, config)

    def register_session(self, name, session_opener):
        from . import openers
        config = ComponentConfig(
            global_opener=session_opener,
            local_opener_factory=openers.CountingOpener,
        )
        return self.register_component(name, config)

    def register_singleton(self, name, instance):
        config = ComponentConfig(
            component=instance,
        )
        return self.register_component(name, config)

    def __getitem__(self, name):
        return ComponentRef(self.config_map[name])

    def get(self, name):
        return ComponentRef(name, reg=self)

default_registry = ComponentRegistry()
