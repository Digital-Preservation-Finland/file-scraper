"""Test the dpres_scraper.scrapers.warctools module"""
import os

import pytest

# Module to test
from dpres_scraper.scrapers.warctools import WarcWarctools, ArcWarctools


@pytest.mark.parametrize(
    'filename',
    ['valid_0.18.warc',
     'valid_0.17.warc',
     'valid_1.0.warc.gz',
     'valid_1.0.warc'])
def test_scrape_valid_warc(filename):

    filepath = os.path.join("tests/data/application_warc", filename)
    scraper = WarcWarctools(filepath, 'application/warc')
    scraper.scrape_file()
    assert scraper.well_formed, scraper.errors()


@pytest.mark.parametrize(
    ['filename', 'error'],
    [('invalid_0.17_incorrect newline_in header.warc', 'incorrect newline in header'),
     ('invalid_1.0_distance_code_error.warc.gz', 'invalid distance code'),
     ('invalid_0.18_header_error.warc', 'invalid header')])
@pytest.mark.timeout(5)
def test_scrape_invalid_warc(filename, error):

    filepath = os.path.join("tests/data/application_warc", filename)
    scraper = WarcWarctools(filepath, 'application/warc')
    scraper.scrape_file()

    assert not scraper.well_formed
    assert error in scraper.errors()


@pytest.mark.parametrize(
    'filename',
    ['valid_1.0.arc.gz',
     'valid_1.0.arc'])
def test_scrape_valid_arc(filename):

    filepath = os.path.join("tests/data/application_x-internet-archive",
                            filename)
    scraper = ArcWarctools(filepath, 'application/x-internet-archive')
    scraper.scrape_file()

    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'error'],
    [('invalid_1.0_no_gzip.gz', 'Not a gzipped file'),
     ('invalid_1.0_crc_error.gz', 'CRC check failed')])
def test_scrape_invalid_arc(filename, error):

    filepath = os.path.join("tests/data/application_x-internet-archive",
                            filename)
    scraper = ArcWarctools(filepath, 'application/x-internet-archive')
    scraper.scrape_file()

    assert not scraper.well_formed
    assert error in scraper.errors()
