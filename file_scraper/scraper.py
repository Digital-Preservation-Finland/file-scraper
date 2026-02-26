"""File metadata scraper."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, NamedTuple, TYPE_CHECKING

from dpres_file_formats.graders import file_formats
from dpres_file_formats.graders import grade as file_formats_grade

from file_scraper.metadata import generate_metadata_dict
from file_scraper.defaults import UNAV
from file_scraper.detectors import ExifToolDetector, MagicCharset
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

if TYPE_CHECKING:
    from file_scraper.base import BaseDetector, BaseExtractor


class ScraperResults(NamedTuple):
    path: str
    mimetype: str
    version: str
    well_formed: str
    streams: dict[int, Any]
    grade: str
    info: dict[str, Any]
    errors: list[str]


class Scraper:
    """File indentifier and scraper."""

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

        self.info = {}
        self._well_formed = None

        mimetype = kwargs.get("mimetype")
        if mimetype:
            # Normalize mimetype
            mimetype = mimetype.lower()

        version = kwargs.get("version")
        # TODO: SAPA is still using old siptools, although it
        # is deprecated. The old siptools is sometimes using empty
        # string as version, so it must be translated to None. Remove
        # this hack when old siptools is not used anymore.
        if version == "":
            version = None

        charset = kwargs.get("charset")
        if charset:
            # Normalize charset
            charset = charset.upper()

        # Initialize streams with user defined metadata
        self.streams: dict[int, dict] = {
            0: {
                "index": 0,
                "mimetype": mimetype,
                "version": version,
            }
        }
        if charset:
            self.streams[0]["charset"] = charset

        _validate_mimetype_and_version(self.mimetype, self.version)

    @property
    def mimetype(self) -> str | None:
        """Return mimetype of the file."""
        return self.streams[0]["mimetype"]

    @property
    def version(self) -> str | None:
        """Return format version of the file."""
        return self.streams[0]["version"]

    @property
    def _charset(self) -> str | None:
        """Return charset of the file."""
        return self.streams[0].get("charset")

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

    def detect_filetype(self) -> tuple[str | None, str | None]:
        """
        Find out the MIME type and version of the file without metadata
        extracting.

        Please note that using only detectors can result in a file type result
        that differs from the one obtained by the full extractor due to full
        extractor using a more comprehensive set of tools.

        :returns: Detected mimetype and version
        """
        if self.info:
            raise RuntimeError("File is already detected")
        detected_mimetype = None
        detected_version = None
        for detector in iter_detectors(path=self.path):
            LOGGER.info(
                "Detecting file type using %s", detector.__class__.__name__
            )
            detected_mimetype, detected_version = _update_filetype(
                detector,
                detected_mimetype,
                detected_version,
            )
            if detector.well_formed is False:
                self.well_formed = False
            self.info[len(self.info)] = detector.info()

        # PDF files should always be scrutinized further to determine if
        # they are PDF/A
        # Files predefined as tiff will be scrutinized further to check if they
        # are dng files in order to return the correct mimetype and version
        if detected_mimetype in {
                "image/tiff",
                "application/pdf",
                "image/jpeg"
        }:
            # TODO: Duplicate code could be avoided if detectors would
            # be more consistent: TPASPKT-1578
            exiftool_detector = ExifToolDetector(self.path)
            detected_mimetype, detected_version = _update_filetype(
                exiftool_detector,
                detected_mimetype,
                detected_version,
            )
            if detector.well_formed is False:
                self.well_formed = False
            self.info[len(self.info)] = detector.info()

        # If detector disagrees with the user evaluate the mimetypes to
        # disallow nonsense user input and guide user to more accurate
        # decisions
        if self.mimetype is not None \
                and detected_mimetype != self.mimetype:
            mismatch = (
                "User defined mimetype: '%s' not detected by detectors. "
                "Detectors detected a different mimetype: '%s'" %
                (self.mimetype, detected_mimetype)
            )
            LOGGER.info(mismatch)
            self.info[len(self.info)] = {
                "class": "Scraper _identify",
                "messages": [mismatch],
                "errors": [],
                "tools": {},
            }
        else:
            self.streams[0]["mimetype"] = detected_mimetype

        # Detected version is used only if detected mimetype does not
        # conflict with predefined mimetype, and version is not
        # predefined
        if self.mimetype == detected_mimetype:
            if self.version is None:
                self.streams[0]["version"] = detected_version
            elif detected_version != self.version:
                mismatch = (
                    f"User defined version: '{self.version}' not detected by "
                    "detectors. Detectors detected a different mimetype: "
                    f"'{detected_version}'"
                )
                LOGGER.info(mismatch)

        # Detect charset if it was not defined by user
        if (
            MagicCharset.is_supported(self.mimetype)
            and self._charset is None
        ):
            charset_detector = MagicCharset(self.path)
            charset_detector.detect()
            self.streams[0]["charset"] = charset_detector.charset

        # Mimetype and version are returned, because they are used by
        # detect-file command
        return (self.mimetype, self.version)

    def _use_extractor(self, extractor: BaseExtractor) -> None:
        """
        Use the given extractor, collect metadata and update well-formedness.

        :param extractor: Extractor instance
        """
        extractor.extract()
        self.info[len(self.info)] = extractor.info()
        if self.well_formed is None \
                or extractor.well_formed is False:
            self.well_formed = extractor.well_formed

        if extractor.streams:
            LOGGER.debug(
                "Extractor %s produced a stream with mimetype: %s and "
                "version: %s",
                extractor.__class__.__name__,
                extractor.streams[0].mimetype(),
                extractor.streams[0].version(),
                # TODO: Could we log all metadata of all streams here?
                # See TPASPKT-1570.
            )
        else:
            LOGGER.debug(
                "Extractor %s didn't produce a stream",
                extractor.__class__.__name__,
            )

        # Merge streams to previous streams
        conflicts = generate_metadata_dict(
            streams=self.streams,
            new_streams=extractor.streams
        )
        if conflicts:
            self.info[len(self.info)] = {
                "class": self.__class__.__name__,
                "errors": conflicts,
            }
            self.well_formed = False

    def _check_utf8(self) -> None:
        """UTF-8 check only for UTF-8.

        We know the charset after actual scraping.
        """
        if self._charset == "UTF-8":
            scraper = JHoveUtf8Extractor(filename=self.path, mimetype=UNAV)
            self._use_extractor(scraper)

    def scrape(self, check_wellformed: bool = True) -> ScraperResults:
        """Scrape file and collect metadata.

        :param check_wellformed: True, full scraping; False, skip well-formed
            check.
        :returns:
            A NamedTuple which contains the following members
            - path::string the input path given to the Scraper
            - mimetype::string the detected or inputted MIME type for scraper
            - version::string the MIME type version
            - streams::dict the collected streams. Inside the list the
              streams are stored with numbers starting from the number 0.
            - well_formed::boolean the well-formedness will always be included
              regardless of the check_wellformed parameter. The file just can't
              be well-formed if the check_wellformed parameter has been set to
              False.
            - grade::string produces the grade for file-scraper
            - info::dict the collected information about each used tool,
              the tools are stored with numbers starting from the number 0.
              Each tool info contains at least the class, messages, errors and
              tools
            - errors::list collects errors from extractors to a list.
        """
        LOGGER.info("Scraping %s", self.path)

        if not self.info:
            # File detection has not been done yet
            self.detect_filetype()

        LOGGER.debug(
            "Mimetype after detectors: %s and version: %s",
            self.mimetype,
            self.version,
        )
        for extractor in iter_extractors(
            path=self.path,
            mimetype=self.mimetype,
            version=self.version,
            charset=self._charset,
            check_wellformed=check_wellformed,
            params=self._kwargs,
        ):
            LOGGER.info("Scraping with %s", extractor.__class__.__name__)
            self._use_extractor(extractor)

        # TODO: UTF-8 extractor should not be used if
        # check_wellformed=False. See PAS-1.
        self._check_utf8()

        # Add error if detected format is not supported
        # TODO: Error should be added also when file is supported
        # according to DPS specification, but it is not yet supported by
        # file-scraper. See TPASPKT-1677.
        try:
            _validate_mimetype_and_version(self.mimetype, self.version)
        except ValueError as exception:
            self.info[len(self.info)] = {
                "class": "Scraper",
                "messages": [],
                "errors": [str(exception)],
                "tools": {},
            }
            self.well_formed = False

        # If validators were not used, well-formedness can not be True
        if not check_wellformed and self.well_formed:
            self.well_formed = None

        # Return scraper results:
        errors = []
        for item in self.info.values():
            for error in item["errors"]:
                errors.append(item["class"] + " :: " + error)
        return ScraperResults(
            path=str(self.input_path),
            mimetype=self.mimetype,
            version=self.version,
            well_formed=self.well_formed,
            streams=self.streams,
            grade=self.grade(),
            info=self.info,
            errors=errors
        )

    def is_textfile(self) -> bool:
        """
        Find out if file is a text file.

        :returns: True, if file is a text file, false otherwise
        """
        extractor = TextfileExtractor(
            filename=self.path,
            mimetype="text/plain",
            charset=None,
        )
        extractor.extract()
        return extractor.well_formed is not False

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


def _validate_mimetype_and_version(mimetype, version):
    """Validate mimetype and version.

    Check that mimetype + version combination is supported by DPS
    specification. Raises Exception if it is not.
    """
    if not mimetype and version:
        raise InvalidMimetype(
            "Missing a mimetype parameter for the provided version " + version
        )

    # Validate that the mimetype and version combination is allowed

    if mimetype is None:
        return  # Both checks require mimetype to be defined

    formats = file_formats(True, True)

    allowed_mimetypes = (f["mimetype"].lower() for f in formats)
    if mimetype not in allowed_mimetypes:
        raise InvalidMimetype(f"Given mimetype {mimetype} is not supported")

    found_mimetype_version_combinations = list(filter(
        lambda f:
        f["mimetype"].lower() == mimetype.lower() and
        f["version"] == version,
        formats
    ))
    if (
        len(found_mimetype_version_combinations) == 0
        and version is not None
    ):
        raise InvalidVersionForMimetype(
            f"Given version {version} for the mimetype "
            f"{mimetype} is not supported"
        )


def _update_filetype(
    detector: BaseDetector,
    mimetype,
    version,
) -> tuple[str, str]:
    """Run the detector check if previous filetype should be overridden.

    The MIME type or version is only changed if the new one is marked
    important by the detector. Returns updated mimetype and version.

    :param detector: Detector tool
    :param mimetype: The mimetype from previous detector(s)
    :param version: The version from previous detector(s)
    """
    detector.detect()
    LOGGER.debug(
        "%s detected MIME type: %s, version: %s, important: %s, "
        "well-formed: %s",
        detector.__class__.__name__, detector.mimetype, detector.version,
        detector.determine_important(), detector.well_formed
    )

    # Update mimetype
    if mimetype is None:
        # No previous value
        mimetype = detector.mimetype
    # TODO: rewrite determine_important to simplify this statement
    elif mimetype != detector.mimetype \
            and detector.mimetype is not None \
            and detector.mimetype == detector.determine_important().mimetype:
        LOGGER.debug(
            "Mimetype %s from %s is important, overriding previous value",
            detector.mimetype, detector.__class__.__name__
        )
        mimetype = detector.mimetype
    elif mimetype != detector.mimetype:
        LOGGER.debug(
            "Mimetype %s from %s is not important, ignoring",
            detector.mimetype, detector.__class__.__name__
        )

    # If mimetype matches the detected one, update the version.
    if mimetype == detector.mimetype:
        if version is None:
            # No previous value
            version = detector.version
        elif detector.version is None:
            # No need to update
            pass
        elif version != detector.version \
                and detector.version \
                == detector.determine_important().version:
            LOGGER.debug(
                "Version %s from %s is important, overriding previous"
                " value",
                detector.version, detector.__class__.__name__
            )
            version = detector.version
        elif version != detector.version:
            LOGGER.debug(
                "Version %s from %s is not important, ignoring",
                detector.version, detector.__class__.__name__
            )

    return mimetype, version
