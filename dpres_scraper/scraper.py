"""File metadata scraper
"""
from dpres_scraper.utils import combine_metadata, combine_element
from dpres_scraper.detectors import FidoDetector, MagicDetector

from dpres_scraper.iterator import iter_scrapers
from dpres_scraper.scrapers.file import TextPlainFile
from dpres_scraper.scrapers.dummy import Dummy

# Keep this in priority order
DETECTORS = [FidoDetector, MagicDetector]

LOOSE = [None, 'application/zip', 'application/octet-stream',
         'text/xml', '0', '(:unav)', '(:unap)']


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

    def identify(self):
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

    def scrape(self, validation=True):
        """Scrape file metadata
        """
        if self.info is None:
            self.info = {}
        for scraper in iter_scrapers(
                filename=self.filename, mimetype=self.mimetype,
                version=self.version, validate=validation):
            scraper.scrape_file()
            self.streams = combine_metadata(
                 self.streams, scraper.streams, LOOSE)
            self.info[len(self.info)] = scraper.info
            if self.well_formed in [None, True]:
                 self.well_formed = scraper.well_formed

        if not self.streams:
            scraper = Dummy(self.mimetype, self.filename)
            scraper.scrape_file()
            self.streams = combine_metadata(
                self.streams, scraper.streams)
            self.info[len(self.info)] = scraper.info

        if not 'mimetype' in self.streams[0]:
            self.streams[0]['mimetype'] = self.mimetype
        else:
            self.mimetype = combine_element(
                self.mimetype, self.streams[0]['mimetype'], LOOSE)
        if not 'version' in self.streams[0]:
            self.streams[0]['version'] = self.version
        else:
            self.version = combine_element(
                self.version, self.streams[0]['version'], LOOSE)

    def is_textfile(self):
        """Find out if file is a text file.
        """
        scraper = TextPlainFile(self.mimetype, self.filename, True)
        scraper.scrape_file()
        return scraper.well_formed
