"""File metadata scraper."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dpres_file_formats import graders

from file_scraper.base import BaseDetector, BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.detectors import ExifToolDetector, MagicCharset
from file_scraper.dummy.dummy_extractor import MimeMatchExtractor
from file_scraper.exceptions import FileIsNotScrapable
from file_scraper.iterator import iter_detectors, iter_extractors
from file_scraper.jhove.jhove_extractor import JHoveUtf8Extractor
from file_scraper.logger import LOGGER
from file_scraper.textfile.textfile_extractor import TextfileExtractor
from file_scraper.utils import generate_metadata_dict, hexdigest

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

    @property
    def filename(self) -> bytes:
        """Return file path as byte string.

        This maintains backwards compatibility for tools expecting file path
        as string. `path` should be preferred instead for newer code.
        """
        return os.fsencode(self.path)

    # TODO move initialization to init if detect_filetype no longer needs to
    # reset the scraper class.
    # pylint: disable=attribute-defined-outside-init
    def clear(self):
        """Clear the Scraper to an initial state."""
        self.mimetype = None
        self.version = None
        self.streams = None
        self.well_formed = None
        self.info = {}
        self._extractor_results = []

        if (mime := self._kwargs.get("mimetype", None)) not in LOSE:
            self._predefined_mimetype = mime.lower()
            self._kwargs["mimetype"] = mime.lower()
        else:
            self._predefined_mimetype = None

        if (version := self._kwargs.get("version", None)) not in LOSE:
            self._predefined_version = version
        else:
            self._predefined_version = None
        # self._detected_mimetype and self._detected_version exist so
        # the predefined values above wouldn't get changed during the running
        # of the scraper.
        self._detected_mimetype = None
        self._detected_version = None
        # REFACTOR: The results get gathered back to the _kwargs
        self._kwargs["detected_mimetype"] = UNAV
        self._kwargs["detected_version"] = UNAV

    def _identify(self):
        """Identify file format and version."""
        for detector_class in iter_detectors():
            LOGGER.info(
                "Detecting file type using %s", detector_class.__name__)
            detector = detector_class(
                self.path,
                self._predefined_mimetype,
                self._predefined_version
                )
            self._update_filetype(detector)

        if (
            MagicCharset.is_supported(self._detected_mimetype)
            and self._kwargs.get("charset", None) is None
        ):
            charset_detector = MagicCharset(self.path)
            charset_detector.detect()
            self._kwargs["charset"] = charset_detector.charset

        # PDF files should always be scrutinized further to determine if
        # they are PDF/A
        # Files predefined as tiff will be scrutinized further to check if they
        # are dng files in order to return the correct mimetype and version
        if self._detected_mimetype in {"image/tiff", "application/pdf"}:
            exiftool_detector = ExifToolDetector(self.path)
            self._update_filetype(exiftool_detector)

    def _update_filetype(self, detector: BaseDetector) -> None:
        """Run the detector and updates the file type based on its results.

        The MIME type or version is only changed if the old one is either
        present in the LOSE list or the new one is marked important by the
        detector.

        :param detector: Detector tool which updates
        """
        detector.detect()
        LOGGER.debug(
            "%s detected MIME type: %s, version: %s, important: %s, "
            "well-formed: %s",
            detector.__class__.__name__, detector.mimetype, detector.version,
            detector.get_important(), detector.well_formed
        )

        if detector.well_formed is False:
            self.well_formed = False
        self.info[len(self.info)] = detector.info()
        important = detector.get_important()

        if self._detected_mimetype in LOSE:
            self._detected_mimetype = detector.mimetype
        if self._detected_mimetype == detector.mimetype and \
                self._detected_version in LOSE:
            self._detected_version = detector.version
        if "mimetype" in important and \
                important["mimetype"] not in LOSE:
            LOGGER.info(
                "Tool provided important value '%s' for MIME type, "
                "setting pre-defined MIME type",
                important["mimetype"]
            )
            self._detected_mimetype = important["mimetype"]
        if "version" in important and \
                important["version"] not in LOSE:
            LOGGER.info(
                "Tool provided important value '%s' for file format version, "
                "setting pre-defined version",
                important["version"]
            )
            self._detected_version = important["version"]
        if detector.info()["class"] == "PredefinedDetector":
            LOGGER.debug(
                "detector used was PredefinedDetector so no changes to"
                "the detected_mimetype or detected_version should occur")
            return
        if self._detected_mimetype != detector.mimetype:
            LOGGER.debug(
                "%s can't apply the MIME type found: %s on top of "
                "another MIME type %s",
                detector.__class__.__name__,
                detector.mimetype,
                self._detected_mimetype)
            return
        # If predefined mimetype is not None it means the user wants choose the
        # mimetype which needs to be respected and the detected mimetype
        # can't overrule the user.
        if self._predefined_mimetype is not None and \
                self._predefined_mimetype != self._detected_mimetype:
            return

        if ("version" in important or
           self._kwargs["detected_version"] in LOSE):
            LOGGER.info(
                "Detected MIME type and version changed. "
                "MIME type: %s -> %s, version: %s -> %s",
                self._kwargs["detected_mimetype"],
                detector.mimetype,
                self._kwargs["detected_version"],
                detector.version
            )

            self._kwargs["detected_mimetype"] = detector.mimetype
            self._kwargs["detected_version"] = detector.version

    def _use_extractor(
        self, extractor: BaseExtractor, check_wellformed: bool
    ) -> None:
        """
        Use the given extractor, collect metadata and update well-formadness.

        :param extractor: Extractor instance
        :param check_wellformed: True for well-formed checking, False otherwise
        """
        extractor.extract()
        if extractor.streams:
            self._extractor_results.append(extractor.streams)
        self.info[len(self.info)] = extractor.info()
        if (
            self.well_formed is None and check_wellformed
        ) or extractor.well_formed is False:
            self.well_formed = extractor.well_formed

    def _check_utf8(self, check_wellformed: bool) -> None:
        """
        UTF-8 check only for UTF-8.
        We know the charset after actual scraping.

        :param check_wellformed: Whether full scraping is used or not.
        """
        if not check_wellformed:
            return
        if "charset" in self.streams[0] and \
                self.streams[0]["charset"] == "UTF-8":
            scraper = JHoveUtf8Extractor(filename=self.path,
                                         mimetype=UNAV)
            self._use_extractor(scraper, True)

    def _check_mime(self, check_wellformed: bool) -> None:
        """
        Check that predefined mimetype and resulted mimetype match.

        :param check_wellformed: Whether full scraping is used or not.
        """
        version = None
        if (ver := self._kwargs.get("version")) not in LOSE:
            version = ver
        scraper = MimeMatchExtractor(
            filename=self.path,
            mimetype=self._detected_mimetype,
            version=version,
            params={"mimetype": self.mimetype,
                    "version": self.version,
                    "well_formed": self.well_formed})
        self._use_extractor(scraper, check_wellformed)

    def _merge_results(self, check_wellformed: bool) -> None:
        """
        Merge scraper results into streams and handle possible
        conflicts.

        :param check_wellformed: Whether full scraping is used or not.
        """
        extractor_results = self._kwargs.get("extractor_results", [])
        errors = []
        messages = []

        streams, conflicts = generate_metadata_dict(extractor_results, LOSE)
        errors += conflicts
        messages.append("Extractor results merged into streams")

        info = {
            "class": "Scraper (_merge_results)",
            "messages": messages,
            "errors": errors,
            "tools": {},
        }

        if len(messages) > 0 and len(errors) == 0:
            merge_well_formed = None
        else:
            merge_well_formed = False

        if streams:
            self._extractor_results.append(streams)
        self.info[len(self.info)] = info
        if (
            self.well_formed is None and check_wellformed
        ) or merge_well_formed is False:
            self.well_formed = merge_well_formed
        self.streams = streams

    def scrape(self, check_wellformed: bool = True) -> None:
        """Scrape file and collect metadata.

        :param check_wellformed: True, full scraping; False, skip well-formed
            check.
        """
        LOGGER.info("Scraping %s", self.path)

        self._identify()

        for extractor_class in iter_extractors(
                mimetype=self._detected_mimetype,
                version=self._detected_version,
                check_wellformed=check_wellformed, params=self._kwargs):
            LOGGER.info("Scraping with %s", extractor_class.__name__)

            extractor = extractor_class(
                filename=self.path,
                mimetype=self._detected_mimetype,
                version=self._detected_version,
                params=self._kwargs)
            self._use_extractor(extractor, check_wellformed)

        self._kwargs["extractor_results"] = self._extractor_results
        self._merge_results(check_wellformed)
        # If no streams exist the mimetype and version are unavailable
        if not self.streams:
            self.mimetype = UNAV
            self.version = UNAV
            return

        self._check_utf8(check_wellformed)
        self.mimetype = self.streams[0]["mimetype"]
        self.version = self.streams[0]["version"]

        self._check_mime(check_wellformed)

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

        :returns: Predefined mimetype and version
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
        return graders.grade(self.mimetype, self.version, self.streams)


def _validate_path(
    supposed_filepath: str | bytes | os.PathLike[str] | os.PathLike[bytes]
) -> Path:
    """
    Checks if the supposed filepath is actually a valid file to scrape

    :param supposed_filepath: any str, byte or Pathlike string or bytes
    :raises FileIsNotScrapable: The file given cannot be scraped for
        reason or another.
    :raises FileNotFoundError: The file cannot be found from the path
        given.
    :raises TypeError: The file argument given was invalid.
    :raises IsADirectoryError: The file given was a directory.
    """
    path = Path(os.fsdecode(supposed_filepath))
    if not path.exists():
        raise FileNotFoundError(
            "A file couldn't be found from the path: " + str(path))
    if path.is_dir():
        raise IsADirectoryError(
            "Instead of a file, a directory was found from the path: " +
            str(path)
        )
    if not path.is_file():
        raise FileIsNotScrapable(
            "The file is not a regular file and can't be scrapable from"
            " the path: " + str(path)
        )

    return path.resolve()
