"""DPX scraper"""

from dpx_validator.api import validate_file
from dpx_validator.messages import MessageType
from dpx_validator import __version__ as dpx_version

from file_scraper.base import BaseScraper
from file_scraper.dpx.dpx_model import DpxMeta


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True

    def scrape_file(self):
        """Scrape DPX."""

        valid, output, logs = validate_file(self.filename, log=True)

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
        if valid:
            self._messages.append("is valid")

        self.streams = list(self.iterate_models(
            well_formed=valid, output=output, filename=self.filename))

        self._check_supported()

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNKN.
        """
        return {"dpx-validator": {"version": dpx_version}}
