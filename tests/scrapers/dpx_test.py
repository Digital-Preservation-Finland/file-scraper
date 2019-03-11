"""
Tests for DPX scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.dpx import Dpx


SUPPORT_MIME = 'image/x-dpx'


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
            'stderr_part': 'Truncated file'})
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, SUPPORT_MIME,
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

def test_is_supported():
    """Test is_Supported method"""
    mime = SUPPORT_MIME
    ver = '2.0'
    assert Dpx.is_supported(mime, ver, True)
    assert Dpx.is_supported(mime, None, True)
    assert not Dpx.is_supported(mime, ver, False)
    assert not Dpx.is_supported(mime, 'foo', True)
    assert not Dpx.is_supported('foo', ver, True)
