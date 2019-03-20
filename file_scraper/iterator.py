"""Scraper iterator"""
from file_scraper.base import BaseScraper
from file_scraper.detectors import FidoDetector, MagicDetector
from file_scraper.jhove_base import JHove
from file_scraper.magic_base import BinaryMagic, TextMagic
from file_scraper.mediainfo_base import Mediainfo
from file_scraper.pil_base import Pil
from file_scraper.wand_base import Wand
from file_scraper.scrapers.dummy import ScraperNotFound


def iter_detectors():
    """Iterate detectors.
    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    for cls in [FidoDetector, MagicDetector]:
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

    # pylint: disable=no-member,too-many-branches
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
