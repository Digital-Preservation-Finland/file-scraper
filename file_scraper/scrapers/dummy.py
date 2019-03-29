"""Dummy scrapers."""
import os.path
from file_scraper.base import BaseScraper


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self._collect_elements()
        self.messages('Proper scraper was not found. '
                      'The file was not analyzed.')

    def _s_stream_type(self):
        """Stram type is not known so return None."""
        return None

    @property
    def well_formed(self):
        """Well-formedness is not known so return None."""
        return None


class FileExists(BaseScraper):
    """Scraper for the case where file was not found."""

    def scrape_file(self):
        """Check if file exists."""
        if not self.filename:
            self.errors('No filename given.')
        elif os.path.isfile(self.filename):
            self.messages('File %s was found.' % self.filename)
        else:
            self.errors('File %s does not exist.' % self.filename)
        self._collect_elements()

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        if self.errors():
            return False
        return None

    def _s_stream_type(self):
        """Stream type is not known so return None."""
        return None
