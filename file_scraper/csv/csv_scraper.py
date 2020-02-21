"""Scraper for CSV file formats."""
from __future__ import unicode_literals

import csv
from io import open as io_open

import six

from file_scraper.base import BaseScraper
from file_scraper.csv.csv_model import CsvMeta


class CsvScraper(BaseScraper):
    """Scraper for CSV files."""

    _supported_metadata = [CsvMeta]

    def scrape_file(self):
        """Scrape CSV file."""

        fields = self._params.get("fields", [])
        charset = self._params.get("charset", None)

        # These are read later if the scraping process is successful
        csvfile = None
        first_line = None
        delimiter = None
        separator = None
        reader = None

        try:
            csvfile = self._open_csv_file(charset)

            delimiter = self._params.get("delimiter", None)
            separator = self._params.get("separator", None)

            if delimiter is None or separator is None:
                # Sniffer may not be able to find any delimiter or separator
                # with the default dialect. This will raise an exception.
                # Therefore, sniffing should be skipped totally, if the
                # characters are given as a parameter.
                dialect = csv.Sniffer().sniff(csvfile.read(4096))
                if delimiter is None:
                    delimiter = dialect.delimiter
                if separator is None:
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

            first_row = next(reader)
            if six.PY2 and charset is not None:
                first_line = [item.decode(charset) for item in first_row]
            else:
                first_line = first_row

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

        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                six.text_type(err))
        except csv.Error as exception:
            if reader is not None:
                self._errors.append("CSV error on line %s: %s" %
                                    (reader.line_num, exception))
            else:
                self._errors.append("CSV error: %s" % exception)
        except (UnicodeError, UnicodeDecodeError, StopIteration) as exception:
            self._errors.append("Error reading file as CSV: %s" % exception)
        else:
            self._messages.append("CSV file was checked successfully.")
        finally:
            if csvfile:
                csvfile.close()

        self.iterate_models(params={"delimiter": delimiter,
                                    "separator": separator,
                                    "fields": fields,
                                    "first_line": first_line})
        
        self._check_supported(allow_unap_version=True)

    def _open_csv_file(self, charset):
        """
        Open the file in mode dependent on the python version.

        :returns: handle to the newly-opened file
        :raises: IOError if the file cannot be read
        """
        if six.PY2:
            return io_open(self.filename, "rb")
        return io_open(self.filename, "rt", encoding=charset)
