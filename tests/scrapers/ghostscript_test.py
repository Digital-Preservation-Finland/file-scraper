"""
Test for pdf 1.7 ghostscript scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.ghostscript import GhostScript


MIMETYPE = 'application/pdf'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.7.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}),
        ('valid_A-2b.pdf', {
            'purpose': 'Test valid PDF/A file.',
            'stdout_part': '',
            'stderr_part': ''})
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = GhostScript(correct.filename, correct.mimetype,
                          True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['version'] = None  # Scraper does not know version

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == None  # The scraper does not know version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'GhostScript'
    if scraper.well_formed:
        assert 'Error' not in scraper.messages()
    else:
        assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = MIMETYPE
    ver = '1.7'
    assert GhostScript.is_supported(mime, ver, True)
    assert GhostScript.is_supported(mime, None, True)
    assert not GhostScript.is_supported(mime, ver, False)
    assert not GhostScript.is_supported(mime, 'foo', True)
    assert not GhostScript.is_supported('foo', ver, True)
