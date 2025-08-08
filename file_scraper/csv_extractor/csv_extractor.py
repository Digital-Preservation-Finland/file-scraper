"""Extractor for CSV file formats."""

import csv
from io import open as io_open

from file_scraper.base import BaseExtractor
from file_scraper.csv_extractor.csv_model import CsvMeta
from file_scraper.logger import LOGGER


class CsvExtractor(BaseExtractor):
    """Extractor for CSV files."""

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
                dialect = csv.Sniffer().sniff(csvfile.read(100*1024))
                LOGGER.debug(
                    "csv.Sniffer detected dialect with "
                    "delimiter: %s, line terminator: %s, quotechar: %s",
                    dialect.delimiter, dialect.lineterminator,
                    dialect.quotechar
                )
                if delimiter is None:
                    LOGGER.debug(
                        "Using auto-detected delimeter: %s", dialect.delimiter
                    )
                    delimiter = dialect.delimiter
                if separator is None:
                    LOGGER.debug(
                        "Using auto-detected separator: %s",
                        dialect.lineterminator
                    )
                    separator = dialect.lineterminator
                if quotechar is None:
                    LOGGER.debug(
                        "Using auto-detected quotechar: %s", dialect.quotechar
                    )
                    quotechar = dialect.quotechar

            # Default quotechar according to csv module documentation is '"'.
            if quotechar is None:
                quotechar = "\""

            csv.register_dialect(
                "new_dialect",
                delimiter=delimiter,
                lineterminator=separator,
                quotechar=quotechar,
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
                self._errors.append(
                    f"CSV error on line {reader.line_num}: {exception}")
            else:
                self._errors.append(f"CSV error: {exception}")
        except (UnicodeError,
                UnicodeDecodeError,
                StopIteration,
                LookupError) as exception:
            self._errors.append(f"Error reading file as CSV: {exception}")
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

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        return {}
