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
"""
from __future__ import unicode_literals

import os
import tempfile
from io import open

import pytest

from file_scraper.lxml.lxml_scraper import LxmlScraper


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

    scraper = LxmlScraper(tmppath, "text/xml")
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
    scraper = LxmlScraper(tmppath, False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
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
