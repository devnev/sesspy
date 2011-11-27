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
from .six.moves import configparser

class FeatureUnconfigured(Exception):
    pass

class LazyConfigReader(object):
    """
    Helper for lazy loading config files.

    This class can be used as a "get_config" callable, lazily loading the
    specified paths on first call. This also allows the paths to be adjusted at
    load-time before the configuration is first read.
    """

    def __init__(self, config, paths, expanduser=True, leaf=None):
        self.config = config
        self.paths = paths
        self.expanduser = expanduser
        self.leaf = leaf
        self.load_lock = threading.Lock()
        self.read_paths = None

    def read(self):
        import os, os.path
        paths = self.paths
        if self.leaf:
            paths = [os.path.join(p, self.leaf) for p in paths]
        if self.expanduser:
            paths = [os.path.expanduser(p) for p in paths]
        read_paths = self.read_paths or []
        read_paths.extend(self.config.read(paths))
        self.read_paths = read_paths

    def __call__(self):
        if self.read_paths is not None:
            return self.config
        with self.load_lock:
            if self.read_paths is not None:
                return self.config
            self.read()
            return self.config

class ConfigOption(object):
    """
    Configuration option helper.

    When called it in turn calls the get_config callable and then attempts to
    retrieve the specified option. If the section or option does not exist,
    it raises a FeatureUnconfigured exception.
    """
    def __init__(self, get_config, section, option):
        self.get_config = get_config
        self.section, self.option = section, option

    def __call__(self):
        config = self.get_config()
        try:
            return config.get(self.section, self.option)
        except (configparser.NoSectionError,
                configparser.NoOptionError):
            raise FeatureUnconfigured(str(sys.exc_info()[1]))
