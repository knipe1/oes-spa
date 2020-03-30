#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementing a default config for a logger. Provides a general logging system 
and using the default logging levels.

Usage: 
    from Logger import Logger
    logger = Logger(__name__)
    # then use logger obj as normal logger for messages
    logger.debug("debug message")
    # changing config requires access to logger.logger
    logger.logger.setLevel(logging.ERROR) #requires import logging.ERROR

Created on Sun Mar 29 12:21:03 2020

@author: hauke

TODO: Add metadata
"""

# official website
# https://docs.python.org/3/library/logging.html

# further descriptive videos
# https://www.youtube.com/watch?v=g8nQ90Hk328
# https://www.youtube.com/watch?v=-ARI4Cz-awo
# https://www.youtube.com/watch?v=jxmzY9soFXg

# Advanced techniques
# logger = logging.getLogger(__name__) --> __name__ is convention
#   will use another logger with a possible different config to write in 
#   different files, console output or something else.
# streamhandler
# logging.exception
# splitting of different setting to different handler (files or consoles)



# logging levels
# DEBUG — Detailed information, typically of interest only when diagnosing problems.
# INFO — Confirmation that things are working as expected.
# WARNING — An indication that something unexpected happened, or indicative of some problem in the near future (e.g. “disk space low”). The software is still working as expected.
# ERROR — Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL — A serious error, indicating that the program itself may be unable to continue running.

import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILENAME = "/home/hauke/IAF/oes-spectra-analysis-Homeversion/debug.log"
LOG_MODE = "w"
LOG_LEVEL = logging.DEBUG


# # config the logger
# # getting the (basic) root logger
# logger = logging.getLogger()

# # setting the debug level
# logger.setLevel(LOG_LEVEL)

# # removing all handler from previous sessions
# while len(logger.handlers):
#     logger.removeHandler(logger.handlers[0])

# # config the default handler
# fhandler = logging.FileHandler(filename = FILENAME, mode = LOG_MODE)
# #adding the format
# formatter = logging.Formatter(LOG_FORMAT)
# fhandler.setFormatter(formatter)
# # adding the configured handler
# logger.addHandler(fhandler)

# # testing the module and its behaviour
# # logger.debug("Debugging Nachricht")
# # logger.info("Info Nachricht")
# # logger.warning("Warnung")
# # logger.error("Error Nachricht")
# # logger.critical("Kritische Nachricht")


class Logger():
    def __init__(self, name, file=FILENAME, level = LOG_LEVEL, format = LOG_FORMAT, 
                 mode = LOG_MODE):
        
        """initialize the parent class ( == logging.Logger.__init__(self)"""
        
        # creating a new logger with file specific name
        self.logger = logging.getLogger(name)
        
        # setting the default logging level
        self.logger.setLevel(logging.DEBUG)
        
        
        # removing all handler from previous sessions
        while len(self.logger.handlers):
            self.logger.removeHandler(self.logger.handlers[0])

        # print(self.logger.getEffectiveLevel(), self.logger.handlers)
        # setting the logging level
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel(logging.DEBUG)
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel(level)
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel = level
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel(), level)
        # except:
        #     pass


        # setting the format
        formatter = logging.Formatter(LOG_FORMAT)
        
        # config the default handler
        fhandler = logging.FileHandler(filename = FILENAME, mode = LOG_MODE)
        # setting the logging level
        fhandler.setLevel(level)
        #adding the format
        fhandler.setFormatter(formatter)
        
        
        # # setting the logging level
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel(logging.DEBUG)
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel(level)
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel())
        #     self.logger.setLevel = level
        # except:
        #     pass
        # try:
        #     print(self.logger.getEffectiveLevel(), level)
        # except:
        #     pass
        
        # adding the configured handler
        self.logger.addHandler(fhandler)
        
    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra = extra)
    def info(self, msg, extra=None):
        self.logger.info(msg, extra = extra)
    def warning(self, msg, extra=None):
        self.logger.warning(msg, extra = extra)
    def error(self, msg, extra=None):
        self.logger.error(msg, extra = extra)
    def critical(self, msg, extra=None):
        self.logger.critical(msg, extra = extra)
    def exception(self, msg, extra=None):
        self.logger.exception(msg, extra = extra)

