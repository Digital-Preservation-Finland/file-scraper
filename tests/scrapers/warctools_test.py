"""Test the dpres_scraper.scrapers.warctools module"""
import os

import pytest

# Module to test
from dpres_scraper.scrapers.warctools import WarcWarctools, ArcWarctools


@pytest.mark.parametrize(
    'filename',
    ['warc_0_18/warc.0.18.warc',
     'warc_0_17/valid.warc',
     'warc_1_0/valid.warc.gz',
     'warc_1_0/valid_no_compress.warc'])
def test_scrape_valid_warc(filename):

    filepath = os.path.join("tests/data/binary", filename)
    scraper = WarcWarctools(filepath, 'application/warc')
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'version', 'error'],
    [('warc_0_17/invalid.warc', '0.17', 'incorrect newline in header'),
     ('warc_0_17/valid.warc', '666.66', 'version check error'),
     ('warc_1_0/invalid.warc.gz', '1.0', 'invalid distance code'),
     ('warc_0_18/invalid_warc.0.18.warc', '0.18', 'invalid header')])
@pytest.mark.timeout(5)
def test_scrape_invalid_warc(filename, version, error):

    filepath = os.path.join("tests/data/binary", filename)
    scraper = WarcWarctools(filepath, 'application/warc')
    scraper.scrape_file()

    assert not scraper.well_formed
    assert error in scraper.errors()


@pytest.mark.parametrize(
    'filename',
    ['arc/valid_arc.gz',
     'arc/valid_arc_no_compress'])
def test_scrape_valid_arc(filename):

    filepath = os.path.join("tests/data/binary", filename)
    scraper = ArcWarctools(filepath, 'application/x-internet-archive')
    scraper.scrape_file()

    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'version', 'error'],
    [('arc/invalid_arc.gz', '1.0', 'Not a gzipped file'),
     ('arc/invalid_arc_crc.gz', '1.0', 'CRC check failed')])
def test_scrape_invalid_arc(filename, version, error):

    filepath = os.path.join("tests/data/binary", filename)
    scraper = ArcWarctools(filepath, 'application/x-internet-archive')
    scraper.scrape_file()

    assert not scraper.well_formed
    assert error in scraper.errors()
