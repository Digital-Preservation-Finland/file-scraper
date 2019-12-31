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

    - For empty files, all these scrapers report MIME type as inode/x-empty.

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
        - version is None
        - MIME type is application/octet-stream
        - scraper errors contains "do not match"
        - file is not well-formed

    - Running scraper without full scraping results in well_formed being None
      and scraper messages containing "Skipping scraper"

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
    - Valid MIME type with made up version is supported, except
      text/html
    - Made up MIME type with any version is not supported
    - When full scraping is not done, none of these combinations are supported.

    - The scraper requires the parameter dict to contain "mimetype_guess"
      entry.
    - If the scraper determines the file to be either XML or XHTML file and
      would thus need to use the supplied MIME type from the dict, but the
      given MIME type does not match either of the types, an error is recorded,
      no metadata is scraped and the file is reported as not well-formed.
    - Forcing MIME type and/or version works:
        - messages are recorded
        - forcing an unsupported MIME type causes an error
        - only forcing version has no effect
        - MIME type can be forced alone
        - for metadata models that support multiple MIME types, using another
          supported MIME type does not cause an error (see docstring of
          test_mixed_filetype for details).
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.magic_scraper.magic_model import (HtmlFileMagicMeta,
                                                    OfficeFileMagicMeta)
from file_scraper.magic_scraper.magic_scraper import MagicScraper
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("valid_1.1.odt",
         "application/vnd.oasis.opendocument.text"),
        ("valid_11.0.doc",
         "application/msword"),
        ("valid_15.0.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("valid_1.1.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("valid_11.0.ppt",
         "application/vnd.ms-powerpoint"),
        ("valid_15.0.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("valid_1.1.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("valid_11.0.xls",
         "application/vnd.ms-excel"),
        ("valid_15.0.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("valid_1.1.odg",
         "application/vnd.oasis.opendocument.graphics"),
        ("valid_1.0.odf",
         "application/vnd.oasis.opendocument.formula"),
        ("valid_1.2.png", "image/png"),
        ("valid_1.01.jpg", "image/jpeg"),
        ("valid.jp2", "image/jp2"),
        ("valid_6.0.tif", "image/tiff"),
        ("valid__iso8859.txt", "text/plain"),
        ("valid__utf8_without_bom.txt", "text/plain"),
        ("valid_1.0_well_formed.xml", "text/xml"),
        ("valid_1.0.xhtml", "application/xhtml+xml"),
        ("valid_4.01.html", "text/html"),
        ("valid_5.0.html", "text/html"),
        ("valid_1.4.pdf", "application/pdf"),
        ("valid_1.0.arc", "application/x-internet-archive"),
    ])
def test_scraper_valid(filename, mimetype, evaluate_scraper):
    """Test scraper."""
    result_dict = {
        "purpose": "Test valid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = MagicScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if correct.streams[0]["mimetype"] == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"
    if (OfficeFileMagicMeta.is_supported(correct.streams[0]["mimetype"]) or
            HtmlFileMagicMeta.is_supported(correct.streams[0]["mimetype"])):
        correct.streams[0]["version"] = "(:unav)"
    if correct.streams[0]["mimetype"] in ["text/plain", "text/csv"]:
        correct.streams[0]["charset"] = "UTF-8"
        correct.streams[0]["version"] = "(:unap)"
    if mimetype == "text/html" or "vnd." in mimetype or "msword" in mimetype:
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
        "stderr_part": "MIME type application/octet-stream with version "
                       "(:unav) is not supported."}
    if "empty" in filename:
        result_dict["stderr_part"] = "MIME type inode/x-empty with version " \
            "(:unav) is not supported."

    correct = parse_results(filename, mimetype,
                            result_dict, True)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    scraper = MagicScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid_1.0_no_closing_tag.xml", "text/xml"),
        ("invalid_1.0_no_doctype.xhtml", "application/xhtml+xml"),
        ("invalid_4.01_nodoctype.html", "text/html"),
        ("invalid_5.0_nodoctype.html", "text/html"),
        ("invalid_1.4_removed_xref.pdf", "application/pdf"),
        ("invalid_1.0_missing_field.arc", "application/x-internet-archive"),
    ])
def test_invalid_markdown_pdf_arc(filename, mimetype, evaluate_scraper):
    """Test scrapers for invalid XML, XHTML, HTML, pdf and arc files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "successfully",
        "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.update_mimetype(mimetype)
    if mimetype != "text/html":
        correct.update_version(filename.split("_")[1])
    scraper = MagicScraper(filename=correct.filename, mimetype=mimetype)
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
        "stderr_part": "MIME type application/octet-stream with version (:unav) "
                       "is not supported."}
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    scraper = MagicScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    ["filename", "mimetype", "error"],
    [
        ("invalid__binary_data.txt", "text/plain",
         "MIME type application/octet-stream with version (:unap) is not "
         "supported."),
        ("invalid__empty.txt", "text/plain",
         "MIME type inode/x-empty with version (:unap) is not supported."),
    ])
def test_invalid_text(filename, mimetype, error):
    """Test TextFileMagic with invalid files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": error}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    correct.update_mimetype(mimetype)
    correct.update_version(filename.split("_")[1])
    scraper = MagicScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    correct.streams[0]["charset"] = None

    assert not scraper.well_formed
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = MagicScraper(filename="tests/data/image_jpeg/valid_1.01.jpg",
                           mimetype="image/jpeg", check_wellformed=False)
    scraper.scrape_file()
    assert not partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("application/vnd.oasis.opendocument.text", "1.1"),
        ("application/msword", "11.0"),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml"
         ".document", "15.0"),
        ("application/vnd.oasis.opendocument.presentation", "1.1"),
        ("application/vnd.ms-powerpoint", "11.0"),
        ("application/vnd.openxmlformats-officedocument.presentationml"
         ".presentation", "15.0"),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.1"),
        ("application/vnd.ms-excel", "8.0"),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml"
         ".sheet", "15.0"),
        ("application/vnd.oasis.opendocument.graphics", "1.1"),
        ("application/vnd.oasis.opendocument.formula", "1.0"),
        ("image/png", "1.2"),
        ("image/jpeg", "1.01"),
        ("image/jp2", "(:unap)"),
        ("image/tiff", "6.0"),
        ("text/plain", ""),
        ("text/xml", "1.0"),
        ("application/xhtml+xml", "1.0"),
        ("application/pdf", "1.4"),
        ("application/x-internet-archive", "1.0"),
    ]
)
def test_is_supported_allow(mime, ver):
    """Test is_supported method."""
    assert MagicScraper.is_supported(mime, ver, True)
    assert MagicScraper.is_supported(mime, None, True)
    assert MagicScraper.is_supported(mime, ver, False)
    assert MagicScraper.is_supported(mime, "foo", True)
    assert not MagicScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("text/html", "4.01"),
    ]
)
def test_is_supported_deny(mime, ver):
    """Test is_supported method."""
    assert MagicScraper.is_supported(mime, ver, True)
    assert MagicScraper.is_supported(mime, None, True)
    assert MagicScraper.is_supported(mime, ver, False)
    assert not MagicScraper.is_supported(mime, "foo", True)
    assert not MagicScraper.is_supported("foo", ver, True)
