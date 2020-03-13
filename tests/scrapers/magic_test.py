#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for File (libmagick) scraper.

This module tests that:
    - For valid files, MagicScraper is able to correctly determine the
      following features of their corresponding file types:
        - MIME type
        - version
        - streams
        - well-formedness
    - In addition to this, the scraper messages contain "successfully" and no
      errors are recorded.

    - For office files (odt, doc, docx, odp, ppt, pptx, ods, xls, xlsx, odg and
      odf) with missing bytes:
        - MIME type is application/octet-stream
        - version is None
        - streams are scraped correctly
        - scraper errors contain "do not match"
        - file is not well-formed
    - For XHTML files with missing closing tag:
        - MIME type, version and streams are scraped correctly
        - there are no scraper errors
        - scraper messages contain "successfully"
        - file is well-formed
    - For HTML files without doctype the same things are checked as with XHTML
      files but version must be None
    - For pdf and arc files the same things are checked as with XHTML files

    - For image files (png, jpeg, jp2, tif) with errors:
        - MIME type is application/octet-stream
        - version and streams are scraped correctly
        - scraper errors contain "do not match"
        - file is not well-formed

    - For text files actually containing binary data:
        - MIME type and version is "(:unav)"
        - scraper errors contains "do not match"
        - file is not well-formed

    - The following MIME type and version pairs are supported when full
      scraping is performed:
        - application/vnd.oasis.opendocument.text, 1.1
        - application/msword, 11.0
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document, 15.0
        - application/vnd.oasis.opendocument.presentation, 1.1
        - application/vnd.ms-powerpoint, 11.0
        - application/vnd.openxmlformats-officedocument.presentationml.presentation, 15.0
        - application/vnd.oasis.opendocument.spreadsheet, 1.1
        - application/vnd.ms-excel, 8.0
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,
          15.0
        - application/vnd.oasis.opendocument.graphics, 1.1
        - application/vnd.oasis.opendocument.formula, 1.0
        - image/png, 1.2
        - image/jpeg, 1.01
        - image/jp2, ""
        - image/tiff, 6.0
        - text/plain, ""
        - text/xml, 1.0
        - application/xhtml+xml, 1.0
        - text/html, 4.01
        - application/pdf, 1.4
        - application/x-internet-archive, 1.0
    - Any of these MIME types with version None is also supported,
      except text/html
    - Valid MIME type with made up version is supported, except for text files
    - Made up MIME type with any version is not supported
    - When full scraping is not done, these combinations are supported only
      for text files.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.magic_scraper.magic_model import (HtmlFileMagicMeta,
                                                    OfficeFileMagicMeta)
from file_scraper.magic_scraper.magic_scraper import (MagicTextScraper,
                                                      MagicBinaryScraper)
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "mimetype", "charset", "scraper_class"],
    [
        ("valid_1.1.odt",
         "application/vnd.oasis.opendocument.text", None, MagicBinaryScraper),
        ("valid_11.0.doc",
         "application/msword", None, MagicBinaryScraper),
        ("valid_15.0.docx",
         "application/vnd.openxmlformats-officedocument."
         "wordprocessingml.document", None, MagicBinaryScraper),
        ("valid_1.1.odp",
         "application/vnd.oasis.opendocument.presentation", None,
         MagicBinaryScraper),
        ("valid_11.0.ppt",
         "application/vnd.ms-powerpoint", None, MagicBinaryScraper),
        ("valid_15.0.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation", None,
         MagicBinaryScraper),
        ("valid_1.1.ods",
         "application/vnd.oasis.opendocument.spreadsheet", None,
         MagicBinaryScraper),
        ("valid_11.0.xls",
         "application/vnd.ms-excel", None, MagicBinaryScraper),
        ("valid_15.0.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         None, MagicBinaryScraper),
        ("valid_1.1.odg",
         "application/vnd.oasis.opendocument.graphics", None,
         MagicBinaryScraper),
        ("valid_1.0.odf",
         "application/vnd.oasis.opendocument.formula", None,
         MagicBinaryScraper),
        ("valid_1.2.png", "image/png", None, MagicBinaryScraper),
        ("valid_1.01.jpg", "image/jpeg", None, MagicBinaryScraper),
        ("valid.jp2", "image/jp2", None, MagicBinaryScraper),
        ("valid_6.0.tif", "image/tiff", None, MagicBinaryScraper),
        ("valid__iso8859.txt", "text/plain", "ISO-8859-15",
         MagicTextScraper),
        ("valid__utf8_without_bom.txt", "text/plain", "UTF-8",
         MagicTextScraper),
        ("valid_1.0_well_formed.xml", "text/xml", "UTF-8",
         MagicTextScraper),
        ("valid_1.0.xhtml", "application/xhtml+xml", "UTF-8",
         MagicTextScraper),
        ("valid_4.01.html", "text/html", "UTF-8", MagicTextScraper),
        ("valid_5.0.html", "text/html", "UTF-8", MagicTextScraper),
        ("valid_1.4.pdf", "application/pdf", None, MagicBinaryScraper),
        ("valid_1.0.arc", "application/x-internet-archive",
         None, MagicBinaryScraper),
    ])
def test_scraper_valid(filename, mimetype, charset, scraper_class,
                       evaluate_scraper):
    """Test scraper."""
    result_dict = {
        "purpose": "Test valid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, True,
                            {"charset": charset})
    scraper = scraper_class(filename=correct.filename, mimetype=mimetype,
                            params={"charset": charset})
    scraper.scrape_file()
    if correct.streams[0]["mimetype"] == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"
    if (OfficeFileMagicMeta.is_supported(correct.streams[0]["mimetype"]) or
            HtmlFileMagicMeta.is_supported(correct.streams[0]["mimetype"])):
        correct.streams[0]["version"] = "(:unav)"

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid_1.1_missing_data.odt",
         "application/vnd.oasis.opendocument.text"),
        ("invalid_11.0_missing_data.doc", "application/msword"),
        ("invalid_15.0_missing_data.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("invalid_1.1_missing_data.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("invalid_11.0_missing_data.ppt", "application/vnd.ms-powerpoint"),
        ("invalid_15.0_missing_data.pptx", "application/vnd.openxml"
                                           "formats-officedocument."
                                           "presentationml.presentation"),
        ("invalid_1.1_missing_data.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("invalid_11.0_missing_data.xls", "application/vnd.ms-excel"),
        ("invalid_15.0_missing_data.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("invalid_1.1_missing_data.odg",
         "application/vnd.oasis.opendocument.graphics"),
        ("invalid_1.0_missing_data.odf",
         "application/vnd.oasis.opendocument.formula"),
        ("invalid__empty.doc", "application/msword"),
    ])
def test_invalid_office(filename, mimetype):
    """Test OfficeFileMagic scraper with invalid files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": "MIME type (:unav) with version (:unav) "
                       "is not supported."}

    correct = parse_results(filename, mimetype,
                            result_dict, True)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    scraper = MagicBinaryScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    ["filename", "mimetype", "scraper_class"],
    [
        ("invalid_1.0_no_closing_tag.xml", "text/xml", MagicTextScraper),
        ("invalid_1.0_no_doctype.xhtml", "application/xhtml+xml",
         MagicTextScraper),
        ("invalid_4.01_nodoctype.html", "text/html", MagicTextScraper),
        ("invalid_5.0_nodoctype.html", "text/html", MagicTextScraper),
        ("invalid_1.4_removed_xref.pdf", "application/pdf",
         MagicBinaryScraper),
        ("invalid_1.0_missing_field.arc", "application/x-internet-archive",
         MagicBinaryScraper),
    ])
def test_invalid_markdown_pdf_arc(filename, mimetype, scraper_class,
                                  evaluate_scraper):
    """Test scrapers for invalid XML, XHTML, HTML, pdf and arc files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.update_mimetype(mimetype)
    if correct.streams[0]["stream_type"] == "(:unav)":
        correct.streams[0]["stream_type"] = "text"
    if mimetype != "text/html":
        correct.update_version(filename.split("_")[1])
    scraper = scraper_class(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    correct.well_formed = True

    if correct.streams[0]["mimetype"] == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"

    evaluate_scraper(scraper, correct)


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
        "stderr_part": "MIME type (:unav) with version (:unav) "
                       "is not supported."}
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    scraper = MagicBinaryScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    ["mime", "ver", "scraper_class"],
    [
        ("application/vnd.oasis.opendocument.text", "1.1",
         MagicBinaryScraper),
        ("application/msword", "11.0", MagicBinaryScraper),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml"
         ".document", "15.0", MagicBinaryScraper),
        ("application/vnd.oasis.opendocument.presentation", "1.1",
         MagicBinaryScraper),
        ("application/vnd.ms-powerpoint", "11.0", MagicBinaryScraper),
        ("application/vnd.openxmlformats-officedocument.presentationml"
         ".presentation", "15.0", MagicBinaryScraper),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.1",
         MagicBinaryScraper),
        ("application/vnd.ms-excel", "8.0", MagicBinaryScraper),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml"
         ".sheet", "15.0", MagicBinaryScraper),
        ("application/vnd.oasis.opendocument.graphics", "1.1",
         MagicBinaryScraper),
        ("application/vnd.oasis.opendocument.formula", "1.0",
         MagicBinaryScraper),
        ("image/png", "1.2", MagicBinaryScraper),
        ("image/jpeg", "1.01", MagicBinaryScraper),
        ("image/jp2", "", MagicBinaryScraper),
        ("image/tiff", "6.0", MagicBinaryScraper),
        ("text/plain", "", MagicTextScraper),
        ("text/xml", "1.0", MagicTextScraper),
        ("application/xhtml+xml", "1.0", MagicTextScraper),
        ("application/pdf", "1.4", MagicBinaryScraper),
        ("application/x-internet-archive", "1.0", MagicBinaryScraper),
    ]
)
def test_is_supported_allow(mime, ver, scraper_class):
    """
    Test is_supported method.

    :mime: MIME type
    :ver: File format version
    :scraper_class: Scraper class to test
    """
    assert scraper_class.is_supported(mime, ver, True)
    assert scraper_class.is_supported(mime, None, True)
    assert scraper_class.is_supported(mime, ver, False)
    assert scraper_class.is_supported(mime, "foo", True)
    assert not scraper_class.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("text/html", "4.01"),
    ]
)
def test_is_supported_deny(mime, ver):
    """
    Test is_supported method.

    :mime: MIME type
    :ver: File format version
    """
    assert MagicTextScraper.is_supported(mime, ver, True)
    assert MagicTextScraper.is_supported(mime, None, True)
    assert MagicTextScraper.is_supported(mime, ver, False)
    assert not MagicTextScraper.is_supported(mime, "foo", True)
    assert not MagicTextScraper.is_supported("foo", ver, True)
