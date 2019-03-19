#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for XML encoding validator.

This module tests that:
    - Well-formed XML files with latin-1, utf-8 or utf-16 encodings are
      reported as well_formed and the charset is identified correctly.
    - When full scraping is not done, scraper messages contain 'Skipping
      scraper' and well-formedness be reported as None.
    - When full scraping is done, MIME type text/xml with version 1.0 or None
      is reported as supported.
    - When full scraping is not done, text/xml version 1.0 is reported as not
      supported.
    - A correct MIME type with made up version is reported as not supported.
    - A made up MIME type with correct version is reported as not supported.
"""

import os
import tempfile
import pytest
from io import open
from file_scraper.scrapers.lxml_encoding import XmlEncoding


@pytest.mark.parametrize(
    'file_encoding',
    [
        'latin_1', 'utf_8', 'utf_16'
    ]
)
def test_xml_encoding(testpath, file_encoding):
    """Test that encoding check from XML header works."""
    enc_match = {'latin_1': u'ISO-8859-15',
                 'utf_8': u'UTF-8',
                 'utf_16': u'UTF-16'}
    xml = u'''<?xml version="1.0" encoding="{}" ?>
              <a>åäö</a>'''.format(enc_match[file_encoding])
    tmppath = os.path.join(testpath, 'valid__.csv')
    with open(tmppath, 'wb') as file_:
        file_.write(xml.encode(file_encoding))

    scraper = XmlEncoding(tmppath, 'text/xml')
    scraper.scrape_file()
    assert scraper.streams[0]['charset'] == enc_match[file_encoding]
    assert scraper.well_formed


def test_no_wellformed(testpath):
    """Test scraper without well-formed check."""
    (_, tmppath) = tempfile.mkstemp()
    xml = u'''<?xml version="1.0" encoding="UTF-8" ?>
              <a>åäö</a>'''
    tmppath = os.path.join(testpath, 'valid__.csv')
    with open(tmppath, 'w', encoding='utf-8') as file_:
        file_.write(xml)
    scraper = XmlEncoding(tmppath, 'text/xml', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = 'text/xml'
    ver = '1.0'
    assert XmlEncoding.is_supported(mime, ver, True)
    assert XmlEncoding.is_supported(mime, None, True)
    assert not XmlEncoding.is_supported(mime, ver, False)
    assert not XmlEncoding.is_supported(mime, 'foo', True)
    assert not XmlEncoding.is_supported('foo', ver, True)
