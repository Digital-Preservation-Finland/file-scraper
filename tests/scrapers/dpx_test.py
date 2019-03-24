"""
Tests for DPX scraper.
"""
import pytest
from tests.common import parse_results
from file_scraper.scrapers.dpx import Dpx


MIMETYPE = 'image/x-dpx'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_2.0.dpx', {
            'purpose': 'Test valid file.',
            'stdout_part': 'is valid',
            'stderr_part': ''}),
        ('invalid_2.0_empty_file.dpx', {
            'purpose': 'Test empty file.',
            'stdout_part': '',
            'stderr_part': 'Truncated file'}),
        ('invalid_2.0_file_size_error.dpx', {
            'purpose': 'Test file size error.',
            'stdout_part': '',
            'stderr_part': 'Different file sizes'}),
        ('invalid_2.0_missing_data.dpx', {
            'purpose': 'Test missing data.',
            'stdout_part': '',
            'stderr_part': 'Different file sizes'}),
        ('invalid_2.0_wrong_endian.dpx', {
            'purpose': 'Test wrong endian.',
            'stdout_part': '',
            'stderr_part': 'is more than file size'}),
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Dpx(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Dpx'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check"""
    scraper = Dpx('tests/data/image_x-dpx/valid_2.0.dpx', MIMETYPE, False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method"""
    mime = MIMETYPE
    ver = '2.0'
    assert Dpx.is_supported(mime, ver, True)
    assert Dpx.is_supported(mime, None, True)
    assert not Dpx.is_supported(mime, ver, False)
    assert not Dpx.is_supported(mime, 'foo', True)
    assert not Dpx.is_supported('foo', ver, True)
