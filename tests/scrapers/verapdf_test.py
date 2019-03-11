"""
Tests for VeraPDF scraper for PDF/A files.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.verapdf import VeraPdf


MIMETYPE = 'application/pdf'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_A-1a.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'PDF file is compliant with Validation Profile '
                           'requirements.',
            'stderr_part': ''}),
        ('valid_A-2b.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'PDF file is compliant with Validation Profile '
                           'requirements.',
            'stderr_part': ''}),
        ('valid_A-3b.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'PDF file is compliant with Validation Profile '
                           'requirements.',
            'stderr_part': ''}),
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = VeraPdf(correct.filename, correct.mimetype,
                      True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'VeraPdf'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = MIMETYPE
    ver = 'A-1b'
    assert VeraPdf.is_supported(mime, ver, True)
    assert VeraPdf.is_supported(mime, None, True)
    assert not VeraPdf.is_supported(mime, ver, False)
    assert not VeraPdf.is_supported(mime, 'foo', True)
    assert not VeraPdf.is_supported('foo', ver, True)
