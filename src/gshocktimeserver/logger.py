import logging
from args import args

_logger = logging.getLogger(__name__)


class Logger:
    log_level = args.get().log_level

    logging.basicConfig(
        level=logging.INFO,  # log_level,
        handlers=[logging.StreamHandler()],
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    logging.basicConfig(level=logging.INFO)

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
