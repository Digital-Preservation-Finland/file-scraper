"""Scraper iterator."""
# flake8: noqa
from __future__ import annotations

from typing import Iterator
from file_scraper.base import BaseDetector, BaseExtractor
from file_scraper.csv_extractor.csv_extractor import CsvExtractor
from file_scraper.detectors import (EpubDetector,
                                    FidoDetector,
                                    MagicDetector,
                                    AtlasTiDetector,
                                    SiardDetector,
                                    SegYDetector,
                                    ODFDetector)
from file_scraper.dbptk.dbptk_extractor import DbptkExtractor
from file_scraper.dpx.dpx_extractor import DpxExtractor
from file_scraper.dummy.dummy_extractor import (DetectedMimeVersionMetadataExtractor,
                                                DetectedMimeVersionExtractor,
                                                ExtractorNotFound)
from file_scraper.ffmpeg.ffmpeg_extractor import FFMpegMetaExtractor, FFMpegExtractor
from file_scraper.ghostscript.ghostscript_extractor import GhostscriptExtractor
from file_scraper.jhove.jhove_extractor import (JHoveAiffExtractor,
                                                JHoveDngExtractor,
                                                JHoveEpubExtractor,
                                                JHoveGifExtractor,
                                                JHoveHtmlExtractor,
                                                JHoveJpegExtractor,
                                                JHovePdfExtractor,
                                                JHoveTiffExtractor,
                                                JHoveWavExtractor)
from file_scraper.logger import LOGGER
from file_scraper.lxml_extractor.lxml_extractor import LxmlExtractor
from file_scraper.magic_extractor.magic_extractor import (MagicBinaryExtractor,
                                                          MagicTextExtractor)
from file_scraper.mediainfo.mediainfo_extractor import MediainfoExtractor
from file_scraper.office.office_extractor import OfficeExtractor
from file_scraper.pil.pil_extractor import PilExtractor
from file_scraper.pngcheck.pngcheck_extractor import PngcheckExtractor
from file_scraper.pspp.pspp_extractor import PsppExtractor
from file_scraper.textfile.textfile_extractor import (TextEncodingMetaExtractor,
                                                      TextEncodingExtractor,
                                                      TextfileExtractor)
from file_scraper.verapdf.verapdf_extractor import VerapdfExtractor
from file_scraper.vnu.vnu_extractor import VnuExtractor
from file_scraper.wand.wand_extractor import WandExtractor
from file_scraper.warctools.warctools_extractor import (WarctoolsFullExtractor,
                                                        WarctoolsExtractor)
from file_scraper.xmllint.xmllint_extractor import XmllintExtractor
from file_scraper.exiftool.exiftool_extractor import ExifToolDngExtractor
from file_scraper.jpylyzer.jpylyzer_extractor import JpylyzerExtractor


def iter_detectors() -> Iterator[type[BaseDetector]]:
    """
    Iterate detectors.

    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    yield from [
        EpubDetector,
        FidoDetector,
        MagicDetector,
        AtlasTiDetector,
        SiardDetector,
        SegYDetector,
        ODFDetector,
    ]


def iter_extractors(
    mimetype: str | None,
    version: str | None,
    check_wellformed: bool = True,
    params: dict | None = None,
) -> Iterator[type[BaseExtractor]]:
    """
    Iterate extractors.

    :param mimetype: Identified mimetype of the file
    :param version: Identified file format version
    :param check_wellformed: True for the full well-formed check, False for just
        identification and metadata scraping
    :param params: Extra parameters needed for the extractor
    :returns: extractor class
    """
    extractor_found = False

    extractors: list[type[BaseExtractor]] = [
        CsvExtractor,
        DbptkExtractor,
        DetectedMimeVersionMetadataExtractor,
        DetectedMimeVersionExtractor,
        DpxExtractor,
        ExifToolDngExtractor,
        FFMpegMetaExtractor,
        FFMpegExtractor,
        GhostscriptExtractor,
        JHoveAiffExtractor,
        JHoveDngExtractor,
        JHoveEpubExtractor,
        JHoveGifExtractor,
        JHoveHtmlExtractor,
        JHoveJpegExtractor,
        JHovePdfExtractor,
        JHoveTiffExtractor,
        JHoveWavExtractor,
        JpylyzerExtractor,
        LxmlExtractor,
        MagicBinaryExtractor,
        MagicTextExtractor,
        MediainfoExtractor,
        OfficeExtractor,
        PilExtractor,
        PngcheckExtractor,
        PsppExtractor,
        TextEncodingMetaExtractor,
        TextEncodingExtractor,
        TextfileExtractor,
        VerapdfExtractor,
        VnuExtractor,
        WandExtractor,
        WarctoolsFullExtractor,
        WarctoolsExtractor,
        XmllintExtractor,
    ]

    for extractor in extractors:
        if extractor.is_supported(mimetype, version, check_wellformed, params):
            extractor_found = True
            yield extractor
        else:
            LOGGER.debug(
                "Skipping unsupported extractor %s", extractor.__name__
            )

    if not extractor_found:
        yield ExtractorNotFound
