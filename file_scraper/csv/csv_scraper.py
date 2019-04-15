"""Scraper for CSV file formats."""
from file_scraper.base import BaseScraper
from file_scraper.csv.csv_model import CsvMeta


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
        try:
            with open(self.filename, "r") as csvfile:
                for md_class in self._supported_metadata:
                    self.streams.append(md_class(csvfile, self._errors,
                                                 self._messages, self._params))
        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                str(err))
