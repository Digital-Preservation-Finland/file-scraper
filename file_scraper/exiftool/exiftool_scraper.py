"""Scraper for dng files using ExifTool """

import json
from pathlib import Path
from typing import Optional
import exiftool

from file_scraper.base import BaseScraper
from file_scraper.exiftool.exiftool_model import ExifToolDngMeta


class ExifToolScraperBase(BaseScraper):
    """
    Scraping methods for the ExifTool scraper
    """

    def __init__(self, filename: Optional[Path], mimetype, version=None,
                 params=None):
        """
        Initialize ExifTool base scraper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters needed for the scraper
        """
        super().__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    @property
    def well_formed(self):
        """ExifTool is not able to check well-formedness.

        :returns: False if ExifTool can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def scrape_file(self):
        """
        Scrape data from file.
        """

        try:
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(self.filename)
            if "ExifTool:Error" in metadata:
                self._errors.append(metadata["ExifTool:Error"])
            else:
                self._messages.append("The file was analyzed successfully.")
        except AttributeError:
            with exiftool.ExifToolHelper() as et:
                from exiftool.exceptions import ExifToolExecuteError
                try:
                    metadata = et.get_metadata(str(self.filename))[0]
                except ExifToolExecuteError as eee:
                    metadata = json.loads(eee.stdout)[0]
                    self._errors.append(metadata["ExifTool:Error"])
                else:
                    self._messages.append(
                        "The file was analyzed successfully.")

        self.streams = list(self.iterate_models(metadata=metadata))
        self._check_supported(allow_unav_version=True)

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software.
        """

        with exiftool.ExifTool() as et:
            return {"ExifTool": {"version": et.version}}


class ExifToolDngScraper(ExifToolScraperBase):
    """Variables for scraping dng files."""

    _supported_metadata = [ExifToolDngMeta]
