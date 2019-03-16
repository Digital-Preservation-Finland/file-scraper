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
    enc_match = {'latin_1': 'ISO-8859-15',
                 'utf_8': 'UTF-8',
                 'utf_16': 'UTF-16'}
    (tmphandle, tmppath) = tempfile.mkstemp()
    xml = '''<?xml version="1.0" encoding="{}" ?>
             <a>åäö</a>'''.format(enc_match[file_encoding])
    with open(tmppath, 'w') as f:
        f.write(xml.decode('utf8').encode(file_encoding))

    scraper = XmlEncoding(tmppath, 'text/xml')
    scraper.scrape_file()
    f.close()
    os.remove(tmppath)
    assert scraper.streams[0]['charset'] == enc_match[file_encoding]
    assert scraper.well_formed == True
