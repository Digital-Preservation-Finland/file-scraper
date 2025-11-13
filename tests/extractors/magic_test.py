#!/usr/bin/env python
"""
Tests for magick extractor.

This module tests that:
    - For valid files, MagicExtractor is able to correctly determine the
      following features of their corresponding file types:
        - MIME type
        - version
        - streams
        - well-formedness
    - In addition to this, the extractor messages contain "successfully" and no
      errors are recorded.

    - For office files (odt, doc, docx, odp, ppt, pptx, ods, xls, xlsx, odg and
      odf) with missing bytes:
        - MIME type is application/octet-stream
        - version is None
        - streams are scraped correctly
        - extractor errors contain "do not match"
        - file is not well-formed
    - For XHTML files with missing closing tag:
        - MIME type, version and streams are scraped correctly
        - there are no extractor errors
        - extractor messages contain "successfully"
        - file is well-formed
    - For HTML files without doctype the same things are checked as with XHTML
      files but version must be None
    - For pdf and arc files the same things are checked as with XHTML files

    - For image files (png, jpeg, jp2, tif) with errors:
        - MIME type is application/octet-stream
        - version and streams are scraped correctly
        - extractor errors contain "do not match"
        - file is not well-formed

    - Character case of magic's result does not affect (:unav) version
      result for JPEG/EXIF images.

    - For text files actually containing binary data:
        - MIME type and version is "(:unav)"
        - extractor errors contains "do not match"
        - file is not well-formed

    - The following MIME type and version pairs are supported when full
      scraping is performed:
        - application/vnd.oasis.opendocument.text, 1.2
        - application/vnd.oasis.opendocument.text, 1.3
        - application/msword, 97-2003
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document, 2007 onwards
        - application/vnd.oasis.opendocument.presentation, 1.2
        - application/vnd.oasis.opendocument.presentation, 1.3
        - application/vnd.ms-powerpoint, 97-2003
        - application/vnd.openxmlformats-officedocument.presentationml.presentation, 2007 onwards
        - application/vnd.oasis.opendocument.spreadsheet, 1.2
        - application/vnd.oasis.opendocument.spreadsheet, 1.3
        - application/vnd.ms-excel, 8X
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, 2007 onwards
        - application/vnd.oasis.opendocument.graphics, 1.2
        - application/vnd.oasis.opendocument.graphics, 1.3
        - application/vnd.oasis.opendocument.formula, 1.2
        - application/vnd.oasis.opendocument.formula, 1.3
        - image/png, 1.2
        - image/jpeg, 1.01
        - image/jp2, ""
        - image/tiff, 6.0
        - text/plain, ""
        - text/xml, 1.0
        - application/xhtml+xml, 1.0
        - text/html, 4.01
        - application/pdf, 1.4
        - audio/x-aiff, 1.3
    - Any of these MIME types with version None is also supported,
      except text/html
    - Valid MIME type with made up version is supported, except for text files
    - Made up MIME type with any version is not supported
    - When full scraping is not done, these combinations are supported only
      for text files.
"""  # noqa  (it's neater to have long lines than to break mimetypes)
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.magic_extractor.magic_model import (HtmlFileMagicMeta,
                                                      JpegFileMagicMeta)
from file_scraper.magic_extractor.magic_extractor import (MagicTextExtractor,
                                                          MagicBinaryExtractor)
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "mimetype", "charset", "extractor_class"],
    [
        ("valid_1.2.odt",
         "application/vnd.oasis.opendocument.text", None, MagicBinaryExtractor),
        ("valid_1.3.odt",
         "application/vnd.oasis.opendocument.text", None, MagicBinaryExtractor),
        ("valid_97-2003.doc",
         "application/msword", None, MagicBinaryExtractor),
        ("valid_2007 onwards.docx",
         "application/vnd.openxmlformats-officedocument."
         "wordprocessingml.document", None, MagicBinaryExtractor),
        ("valid_1.2.odp",
         "application/vnd.oasis.opendocument.presentation", None,
         MagicBinaryExtractor),
        ("valid_1.3.odp",
         "application/vnd.oasis.opendocument.presentation", None,
         MagicBinaryExtractor),
        ("valid_97-2003.ppt",
         "application/vnd.ms-powerpoint", None, MagicBinaryExtractor),
        ("valid_2007 onwards.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation", None,
         MagicBinaryExtractor),
        ("valid_1.2.ods",
         "application/vnd.oasis.opendocument.spreadsheet", None,
         MagicBinaryExtractor),
        ("valid_1.3.ods",
         "application/vnd.oasis.opendocument.spreadsheet", None,
         MagicBinaryExtractor),
        ("valid_8X.xls",
         "application/vnd.ms-excel", None, MagicBinaryExtractor),
        ("valid_2007 onwards.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         None, MagicBinaryExtractor),
        ("valid_1.2.odg",
         "application/vnd.oasis.opendocument.graphics", None,
         MagicBinaryExtractor),
        ("valid_1.3.odg",
         "application/vnd.oasis.opendocument.graphics", None,
         MagicBinaryExtractor),
        ("valid_1.2.odf",
         "application/vnd.oasis.opendocument.formula", None,
         MagicBinaryExtractor),
        ("valid_1.3.odf",
         "application/vnd.oasis.opendocument.formula", None,
         MagicBinaryExtractor),
        ("valid_1.2.png", "image/png", None, MagicBinaryExtractor),
        ("valid_1.01.jpg", "image/jpeg", None, MagicBinaryExtractor),
        ("valid__jpylyzer_reference.jp2",
         "image/jp2", None, MagicBinaryExtractor),
        ("valid_6.0.tif", "image/tiff", None, MagicBinaryExtractor),
        ("valid__iso8859.txt", "text/plain", "ISO-8859-15",
         MagicTextExtractor),
        ("valid__utf8_without_bom.txt", "text/plain", "UTF-8",
         MagicTextExtractor),
        ("valid_1.0_well_formed.xml", "text/xml", "UTF-8",
         MagicTextExtractor),
        ("valid_1.0.xhtml", "application/xhtml+xml", "UTF-8",
         MagicTextExtractor),
        ("valid_4.01.html", "text/html", "UTF-8", MagicTextExtractor),
        ("valid_5.html", "text/html", "UTF-8", MagicTextExtractor),
        ("valid_1.4.pdf", "application/pdf", None, MagicBinaryExtractor),
        ("valid_1.3.aiff", "audio/x-aiff", None, MagicBinaryExtractor),
        ("valid__aiff-c.aiff", "audio/x-aiff", None, MagicBinaryExtractor),
    ])
def test_extractor_valid(filename, mimetype, charset, extractor_class,
                       evaluate_extractor):
    """Test extractor."""
    result_dict = {
        "purpose": "Test valid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, False,
                            {"charset": charset})

    office_unav_version_mimes = [
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/vnd.oasis.opendocument.graphics",
        "application/vnd.oasis.opendocument.formula",
    ]

    extractor = extractor_class(filename=correct.filename, mimetype=mimetype,
                            params={"charset": charset})
    extractor.extract()
    if correct.streams[0]["mimetype"] == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"
    if ((correct.streams[0]["mimetype"] in office_unav_version_mimes) or
            HtmlFileMagicMeta.is_supported(correct.streams[0]["mimetype"])):
        correct.streams[0]["version"] = UNAV

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid_1.2_missing_data.odt",
         "application/vnd.oasis.opendocument.text"),
        ("invalid_97-2003_missing_data.doc", "application/msword"),
        ("invalid_2007 onwards_missing_data.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("invalid_1.2_missing_data.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("invalid_97-2003_missing_data.ppt", "application/vnd.ms-powerpoint"),
        ("invalid_2007 onwards_missing_data.pptx",
         "application/vnd.openxmlformats-officedocument.presentationml."
         "presentation"),
        ("invalid_1.2_missing_data.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("invalid_8X_missing_data.xls", "application/vnd.ms-excel"),
        ("invalid_2007 onwards_missing_data.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("invalid_1.2_missing_data.odg",
         "application/vnd.oasis.opendocument.graphics"),
        ("invalid_1.2_missing_data.odf",
         "application/vnd.oasis.opendocument.formula"),
        ("invalid__empty.doc", "application/msword"),
    ])
def test_invalid_office(filename, mimetype):
    """Test OfficeFileMagic extractor with invalid files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": "MIME type %s with version %s is not "
                       "supported." % (UNAV, UNAV)}

    correct = parse_results(filename, mimetype,
                            result_dict, False)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    extractor = MagicBinaryExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.extract()

    assert extractor.well_formed is False
    assert partial_message_included(correct.stdout_part, extractor.messages())
    assert partial_message_included(correct.stderr_part, extractor.errors())


@pytest.mark.parametrize(
    ["filename", "mimetype", "extractor_class"],
    [
        ("invalid_1.0_no_closing_tag.xml", "text/xml", MagicTextExtractor),
        ("invalid_1.0_no_doctype.xhtml", "application/xhtml+xml",
         MagicTextExtractor),
        ("invalid_4.01_nodoctype.html", "text/html", MagicTextExtractor),
        ("invalid_5_nodoctype.html", "text/html", MagicTextExtractor),
        ("invalid_1.4_removed_xref.pdf", "application/pdf",
         MagicBinaryExtractor),
    ])
def test_invalid_markup_pdf(filename, mimetype, extractor_class,
                            evaluate_extractor):
    """Test extractors for invalid XML, XHTML, HTML, and pdf files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, False)
    correct.update_mimetype(mimetype)
    if correct.streams[0]["stream_type"] == UNAV:
        correct.streams[0]["stream_type"] = "text"
    if mimetype != "text/html":
        correct.update_version(filename.split("_")[1])
    extractor = extractor_class(filename=correct.filename, mimetype=mimetype)
    extractor.extract()

    correct.well_formed = None

    if correct.streams[0]["mimetype"] == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid_1.2_wrong_header.png", "image/png"),
        ("invalid_1.01_no_start_marker.jpg", "image/jpeg"),
        ("invalid__data_missing.jp2", "image/jp2"),
        ("invalid_6.0_wrong_byte_order.tif", "image/tiff"),
    ])
def test_invalid_images(filename, mimetype):
    """Test scrapes for invalid image files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": "MIME type %s with version %s is not "
                       "supported." % (UNAV, UNAV)}
    correct = parse_results(filename, mimetype, result_dict, False)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    extractor = MagicBinaryExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.extract()

    assert extractor.well_formed is False
    assert partial_message_included(correct.stdout_part, extractor.messages())
    assert partial_message_included(correct.stderr_part, extractor.errors())


def test_jpeg_exif_character_case():
    """
    Test that character case in magic's result does not affect (:unav)
    version result for JPEG/EXIF images.
    """
    jpeg_meta = JpegFileMagicMeta(
        {"magic_none": "JPEG image data, EXIF standard"}, "image/jpeg")
    assert jpeg_meta.version() == UNAV
    jpeg_meta = JpegFileMagicMeta(
        {"magic_none": "JPEG image data, Exif standard"}, "image/jpeg")
    assert jpeg_meta.version() == UNAV


def test_msoffice_word_detected():
    """
    Regression test for TPASPKT-1382. Ensure that MSOffice Word document's type
    is detected correctly. Older file versions such as 5.39 shipped with RHEL9
    only report the generic "Microsoft OOXML" instead of "Microsoft Word 2007+"
    """
    extractor = MagicBinaryExtractor(
        filename=Path(
            "tests/data/application_vnd.openxmlformats-officedocument"
            ".wordprocessingml.document/valid_2007 onwards_word-dir-third.docx"
        ),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    extractor.extract()

    assert extractor.streams[0].mimetype() \
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.mark.parametrize(
    ["mime", "ver", "extractor_class"],
    [
        ("application/vnd.oasis.opendocument.text", "1.2",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.text", "1.3",
         MagicBinaryExtractor),
        ("application/msword", "97-2003", MagicBinaryExtractor),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml"
         ".document", "2007 onwards", MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.presentation", "1.2",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.presentation", "1.3",
         MagicBinaryExtractor),
        ("application/vnd.ms-powerpoint", "97-2003", MagicBinaryExtractor),
        ("application/vnd.openxmlformats-officedocument.presentationml"
         ".presentation", "2007 onwards", MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.2",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.3",
         MagicBinaryExtractor),
        ("application/vnd.ms-excel", "8X", MagicBinaryExtractor),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml"
         ".sheet", "2007 onwards", MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.graphics", "1.2",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.graphics", "1.3",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.formula", "1.2",
         MagicBinaryExtractor),
        ("application/vnd.oasis.opendocument.formula", "1.3",
         MagicBinaryExtractor),
        ("image/png", "1.2", MagicBinaryExtractor),
        ("image/jpeg", "1.01", MagicBinaryExtractor),
        ("image/jp2", "", MagicBinaryExtractor),
        ("image/tiff", "6.0", MagicBinaryExtractor),
        ("text/plain", "", MagicTextExtractor),
        ("text/xml", "1.0", MagicTextExtractor),
        ("application/xhtml+xml", "1.0", MagicTextExtractor),
        ("application/pdf", "1.4", MagicBinaryExtractor),
        ("audio/x-aiff", "1.3", MagicBinaryExtractor),
    ]
)
# pylint: disable=invalid-name
def test_is_supported_allow_any_version(mime, ver, extractor_class):
    """
    Test is_supported method.
    Any version is supported.

    :mime: MIME type
    :ver: File format version
    :extractor_class: Extractor class to test
    """
    assert extractor_class.is_supported(mime, ver, True)
    assert extractor_class.is_supported(mime, None, True)
    assert extractor_class.is_supported(mime, ver, False)
    assert extractor_class.is_supported(mime, "foo", True)
    assert not extractor_class.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("text/html", "4.01"),
    ]
)
# pylint: disable=invalid-name
def test_is_supported_disallow_versions(mime, ver):
    """
    Test is_supported method.
    Only defined versions are supported.

    :mime: MIME type
    :ver: File format version
    """
    assert MagicTextExtractor.is_supported(mime, ver, True)
    assert MagicTextExtractor.is_supported(mime, None, True)
    assert MagicTextExtractor.is_supported(mime, ver, False)
    assert not MagicTextExtractor.is_supported(mime, "foo", True)
    assert not MagicTextExtractor.is_supported("foo", ver, True)


def test_tools():
    """Test that magic extractor returns software used"""
    tools = MagicTextExtractor(filename=Path(""), mimetype="").tools()
    assert tools["libmagic"]["version"][0].isdigit()
