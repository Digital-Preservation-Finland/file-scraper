"""Scraper iterator."""
# flake8: noqa
from __future__ import unicode_literals

from file_scraper.csv.csv_scraper import CsvScraper
from file_scraper.detectors import (FidoDetector, MagicDetector,
                                    PredefinedDetector)
from file_scraper.dpx.dpx_scraper import DpxScraper
from file_scraper.dummy.dummy_scraper import (
    ScraperNotFound, DetectedMimeVersionScraper,
    DetectedMimeVersionMetadataScraper)
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from file_scraper.jhove.jhove_scraper import (JHoveGifScraper,
                                              JHoveHtmlScraper,
                                              JHoveJpegScraper,
                                              JHovePdfScraper,
                                              JHoveTiffScraper,
                                              JHoveWavScraper)
from file_scraper.lxml_scraper.lxml_scraper import LxmlScraper
from file_scraper.magic_scraper.magic_scraper import (MagicTextScraper,
                                                      MagicBinaryScraper)
from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from file_scraper.office.office_scraper import OfficeScraper
from file_scraper.pil.pil_scraper import PilScraper
from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from file_scraper.pspp.pspp_scraper import PsppScraper
from file_scraper.schematron.schematron_scraper import SchematronScraper
from file_scraper.textfile.textfile_scraper import (TextEncodingScraper,
                                                    TextEncodingMetaScraper,
                                                    TextfileScraper)
from file_scraper.verapdf.verapdf_scraper import VerapdfScraper
from file_scraper.vnu.vnu_scraper import VnuScraper
from file_scraper.wand.wand_scraper import WandScraper
from file_scraper.warctools.warctools_scraper import (
    ArcWarctoolsScraper, GzipWarctoolsScraper, WarcWarctoolsFullScraper,
    WarcWarctoolsScraper)
from file_scraper.xmllint.xmllint_scraper import XmllintScraper


def iter_detectors():
    """
    Iterate detectors.

    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    for cls in [FidoDetector, MagicDetector, PredefinedDetector]:
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

    scrapers = [
        WarcWarctoolsFullScraper, ArcWarctoolsScraper, GzipWarctoolsScraper,
        WarcWarctoolsScraper, CsvScraper, DetectedMimeVersionMetadataScraper,
        DetectedMimeVersionScraper, DpxScraper, FFMpegScraper,
        GhostscriptScraper, JHoveGifScraper, JHoveHtmlScraper,
        JHoveJpegScraper, JHovePdfScraper, JHoveTiffScraper,
        JHoveWavScraper, LxmlScraper, MagicTextScraper, MagicBinaryScraper,
        MediainfoScraper, OfficeScraper, PilScraper, PngcheckScraper,
        PsppScraper, SchematronScraper, TextfileScraper, TextEncodingScraper,
        TextEncodingMetaScraper, VerapdfScraper, VnuScraper, WandScraper,
        XmllintScraper]

    for scraper in scrapers:
        if scraper.is_supported(mimetype, version, check_wellformed, params):
            scraper_found = True
            yield scraper

    if not scraper_found:
        yield ScraperNotFound
