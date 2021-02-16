#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""

# standard libs
import csv

# third-party libs
from unittest import TestCase

# local modules/libs
from modules.filehandling.fileframework import FileFramework

class TestFileFramework(TestCase):
    framework = FileFramework()

    def test_init(self):
        self.assertTrue(isinstance(self.framework.MARKER, dict));
        self.assertTrue(isinstance(self.framework.DIALECT, dict));

    def test_static(self):
        self.assertEqual(self.framework.dialect, "spectral_data")
        self.assertNotEqual(csv.get_dialect("spectral_data"), csv.Error)
        self.assertTrue("spectral_data" in csv.list_dialects())
