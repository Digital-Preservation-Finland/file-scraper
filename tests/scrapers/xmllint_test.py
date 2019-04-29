"""
Xmllint scraper tests

This module tests that:
    - MIME type, version, streams and well-formedness of xml files are scraped
      correctly and scraper messages do not contain "<note>".
    - For a well-formed document without schema, scraper messages contains
      "Document is well-formed but does not contain schema."
    - For other well-formed files, scraper messages contains "Success".
    - For file with missing closing tag, scraper messages contains "Opening
      and ending tag mismatch".
    - For invalid given schema and a file without schema, scraper errors
      contains "Schemas validity error".
    - For invalid given schema and a valid file with schema, scraper errors
      contains "parser error".
    - For invalid file with local catalog, scraper errors contains "Missing
      child element(s)".
    - For invalid file with DTD, scraper errors contains "does not follow the
      DTD".
    - For empty file, scraper errors contains "Document is empty".

    - Without well-formedness check, scraper messages contains "Skipping
      scraper" and well_formed is None.

    - MIME type text/xml with version 1.0 or None is supported when well-
      formedness is checked.
    - When well-formedness is not checked, text/xml 1.0 is not supported.
    - A made up MIME type is not supported, but version is.

    - Schema, catalogs and network-usage can be defined as parameters.
"""
import os
import pytest
from file_scraper.xmllint.xmllint_scraper import XmllintScraper
from tests.common import parse_results

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../"))


@pytest.mark.parametrize(
    ["filename", "result_dict", "params"],
    [
        ("valid_1.0_well_formed.xml", {
            "purpose": "Test valid file without schema.",
            "stdout_part": "Document is well-formed but does not contain "
                           "schema.",
            "stderr_part": ""},
         {"catalogs": False}),
        ("valid_1.0_local_xsd.xml", {
            "purpose": "Test valid xml with given schema.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalogs": False,
          "schema": os.path.join(ROOTPATH, "tests/data/text_xml/local.xsd")}),
        ("valid_1.0_catalog.xml", {
            "purpose": "Test valid file with local catalog.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalog_path": "tests/data/text_xml/test-catalog.xml",
          "catalogs": True}),
        ("valid_1.0_dtd.xml", {
            "purpose": "Test valid xml with dtd.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalogs": False})
    ]
)
def test_scraper_valid(filename, result_dict, params, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, "text/xml",
                            result_dict, True, params)
    scraper = XmllintScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
    else:
        evaluate_scraper(scraper, correct)
    assert "<note>" not in scraper.messages()


@pytest.mark.parametrize(
    ["filename", "result_dict", "params"],
    [
        ("invalid_1.0_no_closing_tag.xml", {
            "purpose": "Test invalid file without schema.",
            "stdout_part": "",
            "stderr_part": "Opening and ending tag mismatch"},
         {"catalogs": False}),
        ("invalid_1.0_local_xsd.xml", {
            "purpose": "Test invalid xml with given schema.",
            "stdout_part": "",
            "stderr_part": "Schemas validity error"},
         {"catalogs": False, "schema": os.path.join(
             ROOTPATH, "tests/data/text_xml/local.xsd")}),
        ("valid_1.0_local_xsd.xml", {
            "purpose": "Test valid xml with given invalid schema.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "parser error"},
         {"catalogs": False, "schema": os.path.join(
             ROOTPATH, "tests/data/text_xml/invalid_local.xsd")}),
        ("invalid_1.0_catalog.xml", {
            "purpose": "Test invalid file with local catalog.",
            "stdout_part": "",
            "stderr_part": "Missing child element(s)"},
         {"catalog_path": "tests/data/text_xml/test-catalog.xml",
          "catalogs": True}),
        ("invalid_1.0_dtd.xml", {
            "purpose": "Test invalid xml with dtd.",
            "stdout_part": "",
            "stderr_part": "does not follow the DTD"},
         {"catalogs": False}),
        ("invalid__empty.xml", {
            "purpose": "Test empty xml.",
            "stdout_part": "",
            "stderr_part": "Document is empty"}, {})
    ]
)
def test_scraper_invalid(filename, result_dict, params, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, "text/xml",
                            result_dict, True, params)
    scraper = XmllintScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    if "empty" in filename or "no_closing_tag" in filename:
        correct.version = None
        correct.streams[0]["version"] = None

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
    else:
        evaluate_scraper(scraper, correct)
    assert "<note>" not in scraper.messages()


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = XmllintScraper("tests/data/text_xml/valid_1.0_wellformed.xml",
                             False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = "text/xml"
    ver = "1.0"
    assert XmllintScraper.is_supported(mime, ver, True)
    assert XmllintScraper.is_supported(mime, None, True)
    assert not XmllintScraper.is_supported(mime, ver, False)
    assert XmllintScraper.is_supported(mime, "foo", True)
    assert not XmllintScraper.is_supported("foo", ver, True)


def test_parameters():
    """Test that parameters and default values work properly."""
    # pylint: disable=protected-access
    scraper = XmllintScraper("testsfile", "test/mimetype")
    assert scraper._schema is None
    assert scraper._catalogs
    assert scraper._no_network
    assert scraper._catalog_path is None

    scraper = XmllintScraper("testsfile", params={"schema": "schemafile",
                                                  "catalogs": False,
                                                  "no_network": False})
    assert scraper._schema == "schemafile"
    assert not scraper._catalogs
    assert not scraper._no_network

    scraper = XmllintScraper("testsfile", params={"catalog_path": "catpath"})
    assert scraper._catalogs
    assert scraper._catalog_path == "catpath"
