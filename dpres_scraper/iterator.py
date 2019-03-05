"""Scraper iterator"""

from dpres_scraper.base import BaseScraper
from dpres_scraper.jhove_base import JHove
from dpres_scraper.magic_base import BinaryMagic, TextMagic
from dpres_scraper.mediainfo_base import Mediainfo
from dpres_scraper.pil_base import Pil
from dpres_scraper.wand_base import Wand
from dpres_scraper.scrapers.jhove import GifJHove, HtmlJHove, JpegJHove, \
    PdfJHove, TiffJHove, Utf8JHove, WavJHove
from dpres_scraper.scrapers.xmllint import Xmllint
from dpres_scraper.scrapers.lxml_encoding import XmlEncoding
from dpres_scraper.scrapers.warctools import WarcWarctools, ArcWarctools
from dpres_scraper.scrapers.ghostscript import GhostScript
from dpres_scraper.scrapers.pngcheck import Pngcheck
from dpres_scraper.scrapers.csv_scraper import Csv
from dpres_scraper.scrapers.mediainfo import MpegMediainfo, DataMediainfo, \
    VideoMediainfo
from dpres_scraper.scrapers.office import Office
from dpres_scraper.scrapers.file import TextPlainFile
from dpres_scraper.scrapers.magic import TextFileMagic, XmlFileMagic, \
    HtmlFileMagic, PdfFileMagic, OfficeFileMagic, PngFileMagic, \
    JpegFileMagic, Jp2FileMagic, TiffFileMagic
from dpres_scraper.scrapers.wand import TiffWand, ImageWand
from dpres_scraper.scrapers.pil import ImagePil, JpegPil, TiffPil
from dpres_scraper.scrapers.pspp import Pspp
from dpres_scraper.scrapers.verapdf import VeraPdf
from dpres_scraper.scrapers.dpx import Dpx
from dpres_scraper.scrapers.vnu import Vnu
from dpres_scraper.scrapers.dummy import Dummy


def iter_scrapers(filename, mimetype, version, validation=True):
    """
    Iterate scrapers
    :returns: scraper class

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python
    """

    # pylint: disable=no-member

    found_validator = False

    for cls in BaseScraper.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in BinaryMagic.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in TextMagic.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in JHove.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in Mediainfo.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in Pil.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    for cls in Wand.__subclasses__():
        obj = cls(filename, mimetype, validation)
        if obj.is_supported(version):
            found_validator = True
            yield obj

    if not found_validator:
        obj = Dummy(filename, mimetype, validation)
        yield obj
