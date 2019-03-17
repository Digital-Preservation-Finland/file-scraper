"""Scraper iterator"""
from file_scraper.base import BaseScraper, BaseDetector
from file_scraper.detectors import FidoDetector, MagicDetector
from file_scraper.jhove_base import JHove
from file_scraper.magic_base import BinaryMagic, TextMagic
from file_scraper.mediainfo_base import Mediainfo
from file_scraper.pil_base import Pil
from file_scraper.wand_base import Wand
from file_scraper.scrapers.jhove import GifJHove, HtmlJHove, JpegJHove, \
    PdfJHove, TiffJHove, Utf8JHove, WavJHove
from file_scraper.scrapers.xmllint import Xmllint
from file_scraper.scrapers.lxml_encoding import XmlEncoding
from file_scraper.scrapers.warctools import GzipWarctools, WarcWarctools, \
    ArcWarctools
from file_scraper.scrapers.ghostscript import GhostScript
from file_scraper.scrapers.pngcheck import Pngcheck
from file_scraper.scrapers.csv_scraper import Csv
from file_scraper.scrapers.mediainfo import MpegMediainfo
from file_scraper.scrapers.ffmpeg import FFMpeg
from file_scraper.scrapers.office import Office
from file_scraper.scrapers.magic import TextFileMagic, XmlFileMagic, \
    HtmlFileMagic, PdfFileMagic, OfficeFileMagic, PngFileMagic, \
    JpegFileMagic, Jp2FileMagic, TiffFileMagic, XhtmlFileMagic, \
    ArcFileMagic
from file_scraper.scrapers.wand import TiffWand, ImageWand
from file_scraper.scrapers.pil import ImagePil, JpegPil, TiffPil
from file_scraper.scrapers.pspp import Pspp
from file_scraper.scrapers.verapdf import VeraPdf
from file_scraper.scrapers.dpx import Dpx
from file_scraper.scrapers.vnu import Vnu
from file_scraper.scrapers.dummy import ScraperNotFound


def iter_detectors():
    """Iterate detectors.
    :returns: detector class

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python
    """
    for cls in BaseDetector.__subclasses__():
        yield cls


def iter_scrapers(mimetype, version, validation=True, params=None):
    """
    Iterate scrapers
    :mimetype: Identified mimetype of the file
    :version: Identified file format version
    :validation: True for the full validation, False for just
                identification and metadata scraping
    :params: Extra parameters needed for the scraper
    :returns: scraper class
    """

    # pylint: disable=no-member
    if params is None:
        params = {}
    found_validator = False

    for cls in BaseScraper.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in BinaryMagic.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in TextMagic.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in JHove.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in Mediainfo.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in Pil.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    for cls in Wand.__subclasses__():
        if cls.is_supported(mimetype, version, validation, params):
            found_validator = True
            yield cls

    if not found_validator:
        yield ScraperNotFound
