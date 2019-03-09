"""Scraper for CSV file formats
"""
import csv

from dpres_scraper.base import BaseScraper


class Csv(BaseScraper):
    """Scraper for CSV files
    """

    _supported = {'text/csv': []}

    def __init__(self, filename, mimetype, validation=True, params={}):
        """Initialize for delimiter and separator info
        """
        self._csv_delimiter = params.get('delimiter', None)
        self._csv_separator = params.get('separator', None)
        self._csv_first_line = None
        super(Csv, self).__init__(filename, mimetype, validation, params)

    def scrape_file(self):
        """Scrape CSV file
        """
        try:
            with open(self.filename, 'rb') as csvfile:

                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                if not self._csv_delimiter:
                    self._csv_delimiter = dialect.delimiter
                if not self._csv_separator:
                    self._csv_separator = dialect.lineterminator
                csv.register_dialect('new_dialect',
                                     delimiter=self._csv_delimiter,
                                     lineterminator=self._csv_separator)

                csvfile.seek(0)
                reader = csv.reader(csvfile, dialect='new_dialect')
                self._csv_first_line = reader.next()
                for _ in reader:
                    pass

        except csv.Error as exception:
            self.errors("CSV error on line %s: %s" %
                        (reader.line_num, exception))
        else:
            self.messages("CSV file was scraped successfully.")
        finally:
            self._collect_elements()


    def _s_delimiter(self):
        """Return delimiter
        """
        return self._csv_delimiter

    def _s_separator(self):
        """Return separator
        """
        return self._csv_separator

    def _s_first_line(self):
        """Return first line
        """
        return self._csv_first_line

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'char'
