"""File metadata scraper."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dpres_file_formats.graders import file_formats
from dpres_file_formats.graders import grade as file_formats_grade

from file_scraper.base import BaseDetector, BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.state import Mimetype
from file_scraper.detectors import ExifToolDetector, MagicCharset
from file_scraper.dummy.dummy_model import UserDefinedMeta
from file_scraper.exceptions import (
    DirectoryIsNotScrapable,
    FileIsNotScrapable,
    FileNotFoundIsNotScrapable,
    InvalidMimetype,
    InvalidVersionForMimetype,
)
from file_scraper.iterator import iter_detectors, iter_extractors
from file_scraper.jhove.jhove_extractor import JHoveUtf8Extractor
from file_scraper.logger import LOGGER
from file_scraper.textfile.textfile_extractor import TextfileExtractor
from file_scraper.utils import (
    hexdigest,
)
from file_scraper.metadata import generate_metadata_dict

LOSE = (None, UNAV, "")


class Scraper:
    """File indentifier and scraper."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, filename: str | os.PathLike, **kwargs: Any) -> None:
        """Initialize scraper.

        The scraper checks filepath validity in initialization and
        throws errors if the filepath given is not valid.

        :param filepath: File path
        :param kwargs: Extra arguments for certain scrapers.
        :raises FileNotFoundError: The filepath given was not found.
        :raises FileIsNotScrapable: The filepath given doesn't point to
            a regular file.
        :raises IsADirectoryError: The filepath given was a directory instead
            of a file.
        """
        self.input_path = filename
        self.path = _validate_path(filename)
        # TODO taking in arbitraty amount of kwargs makes it hard to document
        # and define what keyword arguments are actually accepted to
        # file-scraper. Part of the ticket TPASPKT-1540 to clean file-scraper
        # parameters.
        self._kwargs = kwargs
        self.clear()
        self._parameter_validation()

    @property
    def filename(self) -> bytes:
        """Return file path as byte string.

        This maintains backwards compatibility for tools expecting file path
        as string. `path` should be preferred instead for newer code.
        """
        return os.fsencode(self.path)

    @property
    def well_formed(self) -> bool | None:
        return self._well_formed

    @well_formed.setter
    def well_formed(self, value: bool | None) -> None:
        if self._well_formed is False and value is not False:
            raise ValueError(
                "Well_formedness cannot be changed to any other value after "
                "getting set as False."
            )
        self._well_formed = value

    # TODO move initialization to init if detect_filetype no longer needs to
    # reset the scraper class.
    # pylint: disable=attribute-defined-outside-init
    def clear(self):
        """Clear the Scraper to an initial state."""
        self.mimetype = None
        self.version = None
        self.streams = None
        self._well_formed = None
        self._check_wellformed = True
        self.info = {}

        if (mime := self._kwargs.get("mimetype", None)) not in [None, ""]:
            self._predefined_mimetype = mime.lower()
            self._kwargs["mimetype"] = mime.lower()
        else:
            self._predefined_mimetype = None

        if (version := self._kwargs.get("version", None)) not in [None, ""]:
            self._predefined_version = version
        else:
            self._predefined_version = None

        self._results = [
            [
                UserDefinedMeta(
                    Mimetype(
                        mimetype=self._predefined_mimetype,
                        version=self._predefined_version
                    )
                )
            ]
        ]
        # self._detected_mimetype and self._detected_version exist so
        # the predefined values above wouldn't get changed during the running
        # of the scraper.
        self._detected_mimetype = None
        self._detected_version = None
        # REFACTOR: The results get gathered back to the _kwargs
        self._kwargs["detected_mimetype"] = UNAV
        self._kwargs["detected_version"] = UNAV

    def _parameter_validation(self):
        """
        Validate parameters given to the scraper and
        raise proper error messages if wrong parameters
        """
        if not self._predefined_mimetype and self._predefined_version:
            raise InvalidMimetype(
                "Missing a mimetype parameter for the provided version "
                + self._predefined_version
            )

        # Validate that the mimetype and version combination is allowed

        if self._predefined_mimetype is None:
            return  # Both checks require _predefined_mimetype to exist

        formats = file_formats(True, True)

        allowed_mimetypes = (f["mimetype"].lower() for f in formats)
        if self._predefined_mimetype not in allowed_mimetypes:
            raise InvalidMimetype(
                f"Given mimetype {self._predefined_mimetype} is not supported"
            )

        found_mimetype_version_combinations = list(filter(
            lambda f:
            f["mimetype"].lower() == self._predefined_mimetype.lower() and
            f["version"] == self._predefined_version,
            formats
        ))
        if (
            len(found_mimetype_version_combinations) == 0
            and self._predefined_version is not None
        ):
            raise InvalidVersionForMimetype(
                f"Given version {self._predefined_version} for the mimetype "
                f"{self._predefined_mimetype} is not supported"
            )

    def _identify(self) -> None:
        """Identify file format and version."""
        for detector_class in iter_detectors():
            LOGGER.info(
                "Detecting file type using %s", detector_class.__name__
            )
            detector = detector_class(self.path)
            self._use_detector(detector)
            self._update_filetype(detector)

        # PDF files should always be scrutinized further to determine if
        # they are PDF/A
        # Files predefined as tiff will be scrutinized further to check if they
        # are dng files in order to return the correct mimetype and version
        if self._detected_mimetype in {"image/tiff", "application/pdf"}:
            exiftool_detector = ExifToolDetector(self.path)
            self._use_detector(exiftool_detector)
            self._update_filetype(exiftool_detector)

        detector_result_mimetype = self._detected_mimetype
        # Changing to predefined values when ever possible
        self._update_attributes(
            "_detected_mimetype",
            self._predefined_mimetype,
            to_empty=None,
            prevent_update_to_values=LOSE
        )
        self._update_attributes(
            "_detected_version",
            self._predefined_version,
            to_empty=None,
            prevent_update_to_values=LOSE
        )

        if (
            MagicCharset.is_supported(self._detected_mimetype)
            and self._kwargs.get("charset", None) is None
        ):
            charset_detector = MagicCharset(self.path)
            charset_detector.detect()
            self._kwargs["charset"] = charset_detector.charset

        if detector_result_mimetype == "application/octet-stream":
            LOGGER.info(
                "Detectors didn't find a mimetype. Trust to the user input")
            return

        # If detector disagrees with the user evaluate the mimetypes to
        # disallow nonsense user input and guide user to more accurate
        # decisions
        if (
            detector_result_mimetype != self._predefined_mimetype
            and self._predefined_mimetype not in LOSE
        ):
            mismatch = (
                "User defined mimetype: '%s' not detected by detectors. "
                "Detectors detected a different mimetype: '%s'" %
                (self._predefined_mimetype, detector_result_mimetype)
            )
            LOGGER.info(mismatch)
            self.info[len(self.info)] = {
                "class": "Scraper _identify",
                "messages": [mismatch],
                "errors": []
            }

    def _use_detector(self, detector: BaseDetector) -> None:
        detector.detect()
        LOGGER.debug(
            "%s detected MIME type: %s, version: %s, important: %s, "
            "well-formed: %s",
            detector.__class__.__name__, detector.mimetype, detector.version,
            detector.determine_important(), detector.well_formed
        )

        if detector.well_formed is False:
            self.well_formed = False
        self.info[len(self.info)] = detector.info()

    def _update_attributes(
        self,
        attribute_name: str,
        new_value: Any,
        to_empty: bool | None = True,
        prevent_update_to_values: list | tuple | None = None,
    ) -> None:
        """
        Updates an attribute and the kwarg argument associated with the
        attribute.

        :param attribute_name: The name of the updated attribute.
        :param new_value: The value the attribute will be update as.
        :param to_empty: Update only if the current value is considered empty,
            defaults to True. If None, always update regardless of the current
            value.
        :param prevent_update_to_values: A list or tuple of values which cannot
            be updated to for the attribute, defaults to None.
        """
        if prevent_update_to_values is None:
            prevent_update_to_values = [None]

        if new_value in prevent_update_to_values:
            return

        if to_empty and getattr(self, attribute_name) in LOSE:
            LOGGER.info(
                "Detected %s change: %s -> %s",
                attribute_name,
                getattr(self, attribute_name),
                new_value,
            )
            setattr(self, attribute_name, new_value)
            self._kwargs[attribute_name[1:]] = new_value
        elif not to_empty and getattr(self, attribute_name) not in LOSE:
            LOGGER.info(
                "Detected %s overwrite: %s -> %s",
                attribute_name,
                getattr(self, attribute_name),
                new_value,
            )
            setattr(self, attribute_name, new_value)
            self._kwargs[attribute_name[1:]] = new_value
        elif to_empty is None:
            LOGGER.info(
                "Detected %s overwrite/change: %s -> %s",
                attribute_name,
                getattr(self, attribute_name),
                new_value,
            )
            setattr(self, attribute_name, new_value)
            self._kwargs[attribute_name[1:]] = new_value

    def _update_filetype(self, detector: BaseDetector) -> None:
        """Run the detector and updates the file type based on its results.

        The MIME type or version is only changed if the old one is either
        present in the LOSE list or the new one is marked important by the
        detector.

        :param detector: Detector tool which updates
        """
        # Update mimetype
        self._update_attributes(
            "_detected_mimetype",
            detector.mimetype,
        )
        important = detector.determine_important()
        if important:
            self._update_attributes(
                "_detected_mimetype",
                important.mimetype,
                to_empty=False,
            )
        # If mimetype matches the detected one, update the version.
        if self._detected_mimetype == detector.mimetype:
            self._update_attributes(
                "_detected_version",
                detector.version,
            )
            if important:
                self._update_attributes(
                    "_detected_version",
                    important.version,
                    to_empty=False,
                )

    def _use_extractor(self, extractor: BaseExtractor) -> None:
        """
        Use the given extractor, collect metadata and update well-formadness.

        :param extractor: Extractor instance
        """
        extractor.extract()
        if extractor.streams:
            self._results.append(extractor.streams)
        self.info[len(self.info)] = extractor.info()
        if (
                (self.well_formed is None and self._check_wellformed)
                or extractor.well_formed is False
        ):
            self.well_formed = extractor.well_formed

    def _check_utf8(self) -> None:
        """
        UTF-8 check only for UTF-8.
        We know the charset after actual scraping.
        """
        if (
            "charset" in self.streams[0]
            and self.streams[0]["charset"] == "UTF-8"
        ):
            scraper = JHoveUtf8Extractor(filename=self.path, mimetype=UNAV)
            self._use_extractor(scraper)

    def _merge_results(self) -> None:
        """
        Merge scraper results into streams and handle possible
        conflicts.
        """
        if len(self._results) > 1:
            streams, errors = generate_metadata_dict(
                self._results[1:],
                LOSE
            )
            if streams[0]["mimetype"] == UNAV:
                errors.append("File format is not supported.")
            if (
                self._predefined_version not in LOSE
                and streams[0]["version"]
                and streams[0]["version"] != self._predefined_version
            ):
                errors.append(
                    f"The Extractors produced a different version: "
                    f"{streams[0]['version']} compared to the version given "
                    f"by the user: {self._predefined_version}"
                )
        else:
            errors = []

        streams, more_errors = generate_metadata_dict(
            self._results,
            LOSE
        )
        errors.extend(more_errors)

        merge_well_formed = None
        if len(errors) > 0:
            merge_well_formed = False

        if (
            (self.well_formed is None and self._check_wellformed)
            or merge_well_formed is False
        ):
            self.well_formed = merge_well_formed
        self.streams = streams

        self.info[len(self.info)] = {
            "class": "Scraper (_merge_results)",
            "messages": ["Extractor results merged into streams"],
            "errors": errors,
            "tools": {},
        }

    def scrape(self, check_wellformed: bool = True) -> None:
        """Scrape file and collect metadata.

        :param check_wellformed: True, full scraping; False, skip well-formed
            check.
        """
        LOGGER.info("Scraping %s", self.path)
        self._check_wellformed = check_wellformed
        self._identify()
        LOGGER.debug(
            "Mimetype after detectors: %s and version: %s",
            self._detected_mimetype,
            self._detected_version,
        )
        for extractor_class in iter_extractors(
            mimetype=self._detected_mimetype,
            version=self._detected_version,
            check_wellformed=self._check_wellformed,
            params=self._kwargs,
        ):
            LOGGER.info("Scraping with %s", extractor_class.__name__)

            extractor = extractor_class(
                filename=self.path,
                mimetype=self._detected_mimetype,
                version=self._detected_version,
                params=self._kwargs,
            )
            self._use_extractor(extractor)
            if extractor.streams:
                LOGGER.debug(
                    "Extractor %s produced a stream with mimetype: %s and "
                    "version: %s",
                    extractor.__class__.__name__,
                    extractor.streams[0].mimetype(),
                    extractor.streams[0].version(),
                )
            else:
                LOGGER.debug(
                    "Extractor %s didn't produce a stream",
                    extractor.__class__.__name__,
                )
        self._merge_results()
        # If no streams exist the mimetype and version are unavailable
        if not self.streams:
            LOGGER.error("No streams found by the extractors!")
            return

        self._check_utf8()
        self.mimetype = self._predefined_mimetype
        self.version = self._predefined_version
        if self._predefined_mimetype is None:
            self.mimetype = self.streams[0]["mimetype"]
        if self._predefined_version is None:
            self.version = self.streams[0]["version"]

    def detect_filetype(self) -> tuple[str | None, str | None]:
        """
        Find out the MIME type and version of the file without metadata
        extracting.

        All stream and file type information gathered during possible previous
        scraping or filetype detection calls is erased when this function is
        called.

        Please note that using only detectors can result in a file type result
        that differs from the one obtained by the full extractor due to full
        extractor using a more comprehensive set of tools.

        :returns: Detected mimetype and version
        """
        self.clear()
        self._identify()
        return (self._detected_mimetype, self._detected_version)

    def is_textfile(self) -> bool:
        """
        Find out if file is a text file.

        :returns: True, if file is a text file, false otherwise
        """
        scraper = TextfileExtractor(self.path, "text/plain")
        scraper.extract()
        return scraper.well_formed is not False

    def checksum(self, algorithm: str = "MD5") -> str:
        """
        Return the checksum of the file with given algorithm.

        :param algorithm: MD5 or SHA variant
        :returns: Calculated checksum
        """
        return hexdigest(self.path, algorithm)

    def grade(self) -> str:
        """Return digital preservation grade."""
        return file_formats_grade(self.mimetype, self.version, self.streams)


def _validate_path(supposed_filepath: str | bytes | os.PathLike) -> Path:
    """
    Checks if the supposed filepath is actually a valid file to scrape.

    :param supposed_filepath: PathLike object.
    :raises FileIsNotScrapable: The file given cannot be scraped.
    :raises FileNotFoundError: The file cannot be found from the path.
    :raises TypeError: The given file arguments are invalid.
    :raises IsADirectoryError: The file is a directory.
    """
    path = Path(os.fsdecode(supposed_filepath))
    if not path.exists():
        raise FileNotFoundIsNotScrapable(
            "A file couldn't be found from the path: " + str(path)
        )
    if path.is_dir():
        raise DirectoryIsNotScrapable(
            "Instead of a file, a directory was found from the path: "
            + str(path)
        )
    if not path.is_file():
        raise FileIsNotScrapable(
            "The file is not a regular file and can't be scraped from"
            " the path: " + str(path)
        )

    return path.resolve()
