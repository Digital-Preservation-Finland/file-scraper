"""
Tests for ImageMagick scraper.
"""
import os
import pytest
from file_scraper.scrapers.wand import TiffWand, ImageWand
from tests.scrapers.common import parse_results


STREAM_VALID = {
    'bps_unit': None,
    'bps_value': '8',
    'colorspace': 'srgb',
    'height': '6',
    'samples_per_pixel': None,
    'width': '10'}

GIF_APPEND = {
    'bps_unit': None,
    'bps_value': '8',
    'colorspace': 'srgb',
    'compression': 'lzw',
    'height': '1',
    'mimetype': 'image/gif',
    'samples_per_pixel': None,
    'stream_type': 'image',
    'version': None,
    'width': '1'}

STREAM_INVALID = {
    'bps_unit': None,
    'bps_value': None,
    'colorspace': None,
    'compression': None,
    'height': None,
    'samples_per_pixel': None,
    'width': None}


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_6.0.tif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_6.0_multiple_tiffs.tif', {
            'purpose': 'Test valid multiple tiff file.',
            'streams': {0: STREAM_VALID.copy(),
                        1: STREAM_VALID.copy(),
                        2: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid_6.0_payload_altered.tif', {
            'purpose': 'Test payload altered in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Failed to read directory at offset 182'}),
        ('invalid_6.0_wrong_byte_order.tif', {
            'purpose': 'Test wrong byte order in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Not a TIFF file, bad version number 10752'}),
        ('invalid__empty.tif', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Cannot read TIFF header.'})
    ]
)
def test_scraper_tif(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/tiff',
                            result_dict, True)
    if correct.well_formed:
        for index in range(0, len(correct.streams)):
            correct.streams[index]['compression'] = 'zip'
            correct.streams[index]['byte_order'] = 'little endian'
            correct.streams[index]['mimetype'] = \
                correct.streams[0]['mimetype']
            correct.streams[index]['stream_type'] = \
                correct.streams[0]['stream_type']
            correct.streams[index]['version'] = None
    else:
        correct.streams[0]['byte_order'] = None

    correct.version = None
    correct.streams[0]['version'] = None
    scraper = TiffWand(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'TiffWand'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.01.jpg', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid_1.01_data_changed.jpg', {
            'purpose': 'Test image data change in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Bogus marker length'}),
        ('invalid_1.01_no_start_marker.jpg', {
            'purpose': 'Test start marker change in file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'starts with 0xff 0xe0'}),
        ('invalid__empty.jpg', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'Empty input file'})
    ]
)
def test_scraper_jpg(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/jpeg',
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]['compression'] = 'jpeg'
    correct.streams[0]['version'] = None
    correct.version = None
    scraper = ImageWand(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ImageWand'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid.jp2', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid__data_missing.jp2', {
            'purpose': 'Test data missing file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'unable to decode image file'}),
        ('invalid__empty.jp2', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'unable to decode image file'})
    ]
)
def test_scraper_jp2(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/jp2',
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]['compression'] = 'jpeg2000'
        correct.streams[0]['colorspace'] = 'rgb'
    correct.streams[0]['version'] = None
    correct.version = None
    scraper = ImageWand(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ImageWand'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.2.png', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid_1.2_no_IEND.png', {
            'purpose': 'Test without IEND.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'}),
        ('invalid_1.2_no_IHDR.png', {
            'purpose': 'Test without IHDR.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'}),
        ('invalid_1.2_wrong_CRC.png', {
            'purpose': 'Test wrong CRC.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'}),
        ('invalid_1.2_wrong_header.png', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'}),
        ('invalid__empty.png', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'}),
    ]
)
def test_scraper_png(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/png',
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]['compression'] = 'zip'
    correct.streams[0]['version'] = None
    correct.version = None
    scraper = ImageWand(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ImageWand'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1987a.gif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_1989a.gif', {
            'purpose': 'Test valid file.',
            'streams': {0: STREAM_VALID.copy(),
                        1: GIF_APPEND.copy(),
                        2: GIF_APPEND.copy()},
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid_1987a_broken_header.gif', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'}),
        ('invalid_1987a_truncated.gif', {
            'purpose': 'Test truncated file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'corrupt image'}),
        ('invalid_1989a_broken_header.gif', {
            'purpose': 'Test invalid header.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'}),
        ('invalid_1989a_truncated.gif', {
            'purpose': 'Test truncated file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'negative or zero image size'}),
        ('invalid__empty.gif', {
            'purpose': 'Test empty file.',
            'streams': {0: STREAM_INVALID.copy()},
            'stdout_part': '',
            'stderr_part': 'improper image header'})
    ]
)
def test_scraper_gif(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/gif',
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]['compression'] = 'lzw'
    correct.streams[0]['version'] = None
    correct.version = None

    scraper = ImageWand(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ImageWand'
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
