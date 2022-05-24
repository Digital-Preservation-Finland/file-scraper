""" """

from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.exiftool.exiftool_model import ExifToolDngMeta
import exiftool


class ExifToolScraperBase(BaseScraper):
    """
    Scraping methods for the ExifTool scraper
    """

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        """
        super(ExifToolScraperBase, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    def scrape_file(self):
        """

        """

        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(self.filename)

        self.streams = list(self.iterate_models(metadata=metadata))
        self._check_supported(allow_unav_version=True)


class ExifToolDngScraper(ExifToolScraperBase):
    """Variables for scraping dng files."""

    _supported_metadata = [ExifToolDngMeta]

