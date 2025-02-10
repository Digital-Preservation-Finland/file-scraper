"""
Test for file_scraper.scrapers.

This module tests that:
    - iter_scrapers(mimetype, version) returns the correct scrapers.
    - iter_detectors() returns the correct detectors.
"""

import pytest

from file_scraper.iterator import iter_scrapers, iter_detectors


WELLFORMED_SCRAPERS = [
    "DpxScraper", "FFMpegScraper", "GhostscriptScraper", "JHoveAiffScraper",
    "JHoveEpubScraper", "JHoveGifScraper", "JHoveHtmlScraper",
    "JHoveJpegScraper", "JHoveTiffScraper", "JHovePdfScraper",
    "JHoveWavScraper", "JHoveUtf8Scraper", "LxmlScraper", "OfficeScraper",
    "PngcheckScraper", "PsppScraper", "SchematronScraper",
    "TextEncodingScraper", "VerapdfScraper", "VnuScraper",
    "WarctoolsFullScraper", "GzipWarctoolsScraper", "XmllintScraper"
]


@pytest.mark.parametrize(
    ["mimetype", "version", "scraper_classes"],
    [
        ("image/x-dpx", None, ["DpxScraper"]),
        ("application/x-spss-por", None, ["PsppScraper"]),
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
        ("application/epub+zip", "3", ["JHoveEpubScraper",
                                       "DetectedMimeVersionScraper"]),
        ("application/mxf", None, ["FFMpegScraper"]),
        ("application/pdf", "1.2", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("application/pdf", "1.3", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("application/pdf", "1.4", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("application/pdf", "1.5", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("application/pdf", "1.6", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("application/pdf", "A-1a", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-1b", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-2a", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-2b", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-2u", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-3a", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-3b", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "A-3u", ["MagicBinaryScraper", "JHovePdfScraper",
                                     "VerapdfScraper", "GhostscriptScraper"]),
        ("application/pdf", "1.7", ["MagicBinaryScraper", "JHovePdfScraper",
                                    "GhostscriptScraper"]),
        ("image/tiff", None, ["JHoveTiffScraper", "MagicBinaryScraper",
                              "PilScraper", "WandScraper"]),
        ("image/jpeg", None, ["JHoveJpegScraper", "MagicBinaryScraper",
                              "PilScraper", "WandScraper"]),
        ("image/gif", None, ["JHoveGifScraper", "MagicBinaryScraper",
                             "PilScraper", "WandScraper"]),
        ("text/html", "4.01", ["JHoveHtmlScraper", "LxmlScraper",
                               "MagicTextScraper",
                               "TextEncodingScraper"]),
        ("text/html", "5", ["VnuScraper",
                            "LxmlScraper", "MagicTextScraper",
                            "TextEncodingScraper"]),
        ("image/png", None,
         ["PngcheckScraper", "MagicBinaryScraper", "PilScraper",
          "WandScraper"]),
        ("application/gzip", None, ["GzipWarctoolsScraper"]),
        ("application/warc", None, ["WarctoolsFullScraper"]),
        ("text/xml", "1.0", ["XmllintScraper",
                             "LxmlScraper", "MagicTextScraper",
                             "TextEncodingScraper"]),
        ("application/xhtml+xml", "1.0", ["JHoveHtmlScraper",
                                          "MagicTextScraper",
                                          "TextEncodingScraper"]),
        ("audio/x-wav", None, ["FFMpegScraper", "JHoveWavScraper",
                               "MediainfoScraper"]),
        ("application/vnd.oasis.opendocument.text", None,
         ["DetectedMimeVersionScraper", "OfficeScraper",
          "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.spreadsheet", None,
         ["DetectedMimeVersionScraper", "OfficeScraper",
          "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.presentation", None,
         ["DetectedMimeVersionScraper", "OfficeScraper",
          "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.graphics", None,
         ["DetectedMimeVersionScraper", "OfficeScraper",
          "MagicBinaryScraper"]),
        ("application/vnd.oasis.opendocument.formula", None,
         ["DetectedMimeVersionScraper", "OfficeScraper",
          "MagicBinaryScraper"]),
        ("application/msword", "97-2003", ["OfficeScraper",
                                           "MagicBinaryScraper"]),
        ("application/vnd.ms-excel", "8X", ["OfficeScraper",
                                            "MagicBinaryScraper"]),
        ("application/vnd.ms-powerpoint", "97-2003",
         ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "2007 onwards", ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "2007 onwards", ["OfficeScraper", "MagicBinaryScraper"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "2007 onwards", ["OfficeScraper",
                                          "MagicBinaryScraper"]),
        ("audio/x-aiff", "1.3", ["FFMpegScraper", "JHoveAiffScraper",
                                 "MagicBinaryScraper", "MediainfoScraper"]),
        ("audio/x-ms-wma", "9", ["FFMpegScraper", "MediainfoScraper"]),
        ("video/x-ms-wmv", "9", ["FFMpegScraper", "MediainfoScraper"]),
        ("test/unknown", None, ["ScraperNotFound"])
    ])
def test_iter_scrapers(mimetype, version, scraper_classes):
    """
    Test scraper discovery.

    :mimetype: Detected mimetype
    :version: Detected file format version
    :scraper_classes: Expected Scraper classes which are run
    """
    scrapers = iter_scrapers(mimetype, version)
    assert {x.__name__ for x in scrapers} == set(scraper_classes)

    scraper_classes = [
        "TextEncodingMetaScraper" if x == "TextEncodingScraper" else x
        for x in scraper_classes
    ]
    scraper_classes = [
        "WarctoolsScraper" if x == "WarctoolsFullScraper" else x
        for x in scraper_classes
    ]
    if mimetype == "application/mxf":
        scraper_classes = ["FFMpegMetaScraper"]
    if mimetype in ["application/x-spss-por", "text/html", "text/xml"] or \
            mimetype == "application/pdf" and version in \
            ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u", "A-3a", "A-3b", "A-3u"]:
        scraper_classes.append("DetectedMimeVersionMetadataScraper")

    scrapers = iter_scrapers(mimetype, version, False)
    scraper_set = set(scraper_classes).difference(set(WELLFORMED_SCRAPERS))
    if mimetype in ["application/gzip", "image/x-dpx"]:
        scraper_set = {"ScraperNotFound"}
    assert {x.__name__ for x in scrapers} == scraper_set


def test_iter_detectors():
    """Test detector discovery."""
    detectors = iter_detectors()
    assert {x.__name__ for x in detectors} == {"EpubDetector",
                                               "FidoDetector",
                                               "MagicDetector",
                                               "PredefinedDetector",
                                               "SegYDetector",
                                               "SiardDetector",
                                               "ODFDetector"}
