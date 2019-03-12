"""Test the dpres_scraper.scrapers.warctools module"""
import os
import pytest
from dpres_scraper.scrapers.warctools import GzipWarctools, WarcWarctools, \
    ArcWarctools
from tests.scrapers.common import parse_results


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.0_.warc.gz', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('invalid_1.0_distance_code_error.warc.gz', {
            'purpose': 'Test distance code error.',
            'stdout_part': '',
            'stderr_part': 'invalid distance code'}),
        ('invalid_1.0_no_gzip.gz', {
            'purpose': 'Test no gzip.',
            'stdout_part': '',
            'stderr_part': 'Not a gzipped file'}),
        ('invalid_1.0_crc_error.gz', {
            'purpose': 'Test CRC failure.',
            'stdout_part': '',
            'stderr_part': 'CRC check failed'}),
    ]
)
def test_gzip_scraper(filename, result_dict):
    """Test scraper"""
    if 'warc' in filename:
        mime = 'application/warc'
        classname = 'WarcWarctools'
    else:
        mime = 'application/x-internet-archive'
        classname = 'ArcWarctools'
    correct = parse_results(filename, mime,
                            result_dict, True)
    scraper = GzipWarctools(correct.filename, 'application/gzip',
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == classname
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_0.17.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('valid_0.18.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('valid_1.0.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('valid_1.0_.warc.gz', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('invalid_0.17_incorrect newline_in header.warc', {
            'purpose': 'Test incorrect newline.',
            'stdout_part': '',
            'stderr_part': 'incorrect newline in header'}),
        ('invalid_1.0_distance_code_error.warc.gz', {
            'purpose': 'Test distance code error.',
            'stdout_part': '',
            'stderr_part': 'invalid distance code'}),
        ('invalid_0.18_header_error.warc', {
            'purpose': 'Test header error.',
            'stdout_part': '',
            'stderr_part': 'invalid header'})
    ]
)
def test_warc_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'application/warc',
                            result_dict, True)
    scraper = WarcWarctools(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'WarcWarctools'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.0.arc', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''})
    ]
)
def test_arc_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'application/x-internet-archive',
                            result_dict, True)
    scraper = ArcWarctools(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['version'] = None
    assert scraper.mimetype == correct.mimetype
    assert scraper.version == None  # Scraper can not solve version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ArcWarctools'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_gzip_is_supported():
    """Test is_Supported method"""
    mime = 'application/gzip'
    ver = ''
    assert GzipWarctools.is_supported(mime, ver, True)
    assert GzipWarctools.is_supported(mime, None, True)
    assert not GzipWarctools.is_supported(mime, ver, False)
    assert GzipWarctools.is_supported(mime, 'foo', True)
    assert not GzipWarctools.is_supported('foo', ver, True)


def test_warc_is_supported():
    """Test is_Supported method"""
    mime = 'application/warc'
    ver = ''
    assert WarcWarctools.is_supported(mime, ver, True)
    assert WarcWarctools.is_supported(mime, None, True)
    assert not WarcWarctools.is_supported(mime, ver, False)
    assert WarcWarctools.is_supported(mime, 'foo', True)
    assert not WarcWarctools.is_supported('foo', ver, True)


def test_arc_is_supported():
    """Test is_Supported method"""
    mime = 'application/x-internet-archive'
    ver = ''
    assert ArcWarctools.is_supported(mime, ver, True)
    assert ArcWarctools.is_supported(mime, None, True)
    assert not ArcWarctools.is_supported(mime, ver, False)
    assert ArcWarctools.is_supported(mime, 'foo', True)
    assert not ArcWarctools.is_supported('foo', ver, True)
