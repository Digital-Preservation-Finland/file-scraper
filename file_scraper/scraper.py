"""File metadata scraper."""
import os
from pathlib import Path
from typing import Union

from dpres_file_formats import graders

from file_scraper.defaults import UNAV
from file_scraper.detectors import (MagicCharset, ExifToolDetector)
from file_scraper.dummy.dummy_scraper import (FileExists, MimeMatchScraper,
                                              ResultsMergeScraper)
from file_scraper.iterator import iter_detectors, iter_scrapers
from file_scraper.jhove.jhove_scraper import JHoveUtf8Scraper
from file_scraper.textfile.textfile_scraper import TextfileScraper
from file_scraper.utils import hexdigest

LOSE = (None, UNAV, "")


class Scraper:
    """File indentifier and scraper."""

    # pylint: disable=no-member, too-many-instance-attributes

    def __init__(self,
                 filename: Union[
                     str,
                     bytes,
                     os.PathLike[str],
                     os.PathLike[bytes]
                 ],
                 **kwargs):
        """Initialize scraper.
        :filename: File path
        :kwargs: Extra arguments for certain scrapers.
        """
        try:
            self.path = Path(os.fsdecode(filename))
        except TypeError as exc:
            raise TypeError("Expected a PathLike type as filename.") from exc

        self.mimetype = None
        self.version = None
        self.streams = None
        self.well_formed = None
        self.info = None
        self._params = kwargs
        self._scraper_results = []
        self._predefined_mimetype = None
        self._predefined_version = None
        self._file_exists = None
        if self._params.get("mimetype", None) not in LOSE:
            self._predefined_mimetype = self._params.get("mimetype").lower()
            self._params["mimetype"] = self._params.get("mimetype").lower()
        if self._params.get("version", None) not in LOSE:
            self._predefined_version = self._params.get("version", None)

    @property
    def filename(self) -> bytes:
        """Return file path as byte string.

        This maintains backwards compatibility for tools expecting file path
        as string. `path` should be preferred instead for newer code.
        """
        return os.fsencode(self.path)

    def _identify(self):
        """Identify file format and version.
        """
        self.info = {}
        _mime = self._predefined_mimetype
        _version = self._predefined_version
        self._params["detected_mimetype"] = UNAV
        self._params["detected_version"] = UNAV

        for detector in iter_detectors():
            tool = detector(self.path, _mime, _version)
            self._update_filetype(tool)

        if MagicCharset.is_supported(self._predefined_mimetype) and \
                self._params.get("charset", None) is None:
            charset_detector = MagicCharset(self.path)
            charset_detector.detect()
            self._params["charset"] = charset_detector.charset

        # PDF files should always be scrutinized further to determine if
        # they are PDF/A
        # Files predefined as tiff will be scrutinized further to check if they
        # are dng files in order to return the correct mimetype and version
        if self._predefined_mimetype in ("image/tiff", "application/pdf"):
            exiftool_detector = ExifToolDetector(self.path)
            self._update_filetype(exiftool_detector)

    def _update_filetype(self, tool):
        """
        Run the detector and updates the file type based on its results.

        The MIME type or version is only changed if the old one is either
        present in the LOSE list or the new one is marked important by the
        detector.

        :tool: Detector tool
        """
        tool.detect()
        if tool.well_formed is False:
            self.well_formed = False
        self.info[len(self.info)] = tool.info()
        important = tool.get_important()
        if self._predefined_mimetype in LOSE:
            self._predefined_mimetype = tool.mimetype
        if self._predefined_mimetype == tool.mimetype and \
                self._predefined_version in LOSE:
            self._predefined_version = tool.version
        if "mimetype" in important and \
                important["mimetype"] not in LOSE:
            self._predefined_mimetype = important["mimetype"]
        if "version" in important and \
                important["version"] not in LOSE:
            self._predefined_version = important["version"]
        if tool.info()["class"] != "PredefinedDetector" and \
                self._predefined_mimetype == tool.mimetype and \
                ("version" in important or
                 self._params["detected_version"] in LOSE):
            self._params["detected_mimetype"] = tool.mimetype
            self._params["detected_version"] = tool.version

    def _scrape_file(self, scraper, check_wellformed):
        """
        Scrape with the given scraper.

        :scraper: Scraper instance
        :check_wellformed: True for well-formed checking, False otherwise
        """
        scraper.scrape_file()
        if scraper.streams:
            self._scraper_results.append(scraper.streams)
        self.info[len(self.info)] = scraper.info()
        if (self.well_formed is None and check_wellformed) or \
                scraper.well_formed is False:
            self.well_formed = scraper.well_formed

    def _check_utf8(self, check_wellformed):
        """
        UTF-8 check only for UTF-8.
        We know the charset after actual scraping.

        :check_wellformed: Whether full scraping is used or not.
        """
        if not check_wellformed:
            return
        if "charset" in self.streams[0] and \
                self.streams[0]["charset"] == "UTF-8":
            scraper = JHoveUtf8Scraper(filename=self.path,
                                       mimetype=UNAV)
            self._scrape_file(scraper, True)

    def _check_mime(self, check_wellformed):
        """
        Check that predefined mimetype and resulted mimetype match.

        :check_wellformed: Whether full scraping is used or not.
        """
        version = None
        if self._params.get("version", None) not in LOSE:
            version = self._params.get("version", None)
        scraper = MimeMatchScraper(
            filename=self.path,
            mimetype=self._predefined_mimetype,
            version=version,
            params={"mimetype": self.mimetype,
                    "version": self.version,
                    "well_formed": self.well_formed})
        self._scrape_file(scraper, check_wellformed)

    def _merge_results(self, check_wellformed):
        """
        Merge scraper results into streams and handle possible
        conflicts.

        :check_wellformed: Whether full scraping is used or not.
        """
        scraper = ResultsMergeScraper(
            filename=self.path,
            mimetype=self._predefined_mimetype,
            version=self._predefined_version,
            params=self._params)
        self._scrape_file(scraper, check_wellformed)
        self.streams = scraper.streams

    def scrape(self, check_wellformed=True):
        """Scrape file and collect metadata.

        :check_wellformed: True, full scraping; False, skip well-formed check.
        """
        self.detect_filetype()

        # MIME type could not be determined or file was not found.
        if not self._predefined_mimetype or not self._file_exists:
            self.streams = {}
            self.mimetype = "(:unav)"
            self.version = "(:unav)"
            return

        for scraper_class in iter_scrapers(
                mimetype=self._predefined_mimetype,
                version=self._predefined_version,
                check_wellformed=check_wellformed, params=self._params):
            scraper = scraper_class(
                filename=self.path,
                mimetype=self._predefined_mimetype,
                version=self._predefined_version,
                params=self._params)
            self._scrape_file(scraper, check_wellformed)
        self._params["scraper_results"] = self._scraper_results

        self._merge_results(check_wellformed)
        self._check_utf8(check_wellformed)

        self.mimetype = self.streams[0]["mimetype"]
        self.version = self.streams[0]["version"]

        self._check_mime(check_wellformed)

    def detect_filetype(self):
        """
        Find out the MIME type and version of the file without metadata scrape.

        All stream and file type information gathered during possible previous
        scraping or filetype detection calls is erased when this function is
        called.

        Please note that using only detectors can result in a file type result
        that differs from the one obtained by the full scraper due to full
        scraping using a more comprehensive set of tools.

        :returns: Predefined mimetype and version
        """
        self.mimetype = None
        self.version = None
        self.streams = None
        self.info = {}
        self.well_formed = None
        self._predefined_mimetype = None
        self._predefined_version = None
        if self._params.get("mimetype", None) not in LOSE:
            self._predefined_mimetype = self._params.get("mimetype", None)
        if self._params.get("version", None) not in LOSE:
            self._predefined_version = self._params.get("version", None)

        file_exists = FileExists(self.path, None)
        self._scrape_file(file_exists, True)
        if file_exists.well_formed is False:
            self._file_exists = False
            return (None, None)

        self._file_exists = True
        self._identify()
        return (self._predefined_mimetype, self._predefined_version)

    def is_textfile(self):
        """
        Find out if file is a text file.

        :returns: True, if file is a text file, false otherwise
        """
        scraper = TextfileScraper(self.path, "text/plain")
        scraper.scrape_file()
        if scraper.well_formed is False:
            return False
        return True

    def checksum(self, algorithm="MD5"):
        """
        Return the checksum of the file with given algorithm.

        :algorithm: MD5 or SHA variant
        :returns: Calculated checksum
        """
        return hexdigest(self.path, algorithm)

    def grade(self):
        """Return digital preservation grade."""
        return graders.grade(self.mimetype,self.version,self.streams)
