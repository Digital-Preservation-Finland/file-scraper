"""File metadata scraper
"""
from dpres_scraper.utils import combine_metadata, combine_element
from dpres_scraper.detectors import FidoDetector, MagicDetector

from dpres_scraper.iterator import iter_scrapers
from dpres_scraper.scrapers.jhove import Utf8JHove
from dpres_scraper.scrapers.file import TextPlainFile

# Keep this in priority order
DETECTORS = [FidoDetector, MagicDetector]

LOOSE = [None, '0', '(:unav)', '(:unap)']


class Scraper(object):
    """File indentifier and scraper
    """

    def __init__(self, filename):
        """Initialize scraper
        """
        self.filename = filename
        self.mimetype = None
        self.version = None
        self.streams = None
        self.well_formed = None
        self.info = None

    def _identify(self):
        """Identify file format and version
        """
        self.info = {}
        for tool in DETECTORS:
            detector_tool = tool(self.filename)
            detector_tool.detect()
            self.info[len(self.info)] = detector_tool.info
            if self.mimetype in LOOSE:
                self.mimetype = detector_tool.mimetype
                self.version = detector_tool.version

    def _scrape_file(self, scraper):
        """Scrape file and collect metadata.
        """
        scraper.scrape_file()
        self.streams = combine_metadata(
            self.streams, scraper.streams, LOOSE)
        self.info[len(self.info)] = scraper.info
        if scraper.well_formed is not None:
            if self.well_formed in [None, True]:
                self.well_formed = scraper.well_formed

    def scrape(self, validation=True):
        """Scrape file metadata
        """
        self.streams = None
        self.info = {}
        self.well_formed = None
        self._identify()
        for scraper in iter_scrapers(
                filename=self.filename, mimetype=self.mimetype,
                version=self.version, validation=validation):
            self._scrape_file(scraper)

        if 'charset' in self.streams[0] and \
            self.streams[0]['charset'] == 'UTF-8':
                scraper = Utf8JHove(self.filename, self.mimetype)
                self._scrape_file(scraper)

        self.mimetype = self.streams[0]['mimetype']
        self.version = self.streams[0]['version']

    def is_textfile(self):
        """Find out if file is a text file.
        """
        scraper = TextPlainFile(self.mimetype, self.filename, True)
        scraper.scrape_file()
        return scraper.well_formed
