import logging.handlers
import os
import sys
import time
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from constants.configurations import LOG


class MQTTLogger(logging.getLoggerClass()):
    def __init__(self, name):
        super().__init__(name)

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.trace):
            self._log(logging.trace, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)


class GenAILogger(object):
    def __init__(self, **kwargs):
        self.LOG_MODULE_NAME = kwargs.get("module", "GRAD_EVAL")
        self.LOG_BASE_PATH = kwargs.get("base_path", LOG.LOG_BASE_PATH)
        self.LOG_FILE = kwargs.get("file_name", LOG.FILE_NAME)
        self.LOG_HANDLERS = kwargs.get("handlers", LOG.LOG_HANDLERS)
        self.LOG_MAX_SIZE = kwargs.get("file_max_size", int(LOG.FILE_MAX_SIZE) * 1024 * 1024)
        self.LOG_BACKUP_COUNT = kwargs.get("file_backup_count", LOG.FILE_BACKUP_COUNT)
        self.LOG_LEVEL = kwargs.get("log_level", LOG.LOG_LEVEL)
        if not os.path.exists(self.LOG_BASE_PATH):
            os.makedirs(self.LOG_BASE_PATH)

        logging.setLoggerClass(MQTTLogger)
        self.logger = logging.getLogger(self.LOG_MODULE_NAME)
        self.logger.setLevel(self.LOG_LEVEL)

        self.initialize_logger()

    def initialize_logger(self):
        logging.trace = logging.DEBUG - 5
        logging.addLevelName(logging.DEBUG - 5, 'TRACE')

        if self.LOG_LEVEL == 'DEBUG' or self.LOG_LEVEL == 'TRACE':
            _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - '
                                           '%(lineno)d - %(message)s')
        else:
            _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if 'file' in self.LOG_HANDLERS:
            # Adding the log file handler to the logger
            _file_handler = logging.FileHandler(self.LOG_FILE + "." + time.strftime("%Y-%m-%d"),encoding="utf-8")
            _file_handler.setFormatter(_formatter)
            self.logger.addHandler(_file_handler)

        if 'rotating' in self.LOG_HANDLERS:
            # Adding the log file handler to the logger
            _rotating_file_handler = RotatingFileHandler(filename=self.LOG_FILE,
                                                         maxBytes=self.LOG_MAX_SIZE,
                                                         backupCount=self.LOG_BACKUP_COUNT,encoding="utf-8")
            _rotating_file_handler.setFormatter(_formatter)
            self.logger.addHandler(_rotating_file_handler)

        if 'console' in self.LOG_HANDLERS:
            # Adding the log Console handler to the logger
            _console_handler = StreamHandler(sys.stdout)
            _console_handler.setFormatter(_formatter)
            self.logger.addHandler(_console_handler)

    def get_logger(self):
        return self.logger


logger = GenAILogger().get_logger()
