"""File metadata scraper
"""
from dpres_scraper.utils import combine_metadata

from dpres_scraper.iterator import iter_scrapers, iter_detectors
from dpres_scraper.scrapers.jhove import Utf8JHove
from dpres_scraper.scrapers.file import TextPlainFile
from dpres_scraper.scrapers.dummy import FileExists

LOSE = [None, '0', '(:unav)', '(:unap)']


class Scraper(object):
    """File indentifier and scraper
    """

# pylint: disable=no-member

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
        self._params = kwargs

    def _identify(self):
        """Identify file format and version.
        """
        self.info = {}
        for detector in iter_detectors():
            tool = detector(self.filename)
            tool.detect()
            self.info[len(self.info)] = tool.info
            important = tool.is_important()
            if self.mimetype in LOSE:
                self.mimetype = tool.mimetype
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
        self.streams = combine_metadata(
            stream=self.streams, metadata=scraper.streams,
            lose=LOSE, important=scraper.is_important())
        self.info[len(self.info)] = scraper.info
        if scraper.well_formed is not None:
            if self.well_formed in [None, True]:
                self.well_formed = scraper.well_formed

    def scrape(self, validation=True):
        """Scrape file and collect metadata.
        :validation: True, full scraping; False, skip well-formed check.
        """
        self.streams = None
        self.info = {}
        self.well_formed = None

        file_exists = FileExists(self.filename, None)
        self._scrape_file(file_exists)

        if file_exists.well_formed not in [None, True]:
            return

        self._identify()
        for scraper_class in iter_scrapers(
                mimetype=self.mimetype, version=self.version,
                validation=validation, params=self._params):
            scraper = scraper_class(self.filename, self.mimetype,
                                    validation, self._params)
            self._scrape_file(scraper)

        if 'charset' in self.streams[0] and \
                self.streams[0]['charset'] == 'UTF-8':
            scraper = Utf8JHove(self.filename, self.mimetype)
            self._scrape_file(scraper)

        self.mimetype = self.streams[0]['mimetype']
        self.version = self.streams[0]['version']

    def is_textfile(self):
        """Find out if file is a text file.
        :returns: True, if file is a text file, false otherwise
        """
        scraper = TextPlainFile(self.filename, self.mimetype)
        scraper.scrape_file()
        return scraper.well_formed
