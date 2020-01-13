"""Scraper for CSV file formats."""
from __future__ import unicode_literals


from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class CsvMeta(BaseMeta):
    """Metadata model for CSV files."""

    _supported = {"text/csv": []}  # Supported mimetype
    _allow_versions = True           # Allow any version

    def __init__(self, errors, params):
        """
        Initialize for delimiter and separator info.

        :params: A dict containing the following keys:
                 delimiter:  the field delimiter used in the file
                 separator:  the line separator
                 fields:     list of columns
                 first_line: contents of the first line
        """
        # Check that a proper parameter dict was supplied
        if any([key not in params for key in ["delimiter", "separator",
                                              "fields", "first_line"]]):
            raise ValueError("CsvMeta must be given a dict containing keys "
                             "'delimiter', 'separator', 'fields' and "
                             "'first_line' as a parameter.")

        self._csv_delimiter = params["delimiter"]
        self._csv_separator = params["separator"]
        self._csv_fields = params["fields"]
        self._csv_first_line = params["first_line"]
        super(CsvMeta, self).__init__(errors)

    @metadata()
    def mimetype(self):
        """Return mimetype"""
        if not self._errors:
            return "text/csv"
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
        if not self._errors:
            return "(:unap)"
        return "(:unav)"

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
        """Return file type."""
        return "text"
