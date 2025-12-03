"""Extractor for dng files using ExifTool """
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TypeVar
import exiftool
from exiftool.exceptions import ExifToolExecuteError

from file_scraper.base import BaseExtractor
from file_scraper.exiftool.exiftool_model import (
    ExifToolBaseMeta,
    ExifToolDngMeta,
)

EXIF_ERROR = "ExifTool:Error"


ExifToolMetaT = TypeVar("ExifToolMetaT", bound=ExifToolBaseMeta)


class ExifToolExtractorBase(BaseExtractor[ExifToolMetaT]):
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

        if exif_version := metadata.get("EXIF:ExifVersion"):
            # Check ExifVersion
            self._parse_exif_version(exif_version)

        self.streams = list(self.iterate_models(metadata=metadata))
        self._check_supported(allow_unav_version=True)

    def _parse_exif_version(self, exif_version):
        """Check that the Exif version is syntactically valid"""
        if len(exif_version) != 4:
            self._errors.append(
                f"ExifVersion '{exif_version}' is not 4 characters long"
            )

        if not exif_version.isdigit():
            self._errors.append(f"ExifVersion '{exif_version}' is not numeric")

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        with exiftool.ExifTool() as et:
            return {"ExifTool": {"version": et.version}}


class ExifToolDngExtractor(ExifToolExtractorBase[ExifToolDngMeta]):
    """Variables for scraping dng files."""

    _supported_metadata = [ExifToolDngMeta]
