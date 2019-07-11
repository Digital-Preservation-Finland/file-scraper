"""Dummy scrapers."""
from __future__ import unicode_literals

import os.path

from file_scraper.base import BaseScraper
from file_scraper.utils import decode_path
from file_scraper.dummy.dummy_model import DummyMeta


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    _supported_metadata = [DummyMeta]

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self._messages.append("Proper scraper was not found. "
                              "The file was not analyzed.")
        self.streams.append(DummyMeta(self._errors))

    @property
    def well_formed(self):
        """Well-formedness is not known: return None."""
        return None


class FileExists(BaseScraper):
    """Scraper for the case where file was not found."""

    _supported_metadata = [DummyMeta]

    def scrape_file(self):
        """Check if file exists."""
        if not self.filename:
            self._errors.append("No filename given.")
        elif os.path.isfile(self.filename):
            self._messages.append(
                "File {} was found.".format(decode_path(self.filename))
            )
        else:
            self._errors.append(
                "File {} does not exist.".format(decode_path(self.filename))
            )
        self.streams.append(DummyMeta(self._errors))

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        if self._errors:
            return False
        return None
