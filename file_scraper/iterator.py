"""Scraper iterator."""
# flake8: noqa

from file_scraper.csv_scraper.csv_scraper import CsvScraper
from file_scraper.detectors import (EpubDetector,
                                    FidoDetector,
                                    MagicDetector,
                                    PredefinedDetector,
                                    AtlasTiDetector,
                                    SiardDetector,
                                    SegYDetector,
                                    ODFDetector)
from file_scraper.dbptk.dbptk_scraper import DbptkScraper
from file_scraper.dpx.dpx_scraper import DpxScraper
from file_scraper.dummy.dummy_scraper import (DetectedMimeVersionMetadataScraper,
                                              DetectedMimeVersionScraper,
                                              ScraperNotFound)
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegMetaScraper, FFMpegScraper
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from file_scraper.graders import ContainerStreamsGrader, MIMEGrader, TextGrader
from file_scraper.jhove.jhove_scraper import (JHoveAiffScraper,
                                              JHoveDngScraper,
                                              JHoveEpubScraper,
                                              JHoveGifScraper,
                                              JHoveHtmlScraper,
                                              JHoveJpegScraper,
                                              JHovePdfScraper,
                                              JHoveTiffScraper,
                                              JHoveWavScraper)
from file_scraper.lxml_scraper.lxml_scraper import LxmlScraper
from file_scraper.magic_scraper.magic_scraper import (MagicBinaryScraper,
                                                      MagicTextScraper)
from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from file_scraper.office.office_scraper import OfficeScraper
from file_scraper.pil.pil_scraper import PilScraper
from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from file_scraper.pspp.pspp_scraper import PsppScraper
from file_scraper.schematron.schematron_scraper import SchematronScraper
from file_scraper.textfile.textfile_scraper import (TextEncodingMetaScraper,
                                                    TextEncodingScraper,
                                                    TextfileScraper)
from file_scraper.verapdf.verapdf_scraper import VerapdfScraper
from file_scraper.vnu.vnu_scraper import VnuScraper
from file_scraper.wand.wand_scraper import WandScraper
from file_scraper.warctools.warctools_scraper import (GzipWarctoolsScraper,
                                                      WarctoolsFullScraper,
                                                      WarctoolsScraper)
from file_scraper.xmllint.xmllint_scraper import XmllintScraper
from file_scraper.exiftool.exiftool_scraper import ExifToolDngScraper
from file_scraper.jpylyzer.jpylyzer_scraper import JpylyzerScraper


def iter_detectors():
    """
    Iterate detectors.

    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    yield from [EpubDetector,
                FidoDetector,
                MagicDetector,
                PredefinedDetector,
                AtlasTiDetector,
                SiardDetector,
                SegYDetector,
                ODFDetector]


def iter_graders():
    """Iterate graders.

    :returns: grader class
    """
    yield from [MIMEGrader, TextGrader, ContainerStreamsGrader]


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
        CsvScraper,
        DbptkScraper,
        DetectedMimeVersionMetadataScraper,
        DetectedMimeVersionScraper,
        DpxScraper,
        ExifToolDngScraper,
        FFMpegMetaScraper,
        FFMpegScraper,
        GhostscriptScraper,
        GzipWarctoolsScraper,
        JHoveAiffScraper,
        JHoveDngScraper,
        JHoveEpubScraper,
        JHoveGifScraper,
        JHoveHtmlScraper,
        JHoveJpegScraper,
        JHovePdfScraper,
        JHoveTiffScraper,
        JHoveWavScraper,
        JpylyzerScraper,
        LxmlScraper,
        MagicBinaryScraper,
        MagicTextScraper,
        MediainfoScraper,
        OfficeScraper,
        PilScraper,
        PngcheckScraper,
        PsppScraper,
        SchematronScraper,
        TextEncodingMetaScraper,
        TextEncodingScraper,
        TextfileScraper,
        VerapdfScraper,
        VnuScraper,
        WandScraper,
        WarctoolsFullScraper,
        WarctoolsScraper,
        XmllintScraper
    ]

    for scraper in scrapers:
        if scraper.is_supported(mimetype, version, check_wellformed, params):
            scraper_found = True
            yield scraper

    if not scraper_found:
        yield ScraperNotFound
