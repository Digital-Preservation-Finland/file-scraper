"""Test the dpres_scraper.scrapers.pil module"""
import os
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.pil import TiffPil, ImagePil, JpegPil

BASEPATH = "tests/data"
DEFAULTSTREAMS = {0: {'byte_order': None, 'bps_unit': 'integer',
                      'bps_value': None, 'index': 0, 'colorspace': None,
                      'stream_type': 'image', 'height': '6',
                      'width': '10', 'version': None,
                      'samples_per_pixel': '3',
                      'compression': None}}

@pytest.mark.parametrize(
    ['filename', 'result_dict', 'mimetype', "scraper_class"],
    [
        ('valid_1.2.png', {
            'purpose': 'Test valid png.',
            'stdout_part': 'file was scraped successfully',
            'stderr_part': '',
            'streams': DEFAULTSTREAMS.copy()},
         'image/png',
         ImagePil),
        ('valid_6.0.tif', {
            'purpose': 'Test valid tiff.',
            'stdout_part': 'file was scraped successfully',
            'stderr_part': '',
            'streams': DEFAULTSTREAMS.copy()},
         'image/tiff',
         TiffPil),
        ('valid_1.01.jpg', {
            'purpose': 'Test valid jpeg.',
            'stdout_part': 'file was scraped successfully',
            'stderr_part': '',
            'streams': DEFAULTSTREAMS.copy()},
         'image/jpeg',
         JpegPil)
    ]
)
def test_scraper(filename, result_dict, mimetype, scraper_class):
    """Test scraper"""
    correct = parse_results(filename,
                            mimetype, result_dict, True)
    correct.streams[0]['mimetype'] = correct.mimetype

    scraper = scraper_class(correct.filename, correct.mimetype,
                            True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version is None
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == scraper_class.__name__
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

@pytest.mark.parametrize(
    ['scraper_class', 'mimetype', 'supported'],
    [
        (TiffPil, "image/tiff", True),
        (TiffPil, "image/png", False),
        (ImagePil, "image/png", True),
        (ImagePil, "image/jp2", True),
        (ImagePil, "image/gif", True),
        (ImagePil, "image/tiff", False),
        (JpegPil, "image/jpeg", True),
        (JpegPil, "image/gif", False)
    ]
)
def test_is_supported(scraper_class, mimetype, supported):
    """Test is_Supported method"""

    if supported:
        error_msg = scraper_class.__name__ + " should support " + mimetype
    else:
        error_msg = scraper_class.__name__ + " should not support " + mimetype

    assert scraper_class.is_supported(mimetype, None) == supported, error_msg
