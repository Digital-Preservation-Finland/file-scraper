#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for XML encoding validator.

This module tests that:
    - Well-formed XML files with latin-1, utf-8 or utf-16 encodings are
      reported as well_formed and the charset is identified correctly.
    - When full scraping is done, MIME type text/xml with version 1.0 and
      text/html with version 5.0 is reported as supported.
    - When full scraping is not done, text/xml version 1.0 is reported as not
      supported.
    - A correct MIME type with made up version is reported as supported for
      text/xml files but not for text/html files.
    - A made up MIME type with correct version is reported as not supported.
    - Scraper works as designed with charset parameter.
"""
from __future__ import unicode_literals

import os
import tempfile
import io

import pytest

from file_scraper.lxml_scraper.lxml_scraper import LxmlScraper
from tests.common import partial_message_included


@pytest.mark.parametrize(
    "file_encoding",
    [
        "latin_1", "utf_8", "utf_16"
    ]
)
def test_xml_encoding(testpath, file_encoding):
    """
    Test that encoding check from XML header works.

    :file_encoding: File character encoding
    """
    enc_match = {"latin_1": u"ISO-8859-15",
                 "utf_8": "UTF-8",
                 "utf_16": "UTF-16"}
    xml = """<?xml version="1.0" encoding="{}" ?>
              <a>åäö</a>""".format(enc_match[file_encoding])
    tmppath = os.path.join(testpath, "valid__.csv")
    with io.open(tmppath, "wb") as file_:
        file_.write(xml.encode(file_encoding))

    scraper = LxmlScraper(filename=tmppath, mimetype="text/xml",
                          params={"charset": enc_match[file_encoding]})
    scraper.scrape_file()
    assert scraper.well_formed


def test_is_supported_allow():
    """Test is_supported method for xml 1.0 files."""
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
    """Test is_supported method for html 5.0 files."""
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
    ["filename", "mimetype", "charset", "well_formed"],
    [("tests/data/text_xml/valid_1.0_xsd.xml", "text/xml", "UTF-8", True),
     ("tests/data/text_xml/valid_1.0_xsd.xml", "text/xml", "ISO-8859-15",
      False),
     ("tests/data/text_html/valid_5.0.html", "text/html", "UTF-8", True),
     ("tests/data/text_html/valid_5.0.html", "text/html", "ISO-8859-15",
      False),
     ("tests/data/text_xml/valid_1.0_xsd.xml", "text/xml", None, False)
    ]
)
def test_charset(filename, mimetype, charset, well_formed):
    """
    Test charset parameter.

    :filename: Test file name
    :mimetype: File MIME type
    :charset: File character encoding
    :well_formed: Expected result of well-formedness
    """
    params = {"charset": charset}
    scraper = LxmlScraper(filename=filename, mimetype=mimetype, params=params)
    scraper.scrape_file()
    assert scraper.well_formed == well_formed
    if charset:
        if well_formed:
            assert not scraper.errors()
        else:
            assert partial_message_included(
                "Found encoding declaration UTF-8", scraper.errors())
    else:
        assert partial_message_included("encoding not defined",
                                        scraper.errors())
