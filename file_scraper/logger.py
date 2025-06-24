"""
The logging component for file-scraper
"""
import logging


LOGGER = logging.getLogger("file-scraper")


def enable_logging(level=logging.DEBUG):
    """
    Enable logging at given level. Logs will be printed to stderr.

    This will also configure the root logger, which means that logs from other
    Python libraries will be printed according to the selected level.
    """
    logging.basicConfig(level=level, force=True)
