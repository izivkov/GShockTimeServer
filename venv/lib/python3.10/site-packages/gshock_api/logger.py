import logging

_logger = logging.getLogger(__name__)

class Logger:
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        logging.basicConfig(
            level=self.log_level,
            handlers=[logging.StreamHandler()],
            format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
        )

    def error(self, *args):
        _logger.error(args)

    def info(self, *args):
        _logger.info(args)

    def debug(self, *args):
        _logger.debug(args)

    def warn(self, *args):
        _logger.warn(args)

    def warning(self, *args):
        _logger.warn(args)

logger = Logger()
