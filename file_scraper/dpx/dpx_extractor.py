"""DPX extractor"""

from dpx_validator.api import validate_file
from dpx_validator.messages import MessageType
from dpx_validator import __version__ as dpx_version

from file_scraper.base import BaseExtractor
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.logger import LOGGER


class DpxExtractor(BaseExtractor[DpxMeta]):
    """DPX extractor."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True

    def extract(self):
        """Scrape DPX."""

        valid, output, logs = validate_file(self.filename)

        for log in logs:
            msg_type, message = log
            if msg_type == MessageType.ERROR:
                self._errors.append(message)
            elif msg_type == MessageType.INFO:
                self._messages.append(message)
            else:
                self._errors.append(
                    "Unknown message type returned by "
                    "dpx_validator.api.validate_file"
                )
                LOGGER.error("Unknown message type returned by "
                             "dpx_validator.api.validate_file")
        if valid:
            self._messages.append("is valid")
            LOGGER.info(
                "dpx-validator validated the file: %s as valid",
                self.filename
            )
        else:
            LOGGER.info(
                "dpx-validator invalidated the file: %s", str(self.filename))

        self.streams = list(self.iterate_models(
            well_formed=valid, output=output, filename=self.filename))

        self._validate()

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {"dpx-validator": {"version": dpx_version}}
