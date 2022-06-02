"""Scraper for dng files using ExifTool """

from __future__ import unicode_literals

import exiftool

from file_scraper.base import BaseScraper
from file_scraper.exiftool.exiftool_model import ExifToolDngMeta


class ExifToolScraperBase(BaseScraper):
    """
    Scraping methods for the ExifTool scraper
    """

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize ExifTool base scraper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters needed for the scraper
        """
        super(ExifToolScraperBase, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    def scrape_file(self):
        """
        Scrape data from file.
        """

        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(self.filename)

        if "ExifTool:Error" in metadata:
            self._errors.append(metadata["ExifTool:Error"])
        else:
            self._messages.append("The file was analyzed successfully.")

        self.streams = list(self.iterate_models(metadata=metadata))
        self._check_supported(allow_unav_version=True)


class ExifToolDngScraper(ExifToolScraperBase):
    """Variables for scraping dng files."""

    _supported_metadata = [ExifToolDngMeta]
