#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for File (libmagick) scraper.
"""

import os
import tempfile
import pytest
from dpres_scraper.scrapers.magic import OfficeFileMagic, TextFileMagic, \
    XmlFileMagic, HtmlFileMagic, PngFileMagic, JpegFileMagic, TiffFileMagic, \
    Jp2FileMagic


BASEPATH = "tests/data"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'class_'],
    [
        ("valid_1.1.odt",
         "application/vnd.oasis.opendocument.text", OfficeFileMagic),
        ("valid_11.0.doc",
         "application/msword", OfficeFileMagic),
        ("valid_15.0.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document", OfficeFileMagic),
        ("valid_1.1.odp",
         "application/vnd.oasis.opendocument.presentation", OfficeFileMagic),
        ("valid_11.0.ppt",
         "application/vnd.ms-powerpoint", OfficeFileMagic),
        ("valid_15.0.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation",
         OfficeFileMagic),
        ("valid_1.1.ods",
         "application/vnd.oasis.opendocument.spreadsheet", OfficeFileMagic),
        ("valid_11.0.xls",
         "application/vnd.ms-excel", OfficeFileMagic),
        ("valid_15.0.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         OfficeFileMagic),
        ("valid_1.1.odg",
         "application/vnd.oasis.opendocument.graphics", OfficeFileMagic),
        ("valid_1.0.odf",
         "application/vnd.oasis.opendocument.formula", OfficeFileMagic),
        ("valid_1.2.png", "image/png", PngFileMagic),
        ("valid_1.01.jpg", "image/jpeg", JpegFileMagic),
        ("valid.jp2", "image/jp2", Jp2FileMagic),
        ("valid_6.0.tif", "image/tiff", TiffFileMagic),
        ("valid_iso8859.txt", "text/plain", TextFileMagic),
        ("valid_utf8.txt", "text/plain", TextFileMagic),
        ("valid_1.0.xml", "text/xml", XmlFileMagic),
        ("valid_1.0.xhtml", "application/xhtml+xml", HtmlFileMagic),
        ("valid_4.01.html", "text/html", HtmlFileMagic),
        ("valid_5.0.html", "text/html", HtmlFileMagic)
    ])
def test_scrape_valid(filename, mimetype, class_):
    scraper = class_(
        os.path.join(BASEPATH, mimetype.replace("/", "_"), filename),
                     mimetype)
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Empty file
        ("office/empty_file.doc", "application/msword"),
        # .zip renamed to .docx
        ("office/MS_Word_2007-2013_XML_zip.docx",
         "application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document"),
        # Bad xmlx created by LibreOffice
        ("office/Office_Open_XML_Spreadsheet.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        # Wrong MIME
        ("office/ODF_Text_Document.odt", "application/msword"),
        # .odt renamed to .doc
        ("office/ODF_Text_Document_with_wrong_filename_extension.doc",
         "application/msword"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):

    scraper = OfficeFileMagic(
        os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert not scraper.well_formed
