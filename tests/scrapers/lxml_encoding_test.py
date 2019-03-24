#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for XML encoding validator.
"""

import os
import tempfile
import pytest
from file_scraper.scrapers.lxml_encoding import XmlEncoding


@pytest.mark.parametrize(
    'file_encoding',
    [
        'latin_1', 'utf_8', 'utf_16'
    ]
)
def test_xml_encoding(file_encoding):
    """Test that encoding check from XML header works.
    """
    enc_match = {'latin_1': 'ISO-8859-15',
                 'utf_8': 'UTF-8',
                 'utf_16': 'UTF-16'}
    (_, tmppath) = tempfile.mkstemp()
    xml = '''<?xml version="1.0" encoding="{}" ?>
             <a>åäö</a>'''.format(enc_match[file_encoding])
    with open(tmppath, 'w') as file_:
        file_.write(xml.decode('utf8').encode(file_encoding))

    scraper = XmlEncoding(tmppath, 'text/xml')
    scraper.scrape_file()
    os.remove(tmppath)
    assert scraper.streams[0]['charset'] == enc_match[file_encoding]
    assert scraper.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check"""
    (_, tmppath) = tempfile.mkstemp()
    xml = '''<?xml version="1.0" encoding="{}" ?>
             <a>åäö</a>'''.format('UTF-8')
    with open(tmppath, 'w') as file_:
        file_.write(xml)
    scraper = XmlEncoding(tmppath, 'text/xml', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method"""
    mime = 'text/xml'
    ver = '1.0'
    assert XmlEncoding.is_supported(mime, ver, True)
    assert XmlEncoding.is_supported(mime, None, True)
    assert not XmlEncoding.is_supported(mime, ver, False)
    assert not XmlEncoding.is_supported(mime, 'foo', True)
    assert not XmlEncoding.is_supported('foo', ver, True)
