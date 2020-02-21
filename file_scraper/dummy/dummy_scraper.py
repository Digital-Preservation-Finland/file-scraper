"""Dummy scrapers."""
from __future__ import unicode_literals

import os.path

from file_scraper.base import BaseScraper
from file_scraper.utils import decode_path
from file_scraper.dummy.dummy_model import DummyMeta


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self._messages.append("Proper scraper was not found. "
                              "The file was not analyzed.")
        self.streams.append(DummyMeta(errors=self._errors))

    @property
    def well_formed(self):
        """Well-formedness is not known: return None."""
        return None


class FileExists(BaseScraper):
    """Scraper for the case where file was not found."""

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
        self.streams.append(DummyMeta(errors=self._errors))

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        if self._errors:
            return False
        return None

class MimeScraper(BaseScraper):
    """
    Scraper to check if the predefined mimetype and version match with the
    resulted ones. This is run if the predefined mimetype mismatches with the
    resulted one, or if the version given by the user mismatches with the
    resulted one.
    """

    _MIME_DICT = {"application/gzip": ["application/warc",
                                       "application/x-internet-archive"]}

    def scrape_file(self):
        """No need to scrape anything, just compare data."""
        error = False
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return

        self._messages.append("MIME type check")

        mime = self._params.get("mimetype", "(:unav)")
        ver = self._params.get("version", "(:unav)")
        well = self._params.get("well_formed", False)
        pre_list = self._MIME_DICT.get(self._predefined_mimetype, [])

        if (mime == "(:unav)" and well) or \
                (mime != self._predefined_mimetype and mime not in pre_list):
            self._errors.append(
                "Predefined mimetype '{}' and resulted mimetype '{}' "
                "mismatch.".format(self._predefined_mimetype, mime))

        if self._predefined_version not in [ver, None]:
            self._errors.append(
                "Predefined version '{}' and resulted version '{}' "
                "mismatch.".format(self._predefined_version, ver))

        self.streams.append(DummyMeta(errors=self._errors))
