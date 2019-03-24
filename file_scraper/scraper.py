"""File metadata scraper
"""
from file_scraper.utils import combine_metadata

from file_scraper.iterator import iter_scrapers, iter_detectors
from file_scraper.scrapers.jhove import Utf8JHove
from file_scraper.scrapers.textfile import CheckTextFile
from file_scraper.scrapers.dummy import FileExists
from file_scraper.utils import hexdigest

LOSE = [None, '0', '(:unav)', '(:unap)']


class Scraper(object):
    """File indentifier and scraper
    """

    # pylint: disable=no-member, too-many-instance-attributes

    def __init__(self, filename, **kwargs):
        """Initialize scraper
        :filename: File path
        :kwargs: Extra arguments for certain scrapers
        """
        self.filename = filename
        self.mimetype = None
        self.version = None
        self.streams = None
        self.well_formed = None
        self.info = None
        self._important = {}
        self._params = kwargs

    def _identify(self):
        """Identify file format and version.
        """
        self.info = {}
        for detector in iter_detectors():
            tool = detector(self.filename)
            tool.detect()
            self.info[len(self.info)] = tool.info
            important = tool.get_important()
            if self.mimetype in LOSE:
                self.mimetype = tool.mimetype
            if self.mimetype == tool.mimetype and \
                    self.version in LOSE:
                self.version = tool.version
            if 'mimetype' in important and \
                    important['mimetype'] is not None:
                self.mimetype = important['mimetype']
            if 'version' in important and \
                    important['version'] is not None:
                self.mimetype = important['version'][self.mimetype]

    def _scrape_file(self, scraper):
        """Scrape with a given scraper.
        :scraper: Scraper instance
        """
        scraper.scrape_file()
        self._important.update(scraper.get_important())
        self.streams = combine_metadata(
            stream=self.streams, metadata=scraper.streams,
            lose=LOSE, important=self._important)
        self.info[len(self.info)] = scraper.info
        if scraper.well_formed is not None:
            if self.well_formed in [None, True]:
                self.well_formed = scraper.well_formed

    def _check_utf8(self, check_wellformed):
        """UTF-8 check only for UTF-8, we know the charset
        after actual scraping
        """
        if 'charset' in self.streams[0] and \
                self.streams[0]['charset'] == 'UTF-8':
            scraper = Utf8JHove(self.filename, self.mimetype, check_wellformed)
            self._scrape_file(scraper)

    def _check_mimetype_version(self):
        """We wan to use scraper's mimetype and version, but
        if not detected, let's use detectors' values
        """
        if self.streams[0]['mimetype'] is not None:
            self.mimetype = self.streams[0]['mimetype']
        else:
            self.streams[0]['mimetype'] = self.mimetype
        if self.streams[0]['version'] is not None:
            self.version = self.streams[0]['version']
        else:
            self.streams[0]['version'] = self.version

    def scrape(self, check_wellformed=True):
        """Scrape file and collect metadata.
        :check_wellformed: True, full scraping; False, skip well-formed check.
        """
        self.streams = None
        self.info = {}
        self.well_formed = None

        file_exists = FileExists(self.filename, None)
        self._scrape_file(file_exists)

        if file_exists.well_formed is False:
            return

        self._identify()
        for scraper_class in iter_scrapers(
                mimetype=self.mimetype, version=self.version,
                check_wellformed=check_wellformed, params=self._params):
            scraper = scraper_class(self.filename, self.mimetype,
                                    check_wellformed, self._params)
            self._scrape_file(scraper)

        self._check_utf8(check_wellformed)
        self._check_mimetype_version()

    def is_textfile(self):
        """Find out if file is a text file.
        :returns: True, if file is a text file, false otherwise
        """
        scraper = CheckTextFile(self.filename, self.mimetype)
        scraper.scrape_file()
        return scraper.well_formed

    def checksum(self, algorithm='MD5'):
        """Return the checksum of the file with given algorithm.
        :algorithm: MD5 or SHA variant
        :returns: Calculated checksum
        """
        return hexdigest(self.filename, algorithm)
