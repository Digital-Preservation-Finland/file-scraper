"""
Tests for PSPP scraper.
"""
import pytest
from tests.common import parse_results
from file_scraper.scrapers.pspp import Pspp


MIMETYPE = 'application/x-spss-por'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid.por', {
            'purpose': 'Test valid file.',
            'stdout_part': 'File conversion was succesful.',
            'stderr_part': ''}),
        ('invalid__wrong_spss_format.sav', {
            'purpose': 'Test wrong format.',
            'stdout_part': '',
            'stderr_part': 'File is not SPSS Portable format.'}),
        ('invalid__header_corrupted.por', {
            'purpose': 'Test corrupted header.',
            'stdout_part': '',
            'stderr_part': 'Bad date string length'}),
        ('invalid__truncated.por', {
            'purpose': 'Test truncated file.',
            'stdout_part': '',
            'stderr_part': 'unexpected end of file'})
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Pspp(correct.filename, correct.mimetype,
                   True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Pspp'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check"""
    scraper = Pspp('valid.por', MIMETYPE, False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method"""
    mime = MIMETYPE
    ver = ''
    assert Pspp.is_supported(mime, ver, True)
    assert Pspp.is_supported(mime, None, True)
    assert not Pspp.is_supported(mime, ver, False)
    assert Pspp.is_supported(mime, 'foo', True)
    assert not Pspp.is_supported('foo', ver, True)
