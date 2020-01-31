"""
Tests for Fido and Magic detectors.

This module tests that:
    - FidoDetector and MagicDetector detect MIME types correctly.
    - FidoDetector returns an empty dict from get_important() with
      certain mimetypes and MagicDetector returns certain mimetypes.
    - VerapdfDetector detects PDF/A MIME types and versions but no others.
    - VerapdfDetector results are important for PDF/A files.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.detectors import FidoDetector, MagicDetector, VerapdfDetector
from tests.common import get_files, partial_message_included

CHANGE_FIDO = {
    "tests/data/text_plain/valid__ascii.txt": None,
    "tests/data/text_plain/valid__iso8859.txt": None,
    "tests/data/text_plain/valid__utf8_bom.txt": None,
    "tests/data/text_plain/valid__utf8_without_bom.txt": None,
    "tests/data/text_plain/valid__utf16le_bom.txt": None,
    "tests/data/text_plain/valid__utf16le_without_bom.txt": None,
    "tests/data/text_plain/valid__utf16be_bom.txt": None,
    "tests/data/text_plain/valid__utf16be_without_bom.txt": None,
    "tests/data/text_plain/valid__utf32le_bom.txt": None,
    "tests/data/text_plain/valid__utf32le_without_bom.txt": None,
    "tests/data/text_plain/valid__utf32be_bom.txt": None,
    "tests/data/text_plain/valid__utf32be_without_bom.txt": None,
    "tests/data/video_mp4/valid__h264_aac.mp4": None,
    "tests/data/application_msword/valid_11.0.doc": None,
    "tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml"
    ".sheet/valid_15.0.xlsx": None,
    "tests/data/application_vnd.openxmlformats-officedocument.presentationml"
    ".presentation/valid_15.0.pptx": None,
    "tests/data/application_vnd.oasis.opendocument.formula/valid_1.0.odf":
        "application/zip",
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz":
        "application/gzip",
    "tests/data/application_warc/valid_1.0_.warc.gz": "application/gzip",
    "tests/data/application_x-internet-archive/valid_1.0.arc": "text/html",
    "tests/data/application_mxf/valid__jpeg2000.mxf": None,
    "tests/data/application_mxf/valid__jpeg2000_grayscale.mxf": None,
    "tests/data/text_csv/valid__ascii.csv": None,
    "tests/data/text_csv/valid__ascii_header.csv": None,
    "tests/data/text_csv/valid__header_only.csv": None,
    "tests/data/text_csv/valid__iso8859-15.csv": None,
    "tests/data/text_csv/valid__utf8.csv": None,
    "tests/data/text_xml/valid_1.0_mets_noheader.xml": None,
}

CHANGE_MAGIC = {
    "tests/data/text_plain/valid__utf16le_without_bom.txt":
        "application/octet-stream",
    "tests/data/text_plain/valid__utf16be_without_bom.txt":
        "application/octet-stream",
    "tests/data/text_plain/valid__utf32le_bom.txt":
        "application/octet-stream",
    "tests/data/text_plain/valid__utf32le_without_bom.txt":
        "application/octet-stream",
    "tests/data/text_plain/valid__utf32be_bom.txt":
        "application/octet-stream",
    "tests/data/text_plain/valid__utf32be_without_bom.txt":
        "application/octet-stream",
    "tests/data/video_MP2T/valid_.ts": "application/octet-stream",
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz":
        "application/x-gzip",
    "tests/data/application_xhtml+xml/valid_1.0.xhtml": "text/xml",
    "tests/data/application_warc/valid_1.0_.warc.gz": "application/x-gzip",
    "tests/data/application_x-spss-por/valid__spss24-dot.por": "text/plain",
    "tests/data/application_x-spss-por/valid__spss24-dates.por": "text/plain",
    "tests/data/text_csv/valid__ascii.csv": "text/plain",
    "tests/data/text_csv/valid__ascii_header.csv": "text/plain",
    "tests/data/text_csv/valid__header_only.csv": "text/plain",
    "tests/data/text_csv/valid__iso8859-15.csv": "text/plain",
    "tests/data/text_csv/valid__utf8.csv": "text/plain",
    "tests/data/text_xml/valid_1.0_mets_noheader.xml": "text/plain",
}


@pytest.mark.parametrize(
    ["filepath", "mimetype", "version"],
    [
        ("tests/data/application_pdf/valid_1.4.pdf", None, None),
        ("tests/data/application_pdf/valid_A-1a.pdf", "application/pdf",
         "A-1a"),
        ("tests/data/application_pdf/valid_A-2b.pdf", "application/pdf",
         "A-2b"),
        ("tests/data/application_pdf/valid_A-3b.pdf", "application/pdf",
         "A-3b"),
        ("tests/data/image_png/valid_1.2.png", None, None)
    ]
)
def test_pdf_detector(filepath, mimetype, version):
    """
    Test that VerapdfDetector works.

    The detector should detect the file types of PDF/A files, but return None
    for other files, including PDF files that are not PDF/A.
    """
    detector = VerapdfDetector(filepath)
    detector.detect()
    assert detector.mimetype == mimetype
    assert detector.version == version


@pytest.mark.parametrize(
    ["detector_class", "change_dict"],
    [
        (FidoDetector, CHANGE_FIDO),
        (MagicDetector, CHANGE_MAGIC)
    ]
)
def test_detectors(detector_class, change_dict):
    """Test Fido and Magic detectors.

    The test compares detected mimetype to expected mimetype.
    Runs all well-formed files in the test data set.

    :detector_class: Detector class to test
    :change_dict: Known exceptions to expected mimetypes
    """
    for filename, mimetype in get_files(well_formed=True):
        detector = detector_class(filename)
        detector.detect()
        if filename in change_dict:
            assert detector.mimetype == change_dict[filename]
        else:
            assert detector.mimetype == mimetype, ("File {} identified as {} "
                                                   "when {} was expected."
                                                   "".format(filename,
                                                             detector.mimetype,
                                                             mimetype)
                                                   )


@pytest.mark.parametrize(
    ["filepath", "important"],
    [
        ("tests/data/application_pdf/valid_A-1a.pdf", True),
        ("tests/data/application_pdf/valid_1.4.pdf", False),
        ("tests/data/image_gif/valid_1987a.gif", False)
    ]
)
def test_important_pdf(filepath, important):
    """
    Test that VerapdfDetector results are important for PDF/A files only.
    """
    detector = VerapdfDetector(filepath)
    detector.detect()
    if important:
        assert "mimetype" in detector.get_important()
        assert "version" in detector.get_important()
    else:
        assert detector.get_important() == {}


@pytest.mark.parametrize(
    ["detector_class", "mimetype"],
    [
        (FidoDetector, "text/html"),
        (FidoDetector, "application/zip"),
        (MagicDetector, "application/vnd.oasis.opendocument.formula"),
        (MagicDetector, "application/x-internet-archive")
    ]
)
def test_important_other(detector_class, mimetype):
    """Test important with cruical mimetypes using other detectors."""
    detector = detector_class("testfilename")
    detector.mimetype = mimetype
    if detector_class == FidoDetector:
        assert detector.get_important() == {}
    else:
        assert detector.get_important() == {"mimetype": mimetype}


@pytest.mark.parametrize(
    ["filename", "charset"],
    [("tests/data/text_plain/valid__utf8_without_bom.txt", "UTF-8"),
     ("tests/data/text_plain/valid__utf16le_without_bom.txt", "UTF-8"),
     ("tests/data/text_plain/valid__utf32be_without_bom.txt", "UTF-8"),
     ("tests/data/text_plain/valid__iso8859.txt", "UTF-8"),
     ("tests/data/video_dv/valid.dv", None)]
)
def test_magic_charset(filename, charset):
    """Test charset encoding detection"""
    detector = MagicCharset(
        "tests/data/text_plain/valid__utf8_without_bom.txt")
    detector.detect()
    if charset:
        detector.charset = charset
        assert not self.errors
        assert partial_message_included(
            "Character encoding detected as", self.errors)
    else:
        assert partial_message_included(
            "Unable to detect character encoding", self.errors)
