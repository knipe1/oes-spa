#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is meant to emulate key-presses.
Can be extended to emulate mouse clicks.

Created on Fri Feb 21 09:14:12 2020

@author: Hauke Wernecke
"""


# third-party libs
from pynput.keyboard import Key, Controller
from time import sleep

PAUSE = 2.;


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
    Emulates a alt+j press after a pause.
    Often used as a thread to accept a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE)
    with keyboard.pressed(Key.alt):
        # keyboard.press("j")
        # keyboard.release("j")
        keyboard.press("y")
        keyboard.release("y")

def key_select_file(iterations):
    """
    Emulates a alt+j press after a pause.
    Often used as a thread to accept a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE)
    with keyboard.pressed(Key.shift_l):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        # windows (next 2 linies outcommented)
        # keyboard.press(Key.tab)
        # keyboard.release(Key.tab)
    # linux (next 3 linies not outcommented)
    keyboard.press(Key.down)
    keyboard.release(Key.down)
    keyboard.press(Key.down)
    keyboard.release(Key.down)
    with keyboard.pressed(Key.shift_l):
        for i in range(iterations):
            keyboard.press(Key.down)
            keyboard.release(Key.down)
        keyboard.press(Key.up)
        keyboard.release(Key.up)
        # linux (next 2 linies outcommented)
        # keyboard.press(Key.up)
        # keyboard.release(Key.up)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def key_arbitrary(text):
    """
    Emulates a key presses of arbitrary text after a pause.
    Often used as a thread to name something in a native file dialog.

    Returns
    -------
    None.

    """
    keyboard = Controller()
    sleep(PAUSE*0.9)
    keyboard.type(text)
