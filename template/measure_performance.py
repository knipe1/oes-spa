#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:40:37 2020

@author: hauke
"""

import time
start = time.perf_counter()
finish = time.perf_counter()

elapsed = round(finish - start, 2) # with 2 decimals
print(elapsed)