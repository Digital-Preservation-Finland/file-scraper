"""Scraper for CSV file formats."""
import csv

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class CsvMeta(BaseMeta):
    """Scraper for CSV files."""

    _supported = {"text/csv": []}  # Supported mimetype
    _allow_versions = True           # Allow any version

    def __init__(self, csvfile, errors, messages, params=None):
        """
        Initialize for delimiter and separator info.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters: delimiter and separator
        """
        if params is None:
            params = {}
        self._csv_delimiter = params.get("delimiter", None)
        self._csv_separator = params.get("separator", None)
        self._csv_fields = params.get("fields", [])
        self._csv_first_line = None

        if self._csv_fields is None:
            self._csv_fields = []
        try:
            reader = csv.reader(csvfile)
            csvfile.seek(0)
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            if not self._csv_delimiter:
                self._csv_delimiter = dialect.delimiter
            if not self._csv_separator:
                self._csv_separator = dialect.lineterminator
            csv.register_dialect("new_dialect",
                                 delimiter=self._csv_delimiter,
                                 lineterminator=self._csv_separator,
                                 strict=True,
                                 doublequote=True)

            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect="new_dialect")
            self._csv_first_line = next(reader)

            if self._csv_fields and \
                    len(self._csv_fields) != len(self._csv_first_line):
                errors.append(
                    "CSV not well-formed: field counts in the given "
                    "header parameter and the CSV header don't match."
                )
                return

            for _ in reader:
                pass

        except csv.Error as exception:
            errors.append("CSV error on line %s: %s" %
                          (reader.line_num, exception))
        except UnicodeDecodeError:
            errors.append("Error reading file as CSV")
        else:
            messages.append("CSV file was checked successfully.")

    # pylint: disable=no-self-use
    # TODO hard-coded, is this ok? Anything does not seem to be actually
    #      the MIME type in this or other scrapers.
    @metadata()
    def mimetype(self):
        return "text/csv"

    @metadata()
    def version(self):
        """Return version."""
        return ""

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
