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
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)


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
    params = correct.params
    params["mimetype_guess"] = correct.mimetype
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    if correct.mimetype == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"
    if (OfficeFileMagicMeta.is_supported(correct.mimetype) or
            HtmlFileMagicMeta.is_supported(correct.mimetype)):
        correct.version = None
        correct.streams[0]["version"] = None
    if correct.mimetype in ["text/plain", "text/csv"]:
        correct.streams[0]["version"] = "(:unap)"
    if mimetype == "text/html" or "vnd." in mimetype or "msword" in mimetype:
        correct.streams[0]["version"] = "(:unav)"
    if mimetype == "image/jp2":
        correct.streams[0]["version"] = ""

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
        "stderr_part": "Unsupported MIME type"}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    params = correct.params
    params["mimetype_guess"] = correct.mimetype
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    if "empty" in filename:
        correct.streams[0]["mimetype"] = "inode/x-empty"
        correct.mimetype = "inode/x-empty"
    else:
        correct.streams[0]["mimetype"] = "application/octet-stream"
        correct.mimetype = "application/octet-stream"

    correct.version = None
    correct.streams[0]["version"] = None

    assert not scraper.well_formed
    assert not scraper.streams
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
    params = correct.params
    params["mimetype_guess"] = correct.mimetype
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    correct.well_formed = True

    if "empty" in filename:
        correct.streams[0]["mimetype"] = "inode/x-empty"

    if correct.mimetype == "text/html":
        correct.streams[0]["version"] = "(:unav)"
    if correct.mimetype == "application/xhtml+xml":
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
        "stderr_part": "Unsupported MIME type"}
    correct = parse_results(filename, mimetype, result_dict, True)
    params = correct.params
    params["mimetype_guess"] = correct.mimetype
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    if "empty" in filename:
        correct.streams[0]["mimetype"] = "inode/x-empty"
        correct.mimetype = "inode/x-empty"
    else:
        correct.streams[0]["mimetype"] = "application/octet-stream"
        correct.mimetype = "application/octet-stream"

    correct.version = None
    correct.streams[0]["version"] = None

    assert not scraper.well_formed
    assert not scraper.streams
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid__binary_data.txt", "text/plain"),
        ("invalid__empty.txt", "text/plain"),
    ])
def test_invalid_text(filename, mimetype):
    """Test TextFileMagic with invalid files."""
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": "Unsupported MIME type"}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    params = correct.params
    params["mimetype_guess"] = correct.mimetype
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    if "empty" in filename:
        correct.streams[0]["mimetype"] = "inode/x-empty"
        correct.mimetype = "inode/x-empty"
    else:
        correct.streams[0]["mimetype"] = "application/octet-stream"
        correct.mimetype = "application/octet-stream"

    correct.version = None
    correct.streams[0]["version"] = None
    correct.streams[0]["charset"] = None

    assert not scraper.well_formed
    assert not scraper.streams
    assert partial_message_included(correct.stdout_part, scraper.messages())
    assert partial_message_included(correct.stderr_part, scraper.errors())


@pytest.mark.parametrize(
    "filepath",
    ["tests/data/text_xml/valid_1.0_catalog.xml",
     "tests/data/application_xhtml+xml/valid_1.0.xhtml"])
def test_wrong_mime_with_xml(filepath):
    """
    Test giving wrong MIME type for text/xml or application/xhtml+xml file.

    This should cause an error to be recorded by the scraper, as those scrapers
    need the MIME type information from outside.
    """
    scraper = MagicScraper(filepath, True, {"mimetype_guess": "wrong/mime"})
    scraper.scrape_file()
    assert not scraper.well_formed
    assert not scraper.streams
    assert partial_message_included("does not match", scraper.errors())


def test_no_mime_given():
    """Test that an error is recorded when no MIME type is given."""
    scraper = MagicScraper(
        "tests/data/text_plain/valid__utf8_without_bom.txt", True, {})
    with pytest.raises(AttributeError) as error:
        scraper.scrape_file()
    assert (
        "not given a parameter dict containing key 'mimetype_guess'"
        in six.text_type(error.value)
    )
    assert ("not given a parameter dict containing key 'mimetype_guess'" in
            str(error.value))
    assert not scraper.well_formed
    assert not scraper.streams


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = MagicScraper("tests/data/image_jpeg/valid_1.01.jpg", False,
                           {"mimetype_guess": "image/jpeg"})
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


def run_filetype_test(filename, result_dict, filetype, evaluate_scraper):
    """
    Runs scraper result evaluation for a scraper with forced MIME type/version

    :filename: Name of the file, not containing the tests/data/mime_type/ part
    :result_dict: Result dict to be given to Correct
    :filetype: A dict containing the forced, expected and real file types under
               the following keys:
                * given_mimetype: the forced MIME type
                * given_version: the forced version
                * expected_mimetype: the expected resulting MIME type
                * expected_version: the expected resulting version
                * correct_mimetype: the real MIME type of the file
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype)
    if correct.mimetype == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "version_result"],
    [
        ("valid__utf8_without_bom.txt", "text/plain", "(:unap)", "(:unap)"),
        ("valid_1.0_well_formed.xml", "text/xml", "1.0", "1.0"),
        ("valid_1.0.xhtml", "application/xhtml+xml", "1.0", "1.0"),
        ("valid_4.01.html", "text/html", "4.01", "(:unav)"),
        ("valid_1.7.pdf", "application/pdf", "1.7", "1.7"),
        ("valid_1.1.odt", "application/vnd.oasis.opendocument.text", "1.1",
         "(:unav)"),
        ("valid_1.0.arc", "application/x-internet-archive", "1.0", "1.0"),
        ("valid_1.2.png", "image/png", "1.2", "1.2"),
        ("valid_1.01.jpg", "image/jpeg", "1.01", "1.01"),
        ("valid.jp2", "image/jp2", "", ""),
        ("valid_6.0_multiple_tiffs.tif", "image/tiff", "6.0", "6.0")
    ]
)
def test_forced_filetype(filename, mimetype, version, version_result,
                         evaluate_scraper):
    """
    Tests the simple cases of file type forcing.

    Here, the following cases are tested for one file type scraped using each
    metadata model class supported by MagicScraper:
        - Force the scraper to use the correct MIME type and version, which
          should always result in the given MIME type and version and the file
          should be well-formed.
        - Force the scraper to use the correct MIME type, which should always
          result in the given MIME type and the version the metadata model
          would normally return.
        - Give forced version without MIME type, which should result in the
          scraper running normally and not affect its results or messages.
        - Force the scraper to use an unsupported MIME type, which should
          result in an error message being logged and the scraper reporting
          the file as not well-formed.
    """
    # Correct version forcing can only be done if there is a version to use
    if version:
        result_dict = {"purpose": "Test forcing correct MIME type and version",
                       "stdout_part": "MIME type and version not scraped",
                       "stderr_part": ""}
        filetype_dict = {"given_mimetype": mimetype,
                         "given_version": version,
                         "expected_mimetype": mimetype,
                         "expected_version": version,
                         "correct_mimetype": mimetype}
        run_filetype_test(filename, result_dict, filetype_dict,
                          evaluate_scraper)

    result_dict = {"purpose": "Test forcing correct MIME type without version",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": None,
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing version only (no effect)",
                   "stdout_part": "The file was analyzed successfully",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": None,
                     "given_version": "99.9",
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing wrong MIME type",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": "Unsupported MIME type"}
    filetype_dict = {"given_mimetype": "unsupported/mime",
                     "given_version": None,
                     "expected_mimetype": "unsupported/mime",
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)


@pytest.mark.parametrize(
    ["filename", "result_dict", "filetype"],
    [
        ("valid__utf8_without_bom.txt",
         {"purpose": "Test forcing text file to CSV file",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/csv", "given_version": None,
          "expected_mimetype": "text/csv", "expected_version": "(:unap)",
          "correct_mimetype": "text/plain"}),
        ("valid_1.7.pdf",
         {"purpose": "Test forcing wrong but supported version for pdf file",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf", "given_version": "1.2",
          "expected_mimetype": "application/pdf", "expected_version": "1.2",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.1.ods",
         {"purpose": "Test scraping and office file as another office type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/vnd.oasis.opendocument.graphics",
          "given_version": None,
          "expected_mimetype":
              "application/vnd.oasis.opendocument.graphics",
          "expected_version": "(:unav)",
          "correct_mimetype":
              "application/vnd.oasis.opendocument.spreadsheet"}),
    ]
)
def test_mixed_filetype(filename, result_dict, filetype, evaluate_scraper):
    """
    Test scraping files as wrong but supported file type.

    Some metadata models support many file types. For example, OfficeMagicMeta
    supports text, spreadsheet and presentation in both MS and open formats,
    among other file types. A side effect of this is that it is entirely
    possible to scrape e.g. an ods file as a doc (or xls) file by just forcing
    the file type the scraper uses, and this does not produce errors and the
    file is reported as well-formed.

    Currently this does not cause problems if the user is aware of this
    functionality, as no metadata scraping results are affected by it. This
    test can hopefully catch if problematic metadata functions are
    introduced in the future.
    """
    correct = parse_results(filename, filetype["correct_mimetype"],
                            result_dict, True)
    correct.update_mimetype(filetype["expected_mimetype"])
    correct.update_version(filetype["expected_version"])

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = MagicScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
