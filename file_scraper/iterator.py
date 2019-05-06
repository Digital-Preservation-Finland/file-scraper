"""Scraper iterator."""
# flake8: noqa
from file_scraper.detectors import FidoDetector, MagicDetector
from file_scraper.csv.csv_scraper import CsvScraper
from file_scraper.dummy.dummy_scraper import ScraperNotFound
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from file_scraper.jhove.jhove_scraper import (JHoveGifScraper, JHoveHtmlScraper,
                                              JHoveJpegScraper, JHoveTiffScraper,
                                              JHovePdfScraper, JHoveWavScraper)
from file_scraper.lxml.lxml_scraper import LxmlScraper
from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from file_scraper.magic_scraper.magic_scraper import MagicScraper
from file_scraper.office.office_scraper import OfficeScraper
from file_scraper.pil.pil_scraper import PilScraper
from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from file_scraper.pspp.pspp_scraper import PsppScraper
from file_scraper.schematron.schematron_scraper import SchematronScraper
from file_scraper.verapdf.verapdf_scraper import VerapdfScraper
from file_scraper.vnu.vnu_scraper import VnuScraper
from file_scraper.wand.wand_scraper import WandScraper
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from file_scraper.xmllint.xmllint_scraper import XmllintScraper
from file_scraper.warctools.warctools_scraper import (GzipWarctoolsScraper,
                                                      WarcWarctoolsScraper,
                                                      ArcWarctoolsScraper)

def iter_detectors():
    """
    Iterate detectors.

    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    for cls in [FidoDetector, MagicDetector]:
        yield cls


def iter_scrapers(mimetype, version, check_wellformed=True, params=None):
    """
    Iterate scrapers.

    :mimetype: Identified mimetype of the file
    :version: Identified file format version
    :check_wellformed: True for the full well-formed check, False for just
                       identification and metadata scraping
    :params: Extra parameters needed for the scraper
    :returns: scraper class
    """
    scraper_found = False

    scrapers = [WandScraper, GhostscriptScraper, JHoveGifScraper,
                JHoveHtmlScraper, JHoveJpegScraper, JHoveTiffScraper,
                JHovePdfScraper, JHoveWavScraper, CsvScraper, FFMpegScraper,
                LxmlScraper, MediainfoScraper, OfficeScraper, PilScraper,
                PngcheckScraper, PsppScraper, SchematronScraper,
                VerapdfScraper, VnuScraper, XmllintScraper, GzipWarctoolsScraper,
                WarcWarctoolsScraper, ArcWarctoolsScraper, MagicScraper]

    for scraper in scrapers:
        if scraper.is_supported(mimetype, version, check_wellformed, params):
            scraper_found = True
            yield scraper

    if not scraper_found:
        yield ScraperNotFound
