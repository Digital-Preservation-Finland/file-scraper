"""Extractor for dng files using ExifTool """
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal
import exiftool
from exiftool.exceptions import ExifToolExecuteError

from file_scraper.base import BaseExtractor
from file_scraper.exiftool.exiftool_model import ExifToolDngMeta

EXIF_ERROR = "ExifTool:Error"


class ExifToolExtractorBase(BaseExtractor):
    """
    Scraping methods for the ExifTool extractor
    """

    def __init__(
        self,
        filename: Path,
        mimetype: str,
        version: str | None = None,
        params: dict | None = None,
    ) -> None:
        """
        Initialize ExifTool base extractor.

        :param filename: File path
        :param mimetype: Predefined mimetype
        :param version: Predefined file format version
        :param params: Extra parameters needed for the extractor
        """
        super().__init__(
            filename=filename,
            mimetype=mimetype,
            version=version,
            params=params,
        )

    @property
    def well_formed(self) -> Literal[False] | None:
        """ExifTool is not able to check well-formedness.

        :returns: False if ExifTool can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def extract(self) -> None:
        """
        Scrape data from file.
        """

        try:
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(self.filename)
            if EXIF_ERROR in metadata:
                self._errors.append(metadata[EXIF_ERROR])
            else:
                self._messages.append("The file was analyzed successfully.")
        except AttributeError:
            with exiftool.ExifToolHelper() as et:
                try:
                    metadata = et.get_metadata(str(self.filename))[0]
                except ExifToolExecuteError as eee:
                    metadata = json.loads(eee.stdout)[0]
                    self._errors.append(metadata[EXIF_ERROR])
                else:
                    self._messages.append(
                        "The file was analyzed successfully.")

        self.streams = list(self.iterate_models(metadata=metadata))
        self._check_supported(allow_unav_version=True)

    def tools(self) -> dict:
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software.
        """

        with exiftool.ExifTool() as et:
            return {"ExifTool": {"version": et.version}}


class ExifToolDngExtractor(ExifToolExtractorBase):
    """Variables for scraping dng files."""

    _supported_metadata = [ExifToolDngMeta]
