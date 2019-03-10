"""
Tests for DPX scraper.
"""
import pytest
from tests.scrapers.common import iter_results
from dpres_scraper.scrapers.dpx import Dpx


RESULT_DICT = {
    'valid_2.0.dpx': {
        'purpose': 'Test valid file.',
        'stdout_part': 'is valid',
        'stderr_part': ''},
    'invalid_2.0_empty_file.dpx': {
        'purpose': 'Test empty file.',
        'stdout_part': '',
        'stderr_part': 'Truncated file'}
    }
SUPPORT_MIME = ['image/x-dpx']

@pytest.mark.parametrize(
    'validation', [True, False]
)
def test_scrape_files(validation):
    """Test scraper"""
    for correct in iter_results(
            SUPPORT_MIME, RESULT_DICT, validation):
        scraper = Dpx(correct.filename, correct.mimetype,
                      validation, correct.params)
        scraper.scrape_file()

        assert scraper.mimetype == correct.mimetype
        assert scraper.version == correct.version
        assert scraper.streams == correct.streams
        assert scraper.info['class'] == 'Dpx'
        assert correct.stdout_part in scraper.info['messages']
        assert correct.stderr_part in scraper.info['errors']
        assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = SUPPORT_MIME[0]
    ver = '2.0'
    assert Dpx.is_supported(mime, ver, True)
    assert Dpx.is_supported(mime, None, True)
    assert not Dpx.is_supported(mime, ver, False)
    assert not Dpx.is_supported(mime, 'foo', True)
    assert not Dpx.is_supported('foo', ver, True)
