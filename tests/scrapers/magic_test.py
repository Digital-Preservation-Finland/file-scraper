#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for File (libmagick) scraper.
"""
import pytest
from file_scraper.scrapers.magic import OfficeFileMagic, TextFileMagic, \
    XmlFileMagic, HtmlFileMagic, PngFileMagic, JpegFileMagic, TiffFileMagic, \
    Jp2FileMagic, XhtmlFileMagic, PdfFileMagic, ArcFileMagic
from tests.common import parse_results


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
        ("valid__iso8859.txt", "text/plain", TextFileMagic),
        ("valid__utf8.txt", "text/plain", TextFileMagic),
        ("valid_1.0_well_formed.xml", "text/xml", XmlFileMagic),
        ("valid_1.0.xhtml", "application/xhtml+xml", XhtmlFileMagic),
        ("valid_4.01.html", "text/html", HtmlFileMagic),
        ("valid_5.0.html", "text/html", HtmlFileMagic),
        ("valid_1.4.pdf", "application/pdf", PdfFileMagic),
        ("valid_1.0.arc", "application/x-internet-archive", ArcFileMagic),
    ])
def test_scraper_valid(filename, mimetype, class_):
    """Test scraper"""
    result_dict = {
        'purpose': 'Test valid file.',
        'stdout_part': 'successfully',
        'stderr_part': ''}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = class_(correct.filename, correct.mimetype,
                     True, correct.params)
    scraper.scrape_file()

    if class_ in [XhtmlFileMagic]:
        correct.streams[0]['stream_type'] = 'text'
    if class_ in [OfficeFileMagic, HtmlFileMagic]:
        correct.version = None
        correct.streams[0]['version'] = None
    if class_ in [TextFileMagic, HtmlFileMagic, XmlFileMagic, XhtmlFileMagic]:
        correct.streams[0]['charset'] = 'UTF-8'
    if filename == 'valid__iso8859.txt':
        correct.streams[0]['charset'] = 'ISO-8859-15'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == class_.__name__
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'class_'],
    [
        ("invalid_1.1_missing_data.odt",
         "application/vnd.oasis.opendocument.text", OfficeFileMagic),
        ("invalid_11.0_missing_data.doc",
         "application/msword", OfficeFileMagic),
        ("invalid_15.0_missing_data.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document", OfficeFileMagic),
        ("invalid_1.1_missing_data.odp",
         "application/vnd.oasis.opendocument.presentation", OfficeFileMagic),
        ("invalid_11.0_missing_data.ppt",
         "application/vnd.ms-powerpoint", OfficeFileMagic),
        ("invalid_15.0_missing_data.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation",
         OfficeFileMagic),
        ("invalid_1.1_missing_data.ods",
         "application/vnd.oasis.opendocument.spreadsheet", OfficeFileMagic),
        ("invalid_11.0_missing_data.xls",
         "application/vnd.ms-excel", OfficeFileMagic),
        ("invalid_15.0_missing_data.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         OfficeFileMagic),
        ("invalid_1.1_missing_data.odg",
         "application/vnd.oasis.opendocument.graphics", OfficeFileMagic),
        ("invalid_1.0_missing_data.odf",
         "application/vnd.oasis.opendocument.formula", OfficeFileMagic),
        ("invalid_1.2_wrong_header.png", "image/png", PngFileMagic),
        ("invalid_1.01_no_start_marker.jpg", "image/jpeg", JpegFileMagic),
        ("invalid__data_missing.jp2", "image/jp2", Jp2FileMagic),
        ("invalid_6.0_wrong_byte_order.tif", "image/tiff", TiffFileMagic),
        ("invalid__binary_data.txt", "text/plain", TextFileMagic),
        ("invalid_1.0_no_closing_tag.xml", "text/xml", XmlFileMagic),
        ("invalid_1.0_no_doctype.xhtml", "application/xhtml+xml",
         XhtmlFileMagic),
        ("invalid_4.01_nodoctype.html", "text/html", HtmlFileMagic),
        ("invalid_5.0_nodoctype.html", "text/html", HtmlFileMagic),
        ("invalid_1.4_removed_xref.pdf", "application/pdf", PdfFileMagic),
        ("invalid_1.0_missing_field.arc", "application/x-internet-archive",
         ArcFileMagic),
        ("invalid__empty.doc", "application/msword", OfficeFileMagic),
        ("invalid__empty.txt", "text/plain", TextFileMagic),
    ])
def test_scraper_invalid(filename, mimetype, class_):
    """Test scraper"""
    result_dict = {
        'purpose': 'Test invalid file.',
        'stdout_part': '',
        'stderr_part': 'do not match'}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = class_(correct.filename, correct.mimetype,
                     True, correct.params)
    scraper.scrape_file()

    if class_ not in [HtmlFileMagic, XmlFileMagic, XhtmlFileMagic,
                      PdfFileMagic, ArcFileMagic]:
        correct.streams[0]['mimetype'] = 'application/octet-stream'
    if 'empty' in filename:
        correct.streams[0]['mimetype'] = 'inode/x-empty'

    if class_ not in [XmlFileMagic, XhtmlFileMagic, PdfFileMagic,
                      ArcFileMagic]:
        correct.version = None
        correct.streams[0]['version'] = None

    if class_ in [XhtmlFileMagic]:
        correct.streams[0]['stream_type'] = 'text'
    if class_ in [TextFileMagic]:
        correct.streams[0]['charset'] = None
    if class_ in [HtmlFileMagic, XmlFileMagic, XhtmlFileMagic]:
        correct.streams[0]['charset'] = 'UTF-8'

    if class_ in [HtmlFileMagic, XmlFileMagic, XhtmlFileMagic,
                  PdfFileMagic, ArcFileMagic]:
        correct.stdout_part = 'successfully'
        correct.stderr_part = ''
        correct.well_formed = True
        assert scraper.mimetype == correct.mimetype
    else:
        assert scraper.mimetype != correct.mimetype

    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == class_.__name__
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['mime', 'ver', 'class_'],
    [
        ('application/vnd.oasis.opendocument.text', '1.1', OfficeFileMagic),
        ('application/msword', '11.0', OfficeFileMagic),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml'
         '.document', '15.0', OfficeFileMagic),
        ('application/vnd.oasis.opendocument.presentation', '1.1',
         OfficeFileMagic),
        ('application/vnd.ms-powerpoint', '11.0', OfficeFileMagic),
        ('application/vnd.openxmlformats-officedocument.presentationml'
         '.presentation', '15.0', OfficeFileMagic),
        ('application/vnd.oasis.opendocument.spreadsheet', '1.1',
         OfficeFileMagic),
        ('application/vnd.ms-excel', '8.0', OfficeFileMagic),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml'
         '.sheet', '15.0', OfficeFileMagic),
        ('application/vnd.oasis.opendocument.graphics', '1.1',
         OfficeFileMagic),
        ('application/vnd.oasis.opendocument.formula', '1.0', OfficeFileMagic),
        ('image/png', '1.2', PngFileMagic),
        ('image/jpeg', '1.01', JpegFileMagic),
        ('image/jp2', '', Jp2FileMagic),
        ('image/tiff', '6.0', TiffFileMagic),
        ('text/plain', '', TextFileMagic),
        ('text/xml', '1.0', XmlFileMagic),
        ('application/xhtml+xml', '1.0', XhtmlFileMagic),
        ('text/html', '4.01', HtmlFileMagic),
        ('application/pdf', '1.4', PdfFileMagic),
        ('application/x-internet-archive', '1.0', ArcFileMagic),
    ]
)
def test_is_supported(mime, ver, class_):
    """Test is_Supported method"""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)
