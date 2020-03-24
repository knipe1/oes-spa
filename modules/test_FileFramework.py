#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv

from unittest import TestCase

from modules.FileFramework import FileFramework

class TestFileFramework(TestCase):
    framework = FileFramework()

    def test_init(self):
        self.assertTrue(isinstance(self.framework.SAVE, dict));
        self.assertTrue(isinstance(self.framework.LOAD, dict));
        self.assertTrue(isinstance(self.framework.MARKER, dict));
        self.assertTrue(isinstance(self.framework.DIALECT, dict));

    def test_static(self):
        self.assertEqual(self.framework.dialect, "spectral_data")
        self.assertNotEqual(csv.get_dialect("spectral_data"), csv.Error)
        self.assertTrue("spectral_data" in csv.list_dialects())