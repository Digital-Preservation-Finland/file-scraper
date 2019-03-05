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
        ("documents/ODF_Text_Document.odt",
         "application/vnd.oasis.opendocument.text", OfficeFileMagic),
        ("documents/ODF_Text_Document.odt",
         "application/vnd.oasis.opendocument.text", OfficeFileMagic),
        ("documents/MS_Word_97-2003.doc",
         "application/msword", OfficeFileMagic),
        ("documents/Office_Open_XML_Text.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document", OfficeFileMagic),
        ("documents/ODF_Presentation.odp",
         "application/vnd.oasis.opendocument.presentation", OfficeFileMagic),
        ("documents/MS_PowerPoint_97-2003.ppt",
         "application/vnd.ms-powerpoint", OfficeFileMagic),
        ("documents/Office_Open_XML_Presentation.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation",
         OfficeFileMagic),
        ("documents/ODF_Spreadsheet.ods",
         "application/vnd.oasis.opendocument.spreadsheet", OfficeFileMagic),
        ("documents/MS_Excel_97-2003.xls",
         "application/vnd.ms-excel", OfficeFileMagic),
        ("documents/Excel_Online_Spreadsheet.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         OfficeFileMagic),
        ("documents/ODF_Drawing.odg",
         "application/vnd.oasis.opendocument.graphics", OfficeFileMagic),
        ("documents/ODF_Formula.odf",
         "application/vnd.oasis.opendocument.formula", OfficeFileMagic),
        ("images/valid_png.png", "image/png", PngFileMagic),
        ("images/valid_jpeg.jpeg", "image/jpeg", JpegFileMagic),
        ("images/valid_jp2.jp2", "image/jp2", Jp2FileMagic),
        ("images/valid_tiff.tiff", "image/tiff", TiffFileMagic),
        ("text/iso-8859.txt", "tet/plain", TextFileMagic),
        ("text/utf8.txt", "text/plain", TextFileMagic),
        ("text/valid.xml", "text/xml", XmlFileMagic),
        ("text/valid.xhtml", "applivation/xhtml+xml", HtmlFileMagic),
        ("text/valid_4.html", "text/html", HtmlFileMagic),
        ("text/valid_5.html", "text/html", HtmlFileMagic)
    ])
def test_scrape_valid(filename, mimetype, class_):
    scraper = class_(
        os.path.join(BASEPATH, filename), mimetype)
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
