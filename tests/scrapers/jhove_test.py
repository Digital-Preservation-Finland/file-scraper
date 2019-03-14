"""Test module for jhove.py"""
import os
import pytest

from dpres_scraper.scrapers.jhove import GifJHove, TiffJHove, PdfJHove, \
    Utf8JHove, JpegJHove, HtmlJHove, WavJHove
from tests.scrapers.common import parse_results


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'get_ver'],
    [
        ('valid_XXXXa.gif', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}, True),
        ('invalid_XXXXa_broken_header.gif', {
            'purpose': 'Test invalid header.',
            'stdout_part': '',
            'stderr_part': 'Invalid GIF header'}, False),
        ('invalid_XXXXa_truncated.gif', {
            'purpose': 'Test truncated file.',
            'stdout_part': '',
            'stderr_part': 'Unknown data block type'}, True),
        ('invalid__empty.gif', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Invalid GIF header'}, False)
    ]
)
def test_scraper_gif(filename, result_dict, get_ver):
    """Test scraper"""
    for version in ['1987', '1989']:
        filename = filename.replace('XXXX', version)
        correct = parse_results(filename, 'image/gif',
                                result_dict, True)
        scraper = GifJHove(correct.filename, correct.mimetype,
                           True, correct.params)
        scraper.scrape_file()
        if not get_ver:
            correct.version = None
            correct.streams[0]['version'] = None

        assert scraper.mimetype == correct.mimetype
        assert scraper.version == correct.version
        assert scraper.streams == correct.streams
        assert scraper.info['class'] == 'GifJHove'
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_6.0.tif', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}),
        ('invalid_6.0_payload_altered.tif', {
            'purpose': 'Test payload altered in file.',
            'stdout_part': '',
            'stderr_part': 'IFD offset not word-aligned'}),
        ('invalid_6.0_wrong_byte_order.tif', {
            'purpose': 'Test wrong byte order in file.',
            'stdout_part': '',
            'stderr_part': 'No TIFF magic number'}),
        ('invalid__empty.tif', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'File is too short'}),
    ]
)
def test_scraper_tiff(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/tiff',
                            result_dict, True)
    scraper = TiffJHove(correct.filename, correct.mimetype,
                        True, correct.params)
    scraper.scrape_file()
    correct.version = '6.0'
    correct.streams[0]['version'] = '6.0'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'TiffJHove'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid__utf8.txt', {
            'purpose': 'Test valid UTF-8 file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}),
        ('valid__ascii.txt', {
            'purpose': 'Test valid ASCII file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}),
        ('valid__iso8859.txt', {
            'purpose': 'Test valid ISO-8859 file, which is invalid.',
            'inverse': True,
            'stdout_part': '',
            'stderr_part': 'Not valid second byte of UTF-8 encoding'})
    ]
)
def test_scraper_utf8(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'text/plain',
                            result_dict, True)
    scraper = Utf8JHove(correct.filename, correct.mimetype,
                        True, correct.params)
    scraper.scrape_file()
    correct.mimetype = None
    correct.version = None
    correct.streams[0]['mimetype'] = None
    correct.streams[0]['version'] = None
    correct.streams[0]['charset'] = 'UTF-8'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Utf8JHove'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'version'],
    [
        ('valid_X.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}, 'X'),
        ('invalid_X_payload_altered.pdf', {
            'purpose': 'Test payload altered file.',
            'stdout_part': '',
            'stderr_part': 'Invalid object definition'}, None),
        ('invalid_X_removed_xref.pdf', {
            'purpose': 'Test xref change.',
            'stdout_part': '',
            'stderr_part': 'Improperly nested dictionary delimiters'}, None),
        ('invalid_X_wrong_version.pdf', {
            'purpose': 'Test invalid version.',
            'stdout_part': '',
            'stderr_part': 'Version 1.0 is not supported.'}, '1.0')
    ]
)
def test_scraper_pdf(filename, result_dict, version):
    """Test scraper"""
    for ver in ['1.2', '1.3', '1.4', '1.5', '1.6', 'A-1a']:
        filename = filename.replace('X', ver)
        correct = parse_results(filename, 'application/pdf',
                                result_dict, True)
        scraper = PdfJHove(correct.filename, correct.mimetype,
                           True, correct.params)
        scraper.scrape_file()
        if version in [None, '1.0']:
            correct.version = version
            correct.streams[0]['version'] = version

        assert scraper.mimetype == correct.mimetype
        assert scraper.version == correct.version
        assert scraper.streams == correct.streams
        assert scraper.info['class'] == 'PdfJHove'
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.01.jpg', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}),
        ('invalid_1.01_data_changed.jpg', {
            'purpose': 'Test image data change in file.',
            'stdout_part': '',
            'stderr_part': 'Unexpected end of file'}),
        ('invalid_1.01_no_start_marker.jpg', {
            'purpose': 'Test start marker change in file.',
            'stdout_part': '',
            'stderr_part': 'Invalid JPEG header'}),
        ('invalid__empty.jpg', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Invalid JPEG header'})
    ]
)
def test_scraper_jpeg(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'image/jpeg',
                            result_dict, True)
    scraper = JpegJHove(correct.filename, correct.mimetype,
                        True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'JpegJHove'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'mimetype', 'charset', 'version'],
    [
        ('valid_4.01.html', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''},
         'text/html', None, '4.01'),
        ('valid_1.0.xhtml', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''},
         'application/xhtml+xml', 'UTF-8', '1.0'),
        ('valid_5.0.html', {
            'purpose': 'Test valid file, which is invalid for this scraper.',
            'inverse': True,
            'stdout_part': '',
            'stderr_part': 'Unrecognized or missing DOCTYPE declaration'},
         'text/html', None, None),
        ('invalid_4.01_illegal_tags.html', {
            'purpose': 'Test illegal tag.',
            'stdout_part': '',
            'stderr_part': 'Unknown tag'},
         'text/html', None, '4.01'),
        ('invalid_4.01_nodoctype.html', {
            'purpose': 'Test without doctype.',
            'stdout_part': '',
            'stderr_part': 'Unrecognized or missing DOCTYPE declaration'},
         'text/html', None, None),
        ('invalid__empty.html', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Document is empty'},
         'text/html', None, None),
        ('invalid_1.0_illegal_tags.xhtml', {
            'purpose': 'Test illegal tag.',
            'stdout_part': '',
            'stderr_part': 'must be declared.'},
         'application/xhtml+xml', 'UTF-8', '1.0'),
        ('invalid_1.0_missing_closing_tag.xhtml', {
            'purpose': 'Test missing closing tag.',
            'stdout_part': '',
            'stderr_part': 'must be terminated by the matching end-tag'},
         'application/xhtml+xml', None, None),
        ('invalid_1.0_no_doctype.xhtml', {
            'purpose': 'Test without doctype.',
            'stdout_part': '',
            'stderr_part': 'Cannot find the declaration of element'},
         'application/xhtml+xml', 'UTF-8', '1.0'),
        ('invalid__empty.xhtml', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Document is empty'},
         'application/xhtml+xml', None, None)
    ]
)
def test_scraper_html(filename, result_dict, mimetype, charset, version):
    """Test scraper"""
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = HtmlJHove(correct.filename, correct.mimetype,
                        True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['charset'] = charset
    correct.streams[0]['stream_type'] = 'text'
    correct.version = version
    correct.streams[0]['version'] = version
    if 'invalid__empty.xhtml' in filename:
        correct.mimetype = 'text/html'
        correct.streams[0]['mimetype'] = 'text/html'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'HtmlJHove'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'version', 'others'],
    [
        ('valid__wav.wav', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''},
         None, True),
        ('valid_2_bwf.wav', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''},
         '2', True),
        ('invalid_2_bwf_data_bytes_missing.wav', {
            'purpose': 'Test data bytes missing.',
            'stdout_part': '',
            'stderr_part': 'Invalid character in Chunk ID'},
         None, True),
        ('invalid_2_bwf_RIFF_edited.wav', {
            'purpose': 'Test edited RIFF.',
            'stdout_part': '',
            'stderr_part': 'Invalid chunk size'},
         None, False),
        ('invalid__empty.wav', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Unexpected end of file'},
         None, False),
        ('invalid__data_bytes_missing.wav', {
            'purpose': 'Test data bytes missing.',
            'stdout_part': '',
            'stderr_part': 'Bytes missing'},
         None, True),
        ('invalid__RIFF_edited.wav', {
            'purpose': 'Test edited RIFF.',
            'stdout_part': '',
            'stderr_part': 'Invalid chunk size'},
         None, False)
    ]
)
def test_scraper_wav(filename, result_dict, version, others):
    """Test scraper"""
    correct = parse_results(filename, 'audio/x-wav',
                            result_dict, True)
    scraper = WavJHove(correct.filename, correct.mimetype,
                       True, correct.params)
    scraper.scrape_file()
    if others:
        correct.streams[0]['bits_per_sample'] = '8'
        correct.streams[0]['sampling_frequency'] = '44.1'
        correct.streams[0]['num_channels'] = '2'
    else:
        correct.streams[0]['bits_per_sample'] = None
        correct.streams[0]['sampling_frequency'] = None
        correct.streams[0]['num_channels'] = None
    if 'empty' in filename:
        correct.mimetype = None
        correct.streams[0]['mimetype'] = None
    correct.version = version
    correct.streams[0]['version'] = version

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'WavJHove'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['mime', 'ver', 'class_'],
    [
        ('image/gif', '1989a', GifJHove),
        ('image/tiff', '6.0', TiffJHove),
        ('image/jpeg', '1.01', JpegJHove),
        ('audio/x-wav', '2', WavJHove)
    ]
)
def test_is_supported_allow(mime, ver, class_):
    """Test is_Supported method"""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)

@pytest.mark.parametrize(
    ['mime', 'ver', 'class_'],
    [
        ('application/pdf', '1.4', PdfJHove),
        ('text/html', '4.01', HtmlJHove),
        ('application/xhtml+xml', '1.0', HtmlJHove),
    ]
)
def test_is_supported_deny(mime, ver, class_):
    """Test is_Supported method"""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)

@pytest.mark.parametrize(
    ['mime', 'ver', 'class_'],
    [
        ('text/plain', '', Utf8JHove)
    ]
)
def test_is_supported_utf8(mime, ver, class_):
    """Test is_Supported method"""
    assert not class_.is_supported(mime, ver, True)
    assert not class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, 'foo', True)
    assert not class_.is_supported('foo', ver, True)
