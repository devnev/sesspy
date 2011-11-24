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
from sesspy import registry, component

class Test_ComponentRef_descriptor(unittest.TestCase):
    def test_register_config(self):
        config = mock.Mock(component.ComponentConfig)
        reg = registry.ComponentRegistry()
        reg.register_component("component", config)
        self.assertEqual(reg["component"].ref, config)

    def test_register_duplicate_config(self):
        config = mock.Mock(component.ComponentConfig)
        config2 = mock.Mock(component.ComponentConfig)
        reg = registry.ComponentRegistry()
        reg.register_component("component", config)
        self.assertRaises(registry.DuplicateComponentError,
                          reg.register_component,
                          "component", config2)
        self.assertEqual(reg["component"].ref, config)

    def test_register_altmethods(self):
        obj = mock.Mock()
        reg = registry.ComponentRegistry()
        reg.register_factory("factory", obj)
        self.assertTrue(reg["factory"])
        reg.register_session("session", obj)
        self.assertTrue(reg["session"])
        reg.register_singleton("singleton", obj)
        self.assertTrue(reg["singleton"])

    def test_register_singleton(self):
        obj = mock.Mock()
        reg = registry.ComponentRegistry()
        reg.register_singleton("obj", obj)
        ref = reg["obj"]
        with ref() as o:
            self.assertEqual(o, obj)

if __name__ == '__main__':
    unittest.main()
