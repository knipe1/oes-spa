#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 09:17:48 2020

@author: hauke
"""

# standard libs
from enum import Enum

class ASC_PARAMETER(Enum):
    """Interface for the .asc-file parameter."""
    # Necessary to be exactly the same name as in the .asc-file.
    WL = "Wavelength (nm)"
    GRAT = "Grating Groove Density (l/mm)"
