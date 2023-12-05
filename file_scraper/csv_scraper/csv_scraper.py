"""Scraper for CSV file formats."""

import csv
from io import open as io_open

from file_scraper.base import BaseScraper
from file_scraper.csv_scraper.csv_model import CsvMeta


class CsvScraper(BaseScraper):
    """Scraper for CSV files."""

    _supported_metadata = [CsvMeta]

    # Raise csv field size limit to 1 MB
    csv.field_size_limit(1048576)

    # pylint: disable=too-many-branches
    def scrape_file(self):
        """Scrape CSV file."""

        fields = self._params.get("fields", [])
        charset = self._params.get("charset", None)

        # These are read later if the scraping process is successful
        csvfile = None
        first_line = None
        delimiter = None
        separator = None
        quotechar = None
        reader = None

        try:
            csvfile = self._open_csv_file(charset)

            delimiter = self._params.get("delimiter", None)
            separator = self._params.get("separator", None)
            quotechar = self._params.get("quotechar", None)

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
                if quotechar is None:
                    quotechar = dialect.quotechar

            # Default quotechar according to csv module documentation is '"'.
            if quotechar is None:
                quotechar = "\""

            csv.register_dialect(
                "new_dialect",
                # 'delimiter' and 'quotechar' accept only byte strings on
                # Python 2 and only Unicode strings on Python 3
                delimiter=str(delimiter),
                lineterminator=separator,
                quotechar=str(quotechar),
                strict=True,
                doublequote=True)

            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect="new_dialect")

            first_row = next(reader)
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

        except OSError as err:
            self._errors.append("Error when reading the file: " +
                                str(err))
        except csv.Error as exception:
            if reader is not None:
                self._errors.append("CSV error on line %s: %s" %
                                    (reader.line_num, exception))
            else:
                self._errors.append("CSV error: %s" % exception)
        except (UnicodeError,
                UnicodeDecodeError,
                StopIteration,
                LookupError) as exception:
            self._errors.append("Error reading file as CSV: %s" % exception)
        else:
            self._messages.append("CSV file was checked successfully.")
        finally:
            if csvfile:
                csvfile.close()

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, params={"delimiter": delimiter,
                                                  "separator": separator,
                                                  "quotechar": quotechar,
                                                  "fields": fields,
                                                  "first_line": first_line}))
        self._check_supported(allow_unap_version=True)

    def _open_csv_file(self, charset):
        """
        Open the file in mode dependent on the python version.

        :charset: File encoding
        :returns: handle to the newly-opened file
        :raises: IOError if the file cannot be read
        """
        return io_open(self.filename, "rt", encoding=charset)
