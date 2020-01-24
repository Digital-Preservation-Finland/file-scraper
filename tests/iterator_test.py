"""
Test for file_scraper.scrapers.

This module tests that:
    - iter_scrapers(mimetype, version) returns the correct scrapers.
    - iter_detectors() returns the correct detectors.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.iterator import iter_scrapers, iter_detectors


@pytest.mark.parametrize(
    ["mimetype", "version", "scraper_classes"],
    [
        ("application/x-spss-por", None, ["PsppScraper"]),
        ("application/warc", None, ["WarcWarctoolsScraper"]),
        ("text/csv", None, ["CsvScraper", "MagicScraper",
                            "TextEncodingScraper"]),
        ("text/plain", None, ["MagicScraper", "TextEncodingScraper"]),
        ("video/mpeg", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/mp4", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/MP2T", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/x-matroska", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/dv", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/quicktime", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("application/pdf", "1.2", ["MagicScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.3", ["MagicScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.4", ["MagicScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.5", ["MagicScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.6", ["MagicScraper", "JHovePdfScraper"]),
        ("application/pdf", "A-1a", ["MagicScraper", "JHovePdfScraper",
                                     "VerapdfScraper"]),
        ("application/pdf", "A-1b", ["MagicScraper", "JHovePdfScraper",
                                     "VerapdfScraper"]),
        ("application/pdf", "A-2a",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "A-2b",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "A-2u",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "A-3a",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "A-3b",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "A-3u",
         ["MagicScraper", "GhostscriptScraper", "VerapdfScraper"]),
        ("application/pdf", "1.7", ["MagicScraper", "GhostscriptScraper"]),
        ("image/tiff", None,
         ["JHoveTiffScraper", "MagicScraper", "PilScraper", "WandScraper"]),
        ("image/jpeg", None,
         ["JHoveJpegScraper", "MagicScraper", "PilScraper", "WandScraper"]),
        ("image/gif", None, ["JHoveGifScraper", "PilScraper", "WandScraper"]),
        ("text/html", "4.01", ["JHoveHtmlScraper", "MagicScraper",
                               "TextEncodingScraper"]),
        ("text/html", "5.0", ["VnuScraper", "LxmlScraper", "MagicScraper",
                              "TextEncodingScraper"]),
        ("image/png", None,
         ["PngcheckScraper", "MagicScraper", "PilScraper", "WandScraper"]),
        ("application/warc", None, ["WarcWarctoolsScraper"]),
        ("application/x-internet-archive", None,
         ["MagicScraper", "ArcWarctoolsScraper"]),
        ("text/xml", "1.0", ["XmllintScraper", "LxmlScraper", "MagicScraper",
                             "TextEncodingScraper"]),
        ("application/xhtml+xml", "1.0", ["JHoveHtmlScraper", "MagicScraper",
                                          "TextEncodingScraper"]),
        ("audio/x-wav", None, ["JHoveWavScraper", "MediainfoScraper"]),
        ("application/vnd.oasis.opendocument.text", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.oasis.opendocument.spreadsheet", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.oasis.opendocument.presentation", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.oasis.opendocument.graphics", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.oasis.opendocument.formula", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/msword", None, ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.ms-excel", None, ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.ms-powerpoint", None,
         ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", None, ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         None, ["OfficeScraper", "MagicScraper"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", None, ["OfficeScraper", "MagicScraper"]),
        ("test/unknown", None, ["ScraperNotFound"])
    ])
def test_iter_scrapers(mimetype, version, scraper_classes):
    """Test scraper discovery."""
    scrapers = iter_scrapers(mimetype, version)
    assert set([x.__name__ for x in scrapers]) == set(scraper_classes)


def test_iter_detectors():
    """Test detector discovery."""
    detectors = iter_detectors()
    assert set([x.__name__ for x in detectors]) == set(["FidoDetector",
                                                        "MagicDetector",
                                                        "PredefinedDetector"])
