#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for XML encoding validator.

This module tests that:
    - Well-formed XML files with latin-1, utf-8 or utf-16 encodings are
      reported as well_formed and the charset is identified correctly.
    - When full scraping is not done, scraper messages contain 'Skipping
      scraper' and well-formedness be reported as None.
    - When full scraping is done, MIME type text/xml with version 1.0 and
      text/html with version 5.0 is reported as supported.
    - When full scraping is not done, text/xml version 1.0 is reported as not
      supported.
    - A correct MIME type with made up version is reported as supported for
      text/xml files but not for text/html files.
    - A made up MIME type with correct version is reported as not supported.
    - Forcing MIME type and/or version works.
"""
from __future__ import unicode_literals

import os
import tempfile
from io import open

import pytest

from file_scraper.lxml_scraper.lxml_scraper import LxmlScraper
from tests.common import force_correct_filetype, partial_message_included


@pytest.mark.parametrize(
    "file_encoding",
    [
        "latin_1", "utf_8", "utf_16"
    ]
)
def test_xml_encoding(testpath, file_encoding):
    """Test that encoding check from XML header works."""
    enc_match = {"latin_1": u"ISO-8859-15",
                 "utf_8": "UTF-8",
                 "utf_16": "UTF-16"}
    xml = """<?xml version="1.0" encoding="{}" ?>
              <a>åäö</a>""".format(enc_match[file_encoding])
    tmppath = os.path.join(testpath, "valid__.csv")
    with open(tmppath, "wb") as file_:
        file_.write(xml.encode(file_encoding))

    scraper = LxmlScraper(tmppath, "text/xml",
                          {"charset": enc_match[file_encoding]})
    scraper.scrape_file()
#    assert scraper.streams[0]["charset"] == enc_match[file_encoding]
    assert scraper.well_formed


def test_no_wellformed(testpath):
    """Test scraper without well-formed check."""
    (_, tmppath) = tempfile.mkstemp()
    xml = """<?xml version="1.0" encoding="UTF-8" ?>
              <a>åäö</a>""".encode("utf-8")
    tmppath = os.path.join(testpath, "valid__.csv")
    with open(tmppath, "wb") as file_:
        file_.write(xml)
    scraper = LxmlScraper(tmppath, False, {"charset": "UTF-8"})
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_is_supported_allow():
    """Test is_supported method for xml files."""
    mime = "text/xml"
    ver = "1.0"
    assert LxmlScraper.is_supported(mime, ver, True)
    assert LxmlScraper.is_supported(mime, None, True)
    assert not LxmlScraper.is_supported(mime, ver, False)
    assert not LxmlScraper.is_supported(mime, ver, True,
                                        {"schematron": "test"})
    assert LxmlScraper.is_supported(mime, "foo", True)
    assert not LxmlScraper.is_supported("foo", ver, True)


def test_is_supported_deny():
    """Test is_supported method for html files."""
    mime = "text/html"
    ver = "5.0"
    assert LxmlScraper.is_supported(mime, ver, True)
    assert LxmlScraper.is_supported(mime, None, True)
    assert not LxmlScraper.is_supported(mime, ver, True,
                                        {"schematron": "test"})
    assert not LxmlScraper.is_supported(mime, ver, False)
    assert not LxmlScraper.is_supported(mime, "foo", True)
    assert not LxmlScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["filename", "result_dict", "filetype"],
    [
        ("valid_1.0_xsd.xml",
         {"purpose": "Test forcing correct MIME type and version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/xml", "given_version": "1.0",
          "expected_mimetype": "text/xml", "expected_version": "1.0",
          "correct_mimetype": "text/xml"}),
        ("valid_1.0_xsd.xml",
         {"purpose": "Test forcing correct MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/xml", "given_version": None,
          "expected_mimetype": "text/xml", "expected_version": "(:unav)",
          "correct_mimetype": "text/xml"}),
        ("valid_1.0_xsd.xml",
         {"purpose": "Test forcing version only (no effect)",
          "stdout_part": "Encoding metadata found.",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "1.0",
          "expected_mimetype": "(:unav)", "expected_version": "(:unav)",
          "correct_mimetype": "text/xml"}),
        ("valid_1.0_xsd.xml",
         {"purpose": "Test forcing wrong MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "is not supported"},
         {"given_mimetype": "unsupported/mime", "given_version": None,
          "expected_mimetype": "unsupported/mime",
          "expected_version": "(:unav)", "correct_mimetype": "text/xml"}),
    ]
)
def test_forced_filetype(filename, result_dict, filetype, evaluate_scraper):
    """
    Test using user-supplied MIME-types and versions.
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype, ["(:unav)"])

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "charset": "UTF-8"}
    scraper = LxmlScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "charset", "well_formed"],
    [("tests/data/text_xml/valid_1.0_xsd.xml", "UTF-8", True),
     ("tests/data/text_xml/valid_1.0_xsd.xml", "ISO-8859-15", False),
     ("tests/data/text_html/valid_5.0.html", "UTF-8", True),
     ("tests/data/text_html/valid_5.0.html", "ISO-8859-15", False),
     ("tests/data/text_xml/valid_1.0_xsd.xml", None, False)
    ]
)
def test_charset(filename, charset, well_formed):
    """
    Test charset parameter.
    """
    params = {"charset": charset}
    scraper = LxmlScraper(filename, True, params)
    scraper.scrape_file()
    assert scraper.well_formed == well_formed
    if charset is not None and not well_formed:
        assert partial_message_included(
            "Found encoding declaration UTF-8", scraper.errors())
    if charset is None:
        assert partial_message_included("encoding not defined",
                                        scraper.errors())
