"""
Tests for PSPP scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.pspp import Pspp


SUPPORT_MIME = 'application/x-spss-por'


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'validation'],
    [
        ('valid.por', {
            'purpose': 'Test valid file.',
            'stdout_part': 'File conversion was succesful.',
            'stderr_part': ''}, True),
        ('invalid__wrong_spss_format.sav', {
            'purpose': 'Test wrong format.',
            'stdout_part': '',
            'stderr_part': 'File is not SPSS Portable format.'}, True)
    ]
)
def test_scraper(filename, result_dict, validation):
    """Test scraper"""
    correct = parse_results(filename, SUPPORT_MIME,
                            result_dict, validation)
    scraper = Pspp(correct.filename, correct.mimetype,
                   validation, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Pspp'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = SUPPORT_MIME
    ver = ''
    assert Pspp.is_supported(mime, ver, True)
    assert Pspp.is_supported(mime, None, True)
    assert not Pspp.is_supported(mime, ver, False)
    assert Pspp.is_supported(mime, 'foo', True)
    assert not Pspp.is_supported('foo', ver, True)
