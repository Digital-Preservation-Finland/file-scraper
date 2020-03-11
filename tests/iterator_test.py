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
        ("image/x-dpx", None, ["DpxScraper", "DetectedVersionScraper"]),
        ("application/x-spss-por", None, ["PsppScraper"]),
        ("application/warc", None, ["WarcWarctoolsScraper"]),
        ("text/csv", None, ["CsvScraper", "MagicTextScraper",
                            "TextEncodingScraper"]),
        ("text/plain", None, ["MagicTextScraper", "TextfileScraper",
                              "TextEncodingScraper"]),
        ("video/mpeg", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/mp4", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/MP2T", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/x-matroska", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/dv", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("video/quicktime", None, ["MediainfoScraper", "FFMpegScraper"]),
        ("application/pdf", "1.2", ["MagicBinaryScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.3", ["MagicBinaryScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.4", ["MagicBinaryScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.5", ["MagicBinaryScraper", "JHovePdfScraper"]),
        ("application/pdf", "1.6", ["MagicBinaryScraper", "JHovePdfScraper"]),
        ("application/pdf", "A-1a", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper",
                                     "DetectedVersionScraper"]),
        ("application/pdf", "A-1b", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper",
                                     "DetectedVersionScraper"]),
        ("application/pdf", "A-2a",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "A-2b",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "A-2u",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "A-3a",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "A-3b",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "A-3u",
         ["MagicBinaryScraper", "GhostscriptScraper", "VerapdfScraper",
          "DetectedVersionScraper"]),
        ("application/pdf", "1.7", ["MagicBinaryScraper",
                                    "GhostscriptScraper"]),
        ("image/tiff", None, ["JHoveTiffScraper", "MagicBinaryScraper",
                              "PilScraper", "WandScraper"]),
        ("image/jpeg", None, ["JHoveJpegScraper", "MagicBinaryScraper",
                              "PilScraper", "WandScraper"]),
        ("image/gif", None, ["JHoveGifScraper", "MagicBinaryScraper",
                             "PilScraper", "WandScraper"]),
        ("text/html", "4.01", ["DetectedVersionScraper", "JHoveHtmlScraper",
                               "LxmlScraper", "MagicTextScraper",
                               "TextEncodingScraper"]),
        ("text/html", "5.0", ["DetectedVersionScraper", "VnuScraper",
                              "LxmlScraper", "MagicTextScraper",
                              "TextEncodingScraper"]),
        ("image/png", None,
         ["PngcheckScraper", "MagicBinaryScraper", "PilScraper",
          "WandScraper"]),
        ("application/warc", None, ["WarcWarctoolsScraper"]),
        ("application/x-internet-archive", None,
         ["MagicBinaryScraper", "ArcWarctoolsScraper"]),
        ("text/xml", "1.0", ["DetectedVersionScraper", "XmllintScraper",
                             "LxmlScraper", "MagicTextScraper",
                             "TextEncodingScraper"]),
        ("application/xhtml+xml", "1.0", ["JHoveHtmlScraper",
                                          "MagicTextScraper",
                                          "TextEncodingScraper"]),
        ("audio/x-wav", None, ["JHoveWavScraper", "MediainfoScraper"]),
        ("application/vnd.oasis.opendocument.text", None,
         ["DetectedVersionScraper", "OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.spreadsheet", None,
         ["DetectedVersionScraper", "OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.presentation", None,
         ["DetectedVersionScraper", "OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.graphics", None,
         ["DetectedVersionScraper", "OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.formula", None,
         ["DetectedVersionScraper", "OfficeScraper", "MagicBinaryScraper"]),
        ("application/msword", None, ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.ms-excel", None, ["OfficeScraper",
                                            "MagicBinaryScraper"]),
        ("application/vnd.ms-powerpoint", None,
         ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", None, ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         None, ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", None, ["OfficeScraper", "MagicBinaryScraper"]),
        ("test/unknown", None, ["ScraperNotFound"])
    ])
def test_iter_scrapers(mimetype, version, scraper_classes):
    """
    Test scraper discovery.

    :mimetype: Predefined mimetype
    :version: Predefined file format version
    :scraper_classes: Expected Scraper classes which are run
    """
    scrapers = iter_scrapers(mimetype, version)
    assert set([x.__name__ for x in scrapers]) == set(scraper_classes)


def test_iter_detectors():
    """Test detector discovery."""
    detectors = iter_detectors()
    assert set([x.__name__ for x in detectors]) == set(["FidoDetector",
                                                        "MagicDetector",
                                                        "PredefinedDetector"])
