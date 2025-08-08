"""
Test for file_scraper.extractor.

This module tests that:
    - iter_extractors(mimetype, version) returns the correct extractors.
    - iter_detectors() returns the correct detectors.
"""

import pytest

from file_scraper.iterator import iter_extractors, iter_detectors


WELLFORMED_EXTRACTORS = [
    "DpxExtractor", "FFMpegExtractor", "GhostscriptExtractor", "JHoveAiffExtractor",
    "JHoveEpubExtractor", "JHoveGifExtractor", "JHoveHtmlExtractor",
    "JHoveJpegExtractor", "JHoveTiffExtractor", "JHovePdfExtractor",
    "JHoveWavExtractor", "JHoveUtf8Extractor", "LxmlExtractor", "OfficeExtractor",
    "PngcheckExtractor", "PsppExtractor", "SchematronExtractor",
    "TextEncodingExtractor", "VerapdfExtractor", "VnuExtractor",
    "WarctoolsFullExtractor", "GzipWarctoolsExtractor", "XmllintExtractor"
]


@pytest.mark.parametrize(
    ["mimetype", "version", "extractor_classes"],
    [
        ("image/x-dpx", None, ["DpxExtractor"]),
        ("application/x-spss-por", None, ["PsppExtractor"]),
        ("text/csv", None, ["CsvExtractor", "MagicTextExtractor",
                            "TextEncodingExtractor"]),
        ("text/plain", None, ["MagicTextExtractor", "TextfileExtractor",
                              "TextEncodingExtractor"]),
        ("video/mpeg", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("video/mp4", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("video/mp2t", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("video/x-matroska", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("video/dv", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("video/quicktime", None, ["MediainfoExtractor", "FFMpegExtractor"]),
        ("application/epub+zip", "3", ["JHoveEpubExtractor",
                                       "DetectedMimeVersionExtractor"]),
        ("application/mxf", None, ["FFMpegExtractor"]),
        ("application/pdf", "1.2", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("application/pdf", "1.3", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("application/pdf", "1.4", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("application/pdf", "1.5", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("application/pdf", "1.6", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("application/pdf", "A-1a", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-1b", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-2a", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-2b", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-2u", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-3a", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-3b", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "A-3u", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                     "VerapdfExtractor", "GhostscriptExtractor"]),
        ("application/pdf", "1.7", ["MagicBinaryExtractor", "JHovePdfExtractor",
                                    "GhostscriptExtractor"]),
        ("image/tiff", None, ["JHoveTiffExtractor", "MagicBinaryExtractor",
                              "PilExtractor", "WandExtractor"]),
        ("image/jpeg", None, ["JHoveJpegExtractor", "MagicBinaryExtractor",
                              "MediainfoExtractor", "PilExtractor",
                              "WandExtractor"]),
        ("image/gif", None, ["JHoveGifExtractor", "MagicBinaryExtractor",
                             "PilExtractor", "WandExtractor"]),
        ("text/html", "4.01", ["JHoveHtmlExtractor", "LxmlExtractor",
                               "MagicTextExtractor",
                               "TextEncodingExtractor"]),
        ("text/html", "5", ["VnuExtractor",
                            "LxmlExtractor", "MagicTextExtractor",
                            "TextEncodingExtractor"]),
        ("image/png", None, ["PngcheckExtractor", "MagicBinaryExtractor",
                             "PilExtractor", "MediainfoExtractor", "WandExtractor"]),
        ("application/gzip", None, ["GzipWarctoolsExtractor"]),
        ("application/warc", None, ["WarctoolsFullExtractor"]),
        ("text/xml", "1.0", ["XmllintExtractor",
                             "LxmlExtractor", "MagicTextExtractor",
                             "TextEncodingExtractor"]),
        ("application/xhtml+xml", "1.0", ["JHoveHtmlExtractor",
                                          "MagicTextExtractor",
                                          "TextEncodingExtractor"]),
        ("audio/x-wav", None, ["FFMpegExtractor", "JHoveWavExtractor",
                               "MediainfoExtractor"]),
        ("application/vnd.oasis.opendocument.text", None,
         ["DetectedMimeVersionExtractor", "OfficeExtractor",
          "MagicBinaryExtractor"]),
        ("application/vnd.oasis.opendocument.spreadsheet", None,
         ["DetectedMimeVersionExtractor", "OfficeExtractor",
          "MagicBinaryExtractor"]),
        ("application/vnd.oasis.opendocument.presentation", None,
         ["DetectedMimeVersionExtractor", "OfficeExtractor",
          "MagicBinaryExtractor"]),
        ("application/vnd.oasis.opendocument.graphics", None,
         ["DetectedMimeVersionExtractor", "OfficeExtractor",
          "MagicBinaryExtractor"]),
        ("application/vnd.oasis.opendocument.formula", None,
         ["DetectedMimeVersionExtractor", "OfficeExtractor",
          "MagicBinaryExtractor"]),
        ("application/msword", "97-2003", ["OfficeExtractor",
                                           "MagicBinaryExtractor"]),
        ("application/vnd.ms-excel", "8X", ["OfficeExtractor",
                                            "MagicBinaryExtractor"]),
        ("application/vnd.ms-powerpoint", "97-2003",
         ["OfficeExtractor", "MagicBinaryExtractor"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "2007 onwards", ["OfficeExtractor", "MagicBinaryExtractor"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "2007 onwards", ["OfficeExtractor", "MagicBinaryExtractor"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "2007 onwards", ["OfficeExtractor",
                                          "MagicBinaryExtractor"]),
        ("audio/x-aiff", "1.3", ["FFMpegExtractor", "JHoveAiffExtractor",
                                 "MagicBinaryExtractor", "MediainfoExtractor"]),
        ("audio/x-ms-wma", "9", ["FFMpegExtractor", "MediainfoExtractor"]),
        ("video/x-ms-wmv", "9", ["FFMpegExtractor", "MediainfoExtractor"]),
        ("test/unknown", None, ["ExtractorNotFound"])
    ])
def test_iter_extractors(mimetype, version, extractor_classes):
    """
    Test extractor discovery.

    :mimetype: Detected mimetype
    :version: Detected file format version
    :extractor_classes: Expected Extractor classes which are run
    """
    extractors = iter_extractors(mimetype, version)
    assert {x.__name__ for x in extractors} == set(extractor_classes)

    extractor_classes = [
        "TextEncodingMetaExtractor" if x == "TextEncodingExtractor" else x
        for x in extractor_classes
    ]
    extractor_classes = [
        "WarctoolsExtractor" if x == "WarctoolsFullExtractor" else x
        for x in extractor_classes
    ]
    if mimetype == "application/mxf":
        extractor_classes = ["FFMpegMetaExtractor"]
    if mimetype in ["application/x-spss-por", "text/html", "text/xml"] or \
            mimetype == "application/pdf" and version in \
            ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u", "A-3a", "A-3b", "A-3u"]:
        extractor_classes.append("DetectedMimeVersionMetadataExtractor")

    extractors = iter_extractors(mimetype, version, False)
    extractor_set = set(extractor_classes).difference(set(WELLFORMED_EXTRACTORS))
    if mimetype in ["application/gzip", "image/x-dpx"]:
        extractor_set = {"ExtractorNotFound"}
    assert {x.__name__ for x in extractors} == extractor_set


def test_iter_detectors():
    """Test detector discovery."""
    detectors = iter_detectors()
    assert {x.__name__ for x in detectors} == {"EpubDetector",
                                               "FidoDetector",
                                               "MagicDetector",
                                               "PredefinedDetector",
                                               "SegYDetector",
                                               "AtlasTiDetector",
                                               "SiardDetector",
                                               "ODFDetector"}
