"""Scraper for CSV file formats."""
from __future__ import unicode_literals


from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.utils import metadata


class CsvMeta(BaseMeta):
    """Metadata model for CSV files."""

    _supported = {"text/csv": []}  # Supported mimetype
    _allow_versions = True           # Allow any version

    def __init__(self, well_formed, params):
        """
        Initialize for delimiter and separator info.

        :well_formed: Well-formed status from scraper
        :params: A dict containing the following keys:
                 delimiter:  the field delimiter used in the file
                 separator:  the line separator
                 fields:     list of columns
                 first_line: contents of the first line
        """
        # Check that a proper parameter dict was supplied
        if any((key not in params for key in ["delimiter", "separator",
                                              "fields", "first_line"])):
            raise ValueError("CsvMeta must be given a dict containing keys "
                             "'delimiter', 'separator', 'fields' and "
                             "'first_line' as a parameter.")

        self._well_formed = well_formed
        self._csv_delimiter = params["delimiter"]
        self._csv_separator = params["separator"]
        self._csv_fields = params["fields"]
        self._csv_first_line = params["first_line"]

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "text/csv" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """
        Return version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        return UNAP if self._well_formed else UNAV

    @metadata()
    def delimiter(self):
        """Return delimiter."""
        return self._csv_delimiter

    @metadata()
    def separator(self):
        """Return separator."""
        return self._csv_separator

    @metadata()
    def first_line(self):
        """Return first line."""
        return self._csv_first_line

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV
