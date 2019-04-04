"""Dummy scrapers."""
import os.path
from file_scraper.base import BaseScraper
from file_scraper.utils import metadata


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self.messages('Proper scraper was not found. '
                      'The file was not analyzed.')
        self._collect_elements()

    @metadata()
    def _stream_type(self):
        """Stream type is not known so return None."""
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
            self._errors.append('No filename given.')
        elif os.path.isfile(self.filename):
            self._messages.append('File %s was found.' % self.filename)
        else:
            self._errors.append('File %s does not exist.' % self.filename)
#        self._collect_elements()

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        if self.errors():
            return False
        return None

    @metadata()
    def _stream_type(self):
        """Stream type is not known so return None."""
        return None
