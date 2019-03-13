"""
Tests for ImageMagick scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.wand import TiffWand, ImageWand

"""
Tests for DPX scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.dpx import Dpx


STREAM_VALID = {
    'bps_unit': None,
    'bps_value': '8',
    'byte_order': None,
    'colorspace': 'srgb',
    'height': '6',
    'index': 0,
    'samples_per_pixel': None,
    'stream_type': 'image',
    'width': '10'}

GIF_APPEND = {
    'bps_unit': None,
    'bps_value': '8',
    'byte_order': None,
    'colorspace': 'srgb',
    'compression': 'lzw',
    'height': '1',
    'index': 1,
    'mimetype': 'image/gif',
    'samples_per_pixel': None,
    'stream_type': 'image',
    'version': None,
    'width': '1'}

STREAM_INVALID = {
    'bps_unit': None,
    'bps_value': None,
    'byte_order': None,
    'colorspace': None,
    'compression': None,
    'height': None,
    'index': 0,
    'samples_per_pixel': None,
    'stream_type': 'image',
    'width': None}


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'mimetype', 'class_', 'compression'],
    [
        ('valid_6.0.tif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/tiff', TiffWand, 'zip'),
        ('valid_1.01.jpg', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/jpeg', ImageWand, 'jpeg'),
        ('valid.jp2', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/jp2', ImageWand, 'jpeg2000'),
        ('valid_1.2.png', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/png', ImageWand, 'zip'),
        ('valid_1987a.gif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/gif', ImageWand, 'lzw'),
        ('valid_1989a.gif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''},
         'image/gif', ImageWand, 'lzw')
    ]
)
def test_scraper_valid(filename, result_dict, mimetype, class_, compression):
    """Test scraper"""
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    correct.streams[0]['compression'] = compression
    correct.streams[0]['mimetype'] = mimetype
    correct.streams[0]['version'] = None
    if mimetype in ['image/tiff']:
        correct.streams[0]['byte_order'] = 'little endian'
    if mimetype in ['image/jp2']:
        correct.streams[0]['colorspace'] = 'rgb'
    if filename in ['valid_1989a.gif']:
        for index in range(1, 3):
            correct.streams[index] = GIF_APPEND.copy()
            correct.streams[index]['index'] = index

    correct.version = None
    scraper = class_(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == class_.__name__
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'mimetype', 'class_'],
    [
        ('invalid_6.0_payload_altered.tif', {
            'purpose': 'Test payload altered in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Failed to read directory at offset 182'},
         'image/tiff', TiffWand),
        ('invalid_6.0_wrong_byte_order.tif', {
            'purpose': 'Test wrong byte order in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Not a TIFF file, bad version number 10752'},
         'image/tiff', TiffWand),
        ('invalid__empty.tif', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Cannot read TIFF header.'},
         'image/tiff', TiffWand),
        ('invalid_1.01_data_changed.jpg', {
            'purpose': 'Test image data change in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Bogus marker length'},
         'image/jpeg', ImageWand),
        ('invalid_1.01_no_start_marker.jpg', {
            'purpose': 'Test start marker change in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'starts with 0xff 0xe0'},
         'image/jpeg', ImageWand),
        ('invalid__empty.jpg', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Empty input file'},
         'image/jpeg', ImageWand),
        ('invalid__data_missing.jp2', {
            'purpose': 'Test data missing file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'unable to decode image file'},
         'image/jp2', ImageWand),
        ('invalid__empty.jp2', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'unable to decode image file'},
         'image/jp2', ImageWand),
        ('invalid_1.2_no_IEND.png', {
            'purpose': 'Test without IEND.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'},
         'image/png', ImageWand),
        ('invalid_1.2_no_IHDR.png', {
            'purpose': 'Test without IHDR.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'},
         'image/png', ImageWand),
        ('invalid_1.2_wrong_CRC.png', {
            'purpose': 'Test wrong CRC.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'},
         'image/png', ImageWand),
        ('invalid_1.2_wrong_header.png', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'},
         'image/png', ImageWand),
        ('invalid__empty.png', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'},
         'image/png', ImageWand),
        ('invalid_1987a_broken_header.gif', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'},
         'image/gif', ImageWand),
        ('invalid_1987a_truncated.gif', {
            'purpose': 'Test truncated file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'},
         'image/gif', ImageWand),
        ('invalid_1989a_broken_header.gif', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'},
         'image/gif', ImageWand),
        ('invalid_1989a_truncated.gif', {
            'purpose': 'Test truncated file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'negative or zero image size'},
         'image/gif', ImageWand),
        ('invalid__empty.gif', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'},
         'image/gif', ImageWand)
    ]
)
def test_scraper_invalid(filename, result_dict, mimetype, class_):
    """Test scraper"""
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = class_(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['mimetype'] = mimetype
    correct.streams[0]['version'] = None
    correct.version = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == class_.__name__
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['mime', 'ver', 'class_'],
    [
        ('image/tiff', '6.0', TiffWand),
        ('image/jpeg', '1.01', ImageWand),
        ('image/jp2', '', ImageWand),
        ('image/png', '1.2', ImageWand),
        ('image/gif', '1987a', ImageWand),
    ]
)
def test_is_supported(mime, ver, class_):
    """Test is_Supported method"""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)
