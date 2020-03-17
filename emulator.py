# -*- coding: utf-8 -*-
"""
This module is meant to emulate key-presses.
Can be extended to emulate mouse clicks.

Created on Fri Feb 21 09:14:12 2020

@author: wernecke
"""

__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de"
__status__ = "alpha"


from pynput.keyboard import Key, Controller
from time import sleep

PAUSE = 1.5;


def key_accept():
    """
    Emulates a enter-key press after a pause.
    Often used as a thread to accept a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def key_reject():
    """
    Emulates a esc-key press after a pause.
    Often used as a thread to reject a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE)
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)

def key_alt_j():
    """
    Emulates a esc-key press after a pause.
    Often used as a thread to reject a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE)
    with keyboard.pressed(Key.alt):
        keyboard.press("j")
        keyboard.release("j")
