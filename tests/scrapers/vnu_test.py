"""
Tests for Vnu scraper.

This module tests that:
    - MIME type, version, streams and well-formedness are scraped correctly for
      html 5 files when well-formedness is checked.
    - For well-formed file, scraper messages contain "valid_5.0.html".
    - For file without doctype, scraper errors contain  "Start tag seen
      without seeing a doctype first."
    - For file with illegal tags in it, scraper errors contain "not allowed as
      child of element".
    - For empty file, scraper errors contain "End of file seen without seeing
      a doctype first".
    - When well-formedness is not checked, scraper messages contain "Skipping
      scraper" and well_formed is None.
    - When well-formedness is checked, MIME type text/html versions 5.0 and
      None are supported. When well-formedness is not checked, this combination
      is not supported.
    - A made up MIME type or version is not supported.
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
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Vnu(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()
    correct.version = '5.0'
    correct.streams[0]['version'] = '5.0'

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = Vnu('tests/data/text_html/valid_5.0.html', MIMETYPE, False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = '5.0'
    assert Vnu.is_supported(mime, ver, True)
    assert Vnu.is_supported(mime, None, True)
    assert not Vnu.is_supported(mime, ver, False)
    assert not Vnu.is_supported(mime, 'foo', True)
    assert not Vnu.is_supported('foo', ver, True)
