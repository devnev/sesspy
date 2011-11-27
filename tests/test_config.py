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

from __future__ import with_statement

if __name__ == '__main__':
    import sys
    import os, os.path
    sys.path.insert(
        0,
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(
                    os.path.abspath(__file__)
                )
            )
        )
    )

import unittest
import mock
import os, os.path
from sesspy import config

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class Test_LazyConfigReader(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, 'conf'):
            del self.conf
        if hasattr(self, 'paths'):
            del self.paths
        if hasattr(self, 'read_paths'):
            del self.read_paths

    def set_up_conf(self, paths, read_paths):
        self.conf = mock.Mock(spec=['read'])
        self.conf.read = mock.Mock(spec=[])
        self.conf.read.return_value = list(read_paths)
        self.paths = paths
        self.read_paths = read_paths

    def check_multicall(self, lcr):
        self.assertEqual(self.conf.called, False)
        self.assertEqual(self.conf.read.called, False)

        for _ in range(5):
            c = lcr()
            self.assertEqual(c, self.conf)
            self.assertEqual(self.conf.read.call_args_list, [
                ((self.paths,), {}),
            ])
            self.assertEqual(lcr.read_paths, self.read_paths)

    def test_call_reads_config_once(self):
        paths = ['/test/1', '/test/2', '~/test/3']
        read_paths = paths[1:]
        self.set_up_conf(paths, read_paths)

        lcr = config.LazyConfigReader(self.conf, self.paths, expanduser=False)
        self.check_multicall(lcr)

    def test_call_reads_config_once_on_emptyread(self):
        paths = ['/test/1', '/test/2', '~/test/3']
        read_paths = []
        self.set_up_conf(paths, read_paths)

        lcr = config.LazyConfigReader(self.conf, self.paths, expanduser=False)
        self.check_multicall(lcr)

    def test_call_epandsuser(self):
        paths = ['~/test/1', '~/test/2', '/test/3']
        expandpaths = [os.path.expanduser(p) for p in paths]
        read_paths = expandpaths[1:]
        self.set_up_conf(paths, read_paths)

        lcr = config.LazyConfigReader(self.conf, self.paths, expanduser=True)
        self.paths = expandpaths
        self.check_multicall(lcr)

    def test_call_addsleaf(self):
        paths = ['/test/', '/test', '~/test/3']
        leaf = 'asdf'
        leafpaths = [os.path.join(p, leaf) for p in paths]
        read_paths = leafpaths[1:]
        self.set_up_conf(paths, read_paths)

        lcr = config.LazyConfigReader(self.conf, self.paths,
                                      leaf=leaf, expanduser=False)
        self.paths = leafpaths
        self.check_multicall(lcr)

class Test_ConfigOption(unittest.TestCase):

    def test_call_returns_value(self):
        get_config = mock.Mock(spec=[])
        conf = mock.Mock(spec=['get'])
        conf.get = mock.Mock(spec=[])
        value = mock.Mock(spec=[])

        get_config.return_value = conf
        conf.get.return_value = value
        sec, opt = 'section', 'option'

        co = config.ConfigOption(get_config, sec, opt)
        self.assertEqual(get_config.called, False)

        v = co()
        self.assertEqual(v, value)
        self.assertEqual(get_config.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(conf.called, False)
        self.assertEqual(conf.get.call_args_list, [
            ((sec, opt), {})
        ])

    def test_secerr_is_caught(self):
        get_config = mock.Mock(spec=[])
        conf = mock.Mock(spec=['get'])
        conf.get = mock.Mock(spec=[])
        value = mock.Mock(spec=[])

        get_config.return_value = conf
        conf.get.return_value = value
        sec, opt = 'section', 'option'
        conf.get.side_effect = configparser.NoSectionError(sec)

        co = config.ConfigOption(get_config, sec, opt)
        self.assertEqual(get_config.called, False)

        self.assertRaises(config.FeatureUnconfigured, co)
        self.assertEqual(get_config.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(conf.called, False)
        self.assertEqual(conf.get.call_args_list, [
            ((sec, opt), {})
        ])

    def test_opterr_is_caught(self):
        get_config = mock.Mock(spec=[])
        conf = mock.Mock(spec=['get'])
        conf.get = mock.Mock(spec=[])
        value = mock.Mock(spec=[])

        get_config.return_value = conf
        conf.get.return_value = value
        sec, opt = 'section', 'option'
        conf.get.side_effect = configparser.NoOptionError(opt, sec)

        co = config.ConfigOption(get_config, sec, opt)
        self.assertEqual(get_config.called, False)

        self.assertRaises(config.FeatureUnconfigured, co)
        self.assertEqual(get_config.call_args_list, [
            ((), {}),
        ])
        self.assertEqual(conf.called, False)
        self.assertEqual(conf.get.call_args_list, [
            ((sec, opt), {})
        ])

if __name__ == '__main__':
    unittest.main()
