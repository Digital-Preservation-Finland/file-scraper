"""Scraper for CSV file formats."""
from __future__ import unicode_literals

import csv
from io import open as io_open

import six

from file_scraper.base import BaseScraper
from file_scraper.csv.csv_model import CsvMeta

MODE = 't' if six.PY3 else 'b'


class CsvScraper(BaseScraper):
    """Scraper for CSV files."""

    _supported_metadata = [CsvMeta]
    _only_wellformed = True

    def __init__(self, filename, check_wellformed=True, params=None):
        """
        Initializer for the scraper.

        :filename: File path
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters: delimiter and separator
        """
        if params is None:
            params = {}
        super(CsvScraper, self).__init__(filename, check_wellformed, params)

    def scrape_file(self):
        """Scrape CSV file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        delimiter = self._params.get("delimiter", None)
        separator = self._params.get("separator", None)
        fields = self._params.get("fields", [])
        first_line = None
        try:
            with io_open(self.filename, "r"+MODE) as csvfile:
                try:
                    reader = csv.reader(csvfile)
                    csvfile.seek(0)
                    dialect = csv.Sniffer().sniff(csvfile.read(1024))
                    if not delimiter:
                        delimiter = dialect.delimiter
                    if not separator:
                        separator = dialect.lineterminator
                    csv.register_dialect(
                        "new_dialect",
                        # 'delimiter' accepts only byte strings on Python 2 and
                        # only Unicode strings on Python 3
                        delimiter=str(delimiter),
                        lineterminator=separator,
                        strict=True,
                        doublequote=True)

                    csvfile.seek(0)
                    reader = csv.reader(csvfile, dialect="new_dialect")
                    first_line = next(reader)

                    if fields and len(fields) != len(first_line):
                        self._errors.append(
                            "CSV not well-formed: field counts in the given "
                            "header parameter and the CSV header don't match."
                        )

                    # Read the whole file in case it contains errors. If there
                    # are any, an exception will be raised, triggering
                    # recording an error
                    for _ in reader:
                        pass

                except csv.Error as exception:
                    self._errors.append("CSV error on line %s: %s" %
                                        (reader.line_num, exception))
                except UnicodeDecodeError:
                    self._errors.append("Error reading file as CSV")
                else:
                    self._messages.append("CSV file was checked successfully.")

                # add metadata
                for md_class in self._supported_metadata:
                    self.streams.append(md_class({"delimiter": delimiter,
                                                  "separator": separator,
                                                  "fields": fields,
                                                  "first_line": first_line},
                                                 self._given_mimetype,
                                                 self._given_version))

        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                six.text_type(err))

        self._check_supported(allow_unap_version=True)
