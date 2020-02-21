# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 09:14:12 2020

@author: wernecke
"""

from pynput.keyboard import Key, Controller
from time import sleep

PAUSE = 0.5;


def key_accept():
    keyboard = Controller()
    sleep(PAUSE)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def key_reject():
    keyboard = Controller()
    sleep(PAUSE)
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
