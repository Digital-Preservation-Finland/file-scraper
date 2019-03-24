"""
Tests for Vnu scraper.
"""
import pytest
from file_scraper.scrapers.vnu import Vnu
from tests.common import parse_results


MIMETYPE = 'text/html'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_5.0.html', {
            'purpose': 'Test valid file.',
            'stdout_part': 'valid_5.0.html',
            'stderr_part': ''}),
        ('invalid_5.0_nodoctype.html', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': 'Start tag seen without seeing a doctype first.'}),
        ('invalid_5.0_illegal_tags.html', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': 'not allowed as child of element'}),
        ('invalid__empty.html', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': 'End of file seen without seeing a doctype first'}),
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Vnu(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()
    correct.version = '5.0'
    correct.streams[0]['version'] = '5.0'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Vnu'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check"""
    scraper = Vnu('valid_5.0.html', MIMETYPE, False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method"""
    mime = MIMETYPE
    ver = '5.0'
    assert Vnu.is_supported(mime, ver, True)
    assert Vnu.is_supported(mime, None, True)
    assert not Vnu.is_supported(mime, ver, False)
    assert not Vnu.is_supported(mime, 'foo', True)
    assert not Vnu.is_supported('foo', ver, True)
