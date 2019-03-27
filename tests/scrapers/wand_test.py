"""
Tests for ImageMagick scraper.

This module tests that:
    - MIME type, version, streams and well-formedness are scraped correctly for
      tiff files.
        - For valid files containing one or more images, scraper messages
          contain "successfully".
        - For file where payload has been altered, scraper errors contain
          "Failed to read directory at offset 182".
        - For file with wrong byte order reported in the header, scraper errors
          contain "Not a TIFF file, bad version number 10752".
        - For an empty file, scraper errors contain "Cannot read TIFF header."
    - MIME type, version, streams and well-formedness are scraped correctly for
      jpeg files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with altered payload, scraper errors contain "Bogus marker
          length".
        - For file without start marker, scraper errors contain "starts with
          0xff 0xe0".
        - For empty file, scraper errors contain "Empty input file".
    - MIME type, version, streams and well-formedness are scraped correctly for
      jp2 files.
        - For well-formed files, scraper messages contain "successfully".
        - For an empty file or a file with missing data, scraper errors
          contain "unable to decode image file".
    - MIME type, version, streams and well-formedness are scraped correctly for
      png files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with missing IEND or IHDR chunk or wrong CRC, scraper
          errors contain "corrupt image".
        - For file with invalid header, scraper errors contain "improper
          image header".
        - For empty file, scraper errors contain "improper image header".
    - MIME type, version, streams and well-formedness are scraped correctly for
      gif files.
        - For well-formed files with one or more images, scraper messages
          contain "successfully".
        - For images with broken header, scraper errors contains "improper
          image header".
        - For truncated version 1987a file, scraper errors contains "corrupt
          image".
        -For truncated version 1989a file, scraper errors contains "negative
         or zero image size".
        - For empty file, scraper errors contains "imporoper image header".
    - When well-formedness is not checked, scraper messages contains "Skipping
      scraper" and well_formed is None.
    - With or without well-formedness check, the following MIME type and
      version pairs are supported:
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - image/jp2, ''
        - image/png, 1.2
        - image/gif, 1987a
    - All these MIME types are also supported when None or a made up version
      is given as the version.
    - A made up MIME type is not supported.

"""
import pytest
from file_scraper.scrapers.wand import TiffWand, ImageWand
from tests.common import parse_results


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
            'stderr_part': 'improper image header'})
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


def test_no_wellformed():
    """Test scraper without well-formed check"""
    scraper = ImageWand('tests/data/image_tiff/valid_6.0.tif',
                        'image/tiff', False)
    scraper.scrape_file()
    assert 'Skipping scraper' not in scraper.messages()
    assert scraper.well_formed is None


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
    """Test is_supported method"""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)
