"""File metadata scraper."""
from __future__ import unicode_literals

from file_scraper.detectors import VerapdfDetector, MagicCharset
from file_scraper.dummy.dummy_scraper import FileExists, MimeScraper
from file_scraper.iterator import iter_detectors, iter_scrapers
from file_scraper.jhove.jhove_scraper import JHoveUtf8Scraper
from file_scraper.textfile.textfile_scraper import TextfileScraper
from file_scraper.utils import encode_path, generate_metadata_dict, hexdigest

LOSE = (None, "(:unav)", "")


class Scraper(object):
    """File indentifier and scraper."""

    # pylint: disable=no-member, too-many-instance-attributes

    def __init__(self, filename, **kwargs):
        """Initialize scraper.
        :filename: File path
        :kwargs: Extra arguments for certain scrapers
        """
        if filename is not None:
            filename = encode_path(filename)
        self.filename = filename
        self.mimetype = None
        self.version = None
        self.streams = None
        self.well_formed = None
        self.info = None
        self._params = kwargs
        self._scraper_results = []
        self._predefined_mimetype = self._params.get("mimetype", None)
        self._predefined_version = self._params.get("version", None)

    def _identify(self):
        """Identify file format and version."""
        self.info = {}
        _mime = self._predefined_mimetype
        _version = self._predefined_version
        for detector in iter_detectors():
            tool = detector(self.filename, _mime, _version)
            self._update_filetype(tool)

        # Unless version is given by the user, PDF files should be scrutinized
        # further to determine if they are PDF/A
        if (self._predefined_mimetype == "application/pdf" and
                not (self._predefined_version)):
            vera_detector = VerapdfDetector(self.filename)
            self._update_filetype(vera_detector)

        if MagicCharset.is_supported(self.mimetype) and \
                self._params.get("charset", None) is None:
            charset_detector = MagicCharset(self.filename)
            charset_detector.detect()
            self._params["charset"] = charset_detector.charset

    def _update_filetype(self, tool):
        """
        Run the detector and updates the file type based on its results.

        The MIME type or version is only changed if the old one is either
        present in the LOSE list or the new one is marked important by the
        detector.
        """
        tool.detect()
        self.info[len(self.info)] = tool.info
        important = tool.get_important()
        if self._predefined_mimetype in LOSE:
            self._predefined_mimetype = tool.mimetype
        if self._predefined_mimetype == tool.mimetype and \
                self._predefined_version in LOSE:
            self._predefined_version = tool.version
        if "mimetype" in important and \
                important["mimetype"] is not None:
            self._predefined_mimetype = important["mimetype"]
        if "version" in important and \
                important["version"] is not None:
            self._predefined_version = important["version"]

    def _scrape_file(self, scraper):
        """Scrape with the given scraper.
        :scraper: Scraper instance
        """
        scraper.scrape_file()
        if scraper.streams:
            self._scraper_results.append(scraper.streams)
        self.info[len(self.info)] = scraper.info()
        if scraper.well_formed is not None:
            if self.well_formed in [None, True]:
                self.well_formed = scraper.well_formed

    def _check_utf8(self, check_wellformed):
        """
        UTF-8 check only for UTF-8.

        We know the charset after actual scraping.
        """
        if "charset" in self.streams[0] and \
                self.streams[0]["charset"] == "UTF-8":
            scraper = JHoveUtf8Scraper(filename=self.filename,
                                       mimetype="(:unav)",
                                       check_wellformed=check_wellformed)
            self._scrape_file(scraper)

    def _check_mime(self, check_wellformed=True):
        """
        Check that predefined mimetype and resulted mimetype match.

        :check_wellformed: Whether full scraping is used or not.
        """
        scraper = MimeScraper(filename=self.filename,
                              mimetype=self._predefined_mimetype,
                              version=self._params.get("version", None),
                              check_wellformed=check_wellformed,
                              params={"mimetype": self.mimetype,
                                      "version": self.version,
                                      "well_formed": self.well_formed})
        self._scrape_file(scraper)

    def _check_mimetype_version(self):
        """
        Detect the MIME type and version.

        Ideally the MIME type and version from the scraper are used, but if
        they are not available, values supplied by the detector are used.
        """
        if not self.well_formed and self._predefined_mimetype:
            self.streams[0]["mimetype"] = self._predefined_mimetype
            self.mimetype = self._predefined_mimetype
        else:
            self.mimetype = self.streams[0]["mimetype"]

        if self.streams[0]["version"] not in LOSE or not self._predefined_version:
            self.version = self.streams[0]["version"]
        elif self._predefined_version:
            self.streams[0]["version"] = self._predefined_version
            self.version = self._predefined_version

    def scrape(self, check_wellformed=True):
        """Scrape file and collect metadata.
        :check_wellformed: True, full scraping; False, skip well-formed check.
        """
        self.detect_filetype()

        # File not found or MIME type could not be determined
        if not self._predefined_mimetype:
            self.streams = {}
            return

        for scraper_class in iter_scrapers(
                mimetype=self._predefined_mimetype, version=self._predefined_version,
                check_wellformed=check_wellformed, params=self._params):
            scraper = scraper_class(
                filename=self.filename,
                mimetype=self._predefined_mimetype,
                check_wellformed=check_wellformed,
                params=self._params)
            self._scrape_file(scraper)
        self.streams = generate_metadata_dict(self._scraper_results, LOSE)
        self._check_utf8(check_wellformed)
        self._check_mimetype_version()
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
        """
        self.mimetype = None
        self.version = None
        self.streams = None
        self.info = {}
        self.well_formed = None
        self._predefined_mimetype = self._params.get("mimetype", None)
        self._predefined_version = self._params.get("version", None)

        file_exists = FileExists(self.filename, None)
        self._scrape_file(file_exists)

        if file_exists.well_formed is False:
            return

        self._identify()

    def is_textfile(self):
        """Find out if file is a text file.
        :returns: True, if file is a text file, false otherwise
        """
        scraper = TextfileScraper(self.filename, "text/plain")
        scraper.scrape_file()
        return scraper.well_formed

    def checksum(self, algorithm="MD5"):
        """Return the checksum of the file with given algorithm.
        :algorithm: MD5 or SHA variant
        :returns: Calculated checksum
        """
        return hexdigest(self.filename, algorithm)
