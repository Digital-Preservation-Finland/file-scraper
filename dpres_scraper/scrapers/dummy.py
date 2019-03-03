"""Dummy scraper
"""
from dpres_scraper.base import BaseScraper


class Dummy(BaseScraper):
    """Make sure that stream is created for all files
    """

    def scrape_file(self):
        """No need to scrape anything, just collect.
        """
        self._collect_elements()
        self.messages('The file was scraped.')
        pass

    def _s_stream_type(self):
        """We don't know the stream type
        """
        return None

    @property
    def well_formed(self):
        """We don't know the well-formed result
        """
        return None
