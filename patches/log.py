import logging
import os

import google.auth


_LOG_TO_FILE_ENV = os.getenv("KAGGLE_LOG_TO_FILE")


class _LogFormatter(logging.Formatter):
    """A logging formatter which truncates long messages."""

    _MAX_LOG_LENGTH = 10000  # Be generous, not to truncate long backtraces.

    def format(self, record):
        msg = super(_LogFormatter, self).format(record)
        return msg[:_LogFormatter._MAX_LOG_LENGTH] if msg else msg

# TODO(vimota): Clean this up once we're using python 3.8 and can use
# (https://github.com/python/cpython/commit/dde9fdbe453925279ac3d2a6a72102f6f9ef247c)
# Right now, making the logging module display the intended frame's information
# when the logging calls (info, warn, ...) are wrapped (as is the case in our
# Log class) involves fragile logic.
class _Logger(logging.Logger):

    # This is a copy of logging.Logger.findCaller with the filename ignore
    # set expanded to include the current filename (".../log.py").
    # Copyright 2001-2015 by Vinay Sajip. All Rights Reserved.
    # License: https://github.com/python/cpython/blob/ce9e62544571e7ade7186697d5dd065fb4c5243f/LICENSE
    def findCaller(self, stack_info=False):
        f = logging.currentframe()
        f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename in _ignore_srcfiles:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv


_srcfile = os.path.normcase(_Logger.findCaller.__code__.co_filename)
_ignore_srcfiles = (_srcfile, logging._srcfile)

class Log:
    """ Helper aggregate for all things related to logging activity. """

    _GLOBAL_LOG = logging.getLogger("")
    _initialized = False

    # These are convenience helpers. For performance, consider saving Log.get_logger() and using that
    @staticmethod
    def critical(msg, *args, **kwargs):
        Log._GLOBAL_LOG.critical(msg, *args, **kwargs)

    @staticmethod
    def fatal(msg, *args, **kwargs):
        Log._GLOBAL_LOG.fatal(msg, *args, **kwargs)

    @staticmethod
    def exception(msg, *args, **kwargs):
        Log._GLOBAL_LOG.exception(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        Log._GLOBAL_LOG.error(msg, *args, **kwargs)

    @staticmethod
    def warn(msg, *args, **kwargs):
        Log._GLOBAL_LOG.warn(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        Log._GLOBAL_LOG.warning(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        Log._GLOBAL_LOG.debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        Log._GLOBAL_LOG.info(msg, *args, **kwargs)

    @staticmethod
    def set_level(loglevel):
        if isinstance(loglevel, int):
            Log._GLOBAL_LOG.setLevel(loglevel)
            return
        elif isinstance(loglevel, str):
            # idea from https://docs.python.org/3.5/howto/logging.html#logging-to-a-file
            numeric_level = getattr(logging, loglevel.upper(), None)
            if isinstance(numeric_level, int):
                Log._GLOBAL_LOG.setLevel(numeric_level)
                return

        raise ValueError('Invalid log level: %s' % loglevel)

    @staticmethod
    def _static_init():
        if Log._initialized:
            return

        logging.setLoggerClass(_Logger)
        # The root logger's type is unfortunately (and surprisingly) not affected by
        # `setLoggerClass`. Monkey patch it instead. TODO(vimota): Remove this, see the TODO
        # associated with _Logger.
        logging.RootLogger.findCaller = _Logger.findCaller
        log_to_file = _LOG_TO_FILE_ENV.lower() in ("yes", "true", "t", "1") if _LOG_TO_FILE_ENV is not None else True
        if log_to_file:
            handler = logging.FileHandler(filename='/tmp/kaggle.log', mode='w')
        else:
            handler = logging.StreamHandler()
        
        # ".1s" is for the first letter: http://stackoverflow.com/a/27453084/1869.
        format_string = "%(asctime)s %(levelname).1s %(process)d %(filename)s:%(lineno)d] %(message)s"
        handler.setFormatter(_LogFormatter(format_string))
        logging.basicConfig(level=logging.INFO, handlers=[handler])
        Log._initialized = True

Log._static_init()