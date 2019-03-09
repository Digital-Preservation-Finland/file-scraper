"""Dummy scrapers
"""
import os.path
from dpres_scraper.base import BaseScraper


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found.
    """

    def scrape_file(self):
        """No need to scrape anything, just collect.
        """
        self._collect_elements()
        self.messages('Proper scraper was not found. '
                      'The file was not scraped.')

    def _s_stream_type(self):
        """We don't know the stream type
        """
        return None

    @property
    def well_formed(self):
        """We don't know the well-formed result
        """
        return None


class FileExists(BaseScraper):
    """Scraper for the case where file was not found.
    """

    def scrape_file(self):
        """Check if file exists
        """
        if os.path.isfile(self.filename):
            self.messages('File %s was found.' % self.filename)
        else:
            self.errors('File %s does not exist.' % self.filename)
        self._collect_elements()

    @property
    def well_formed(self):
        """Let's give the actual decision to the real scrapers.
        """
        return None

    def _s_stream_type(self):
        """We don't know the stream type
        """
        return None
