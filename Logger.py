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

logging levels
DEBUG — Detailed information, typically of interest only when diagnosing problems.
INFO — Confirmation that things are working as expected.
WARNING — An indication that something unexpected happened, or indicative of some problem in the near future (e.g. “disk space low”). The software is still working as expected.
ERROR — Due to a more serious problem, the software has not been able to perform some function.
CRITICAL — A serious error, indicating that the program itself may be unable to continue running.

official website
https://docs.python.org/3/library/logging.html

Created on Sun Mar 29 12:21:03 2020

@author: hauke
"""

# TODO: Add metadata
# TODO: Add streamhandler?

# further descriptive videos
# Logging module: https://www.youtube.com/watch?v=g8nQ90Hk328
# Logging module (simple): https://www.youtube.com/watch?v=-ARI4Cz-awo
# Logging module (advanced): https://www.youtube.com/watch?v=jxmzY9soFXg

# Advanced techniques
# logger = logging.getLogger(__name__) --> __name__ is convention
#   will use another logger with a possible different config to write in 
#   different files, console output or something else.
# streamhandler:
# splitting of different setting to different handler (files or consoles)


# standard libs
import logging

# local modules/libs
import modules.Universal as uni
from dialog_messages import information_LogFileNotFound

class Logger():
    """
    A class used to implement a general logger for each module.

    This class provides a universal logger that can be used for logging into
    the same file from different modules.
    
    Usage: 
        from Logger import Logger
        logger = Logger(__name__)
        # then use logger obj as normal logger for messages
        logger.debug("debug message")
        # changing config requires access to logger.logger
        logger.logger.setLevel(logging.ERROR) #requires import logging.ERROR
    
    Attributes
    ----------
    level : int
        The level of Logging (default logging.DEBUG)
    format : str
        Entries are formatted according to this format
        (default %(asctime)s - %(name)s - %(levelname)s - %(message)s).
    filename : str
        Logs are written to this file (default defined in config.log->FILE
                                       ->LOG_FILE)
    mode : str
        The logger opens the logfile in this mode. Options are: w, a 
        (default w). 
        See also: https://docs.python.org/3/library/functions.html#open

    Methods
    -------
    debug(msg: str, extra=None)
         Writing the message to the log with level DEBUG.
    info(msg: str, extra=None)
         Writing the message to the log with level INFO.
    warning(msg: str, extra=None)
         Writing the message to the log with level WARNING.
    error(msg: str, extra=None)
         Writing the message to the log with level ERROR.
    exception(msg: str, extra=None)
         Writing the message to the log with level ERROR inclusive Traceback.
    critical(msg: str, extra=None)
         Writing the message to the log with level CRITICAL.
    """
    
    config = uni.load_config()
    FILE = config["FILE"]
    level = logging.DEBUG
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    filename = FILE["LOG_FILE"]
    mode = "w"
    defaultFilename = "./debug.log"
    showedFileNotFound = False
    
    def __init__(self, name: str):
        """
        Parameters
        ----------
        name : str
            The name used to determine the logger object. Please consider
            __name__ as common name to distinguish the different entries
            of the different modules. They are then named in the logs.

        Returns
        -------
        None.

        """
        
        # Setting up the logger with the default configuration.
        self.logger = logging.getLogger(name)   # get or create the logger
        self.logger.setLevel(self.level)
        
        # removing all handler from previous sessions to set up a clean logger
        while len(self.logger.handlers):
            self.logger.removeHandler(self.logger.handlers[0])


        
        # config a file handler
        try:
            fhandler = logging.FileHandler(filename = self.filename, 
                                           mode = self.mode)
        except FileNotFoundError:
            # Show the information about the wrong path of the log.file just
            # once
            if not Logger.showedFileNotFound:
                information_LogFileNotFound(self.defaultFilename)
                Logger.showedFileNotFound = True
            # set the default log.file
            fhandler = logging.FileHandler(filename = self.defaultFilename, 
                                           mode = self.mode)
        
        fhandler.setLevel(self.level)
        
        # config the format of the handler
        formatter = logging.Formatter(self.format)
        fhandler.setFormatter(formatter)
        
        # the handler can now log messages
        self.logger.addHandler(fhandler)
        
    def debug(self, msg: str, extra=None):
        """
        Writing the message to the log with level DEBUG.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.debug(msg, extra = extra)
        
    def info(self, msg: str, extra=None):
        """
        Writing the message to the log with level INFO.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.info(msg, extra = extra)
        
    def warning(self, msg: str, extra=None):
        """
        Writing the message to the log with level WARNING.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.warning(msg, extra = extra)
        
    def error(self, msg, extra=None):
        """
        Writing the message to the log with level ERROR.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.error(msg, extra = extra)
        
    def critical(self, msg: str, extra=None):
        """
        Writing the message to the log with level CRITICAL.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.critical(msg, extra = extra)
        
    def exception(self, msg, extra=None):
        """
        Writing the message to the log with level ERROR inclusive Traceback.

        Parameters
        ----------
        msg : str
            This string will appear inside the log.
        extra : TYPE, optional
            Additional arguments according to the docs of the logging module. 
            The default is None.

        Returns
        -------
        None.

        """
        
        self.logger.exception(msg, extra = extra)

