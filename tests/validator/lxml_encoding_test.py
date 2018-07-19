#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for XML encoding validator.
"""

import os
import tempfile
import pytest
from ipt.validator.lxml_encoding import XmlEncoding


@pytest.mark.parametrize(
    ['mimetype', 'version', 'encoding', 'file_encoding'],
    [
        ('text/xml', '1.0', 'ISO-8859-15', 'latin_1'),
        ('text/xml', '1.0', 'UTF-8', 'latin_1'),
        ('text/xml', '1.0', 'UTF-16', 'latin_1'),
        ('text/xml', '1.0', 'ISO-8859-15', 'utf_8'),
        ('text/xml', '1.0', 'UTF-8', 'utf_8'),
        ('text/xml', '1.0', 'UTF-16', 'utf_8'),
        ('text/xml', '1.0', 'ISO-8859-15', 'utf_16'),
        ('text/xml', '1.0', 'UTF-8', 'utf_16'),
        ('text/xml', '1.0', 'UTF-16', 'utf_16'),
    ]
)
def test_validate_xml_encoding(mimetype, version, encoding, file_encoding):
    enc_match = {'latin_1': 'ISO-8859-15',
                 'utf_8': 'UTF-8',
                 'utf_16': 'UTF-16'}
    (tmphandle, tmppath) = tempfile.mkstemp()
    xml = '''<?xml version="1.0" encoding="{}" ?>
             <a>åäö</a>'''.format(enc_match[file_encoding])
    with open(tmppath, 'w') as f:
        f.write(xml.decode('utf8').encode(file_encoding))

    metadata_info = {
        'filename': tmppath,
        'format': {
            'mimetype': mimetype,
            'version': version,
            'charset': encoding
        }
    }

    validator = XmlEncoding(metadata_info)
    validator.validate()
    f.close()
    os.remove(tmppath)
    assert validator.is_valid == bool(encoding == enc_match[file_encoding])
