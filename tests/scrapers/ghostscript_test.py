"""
Test for pdf 1.7 ghostscript scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from file_scraper.scrapers.ghostscript import GhostScript


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_X.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'Well-Formed and valid',
            'stderr_part': ''}),
        ('invalid_X_payload_altered.pdf', {
            'purpose': 'Test payload altered file.',
            'stdout_part': '',
            'stderr_part': 'An error occurred while reading an XREF table.'}),
        ('invalid_X_removed_xref.pdf', {
            'purpose': 'Test xref change.',
            'stdout_part': '',
            'stderr_part': 'An error occurred while reading an XREF table.'}),
    ]
)
def test_scraper_pdf(filename, result_dict):
    """Test scraper"""
    for ver in ['1.7', 'A-1a', 'A-2b', 'A-3b']:
        filename = filename.replace('X', ver)
        correct = parse_results(filename, 'application/pdf',
                                result_dict, True)
        scraper = GhostScript(correct.filename, correct.mimetype,
                           True, correct.params)
        scraper.scrape_file()
        # Ghostscript cannot handle version
        correct.version = None
        correct.streams[0]['version'] = None

        assert scraper.mimetype == correct.mimetype
        assert scraper.version == correct.version
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
    mime = 'application/pdf'
    ver = '1.7'
    assert GhostScript.is_supported(mime, ver, True)
    assert GhostScript.is_supported(mime, None, True)
    assert not GhostScript.is_supported(mime, ver, False)
    assert not GhostScript.is_supported(mime, 'foo', True)
    assert not GhostScript.is_supported('foo', ver, True)
