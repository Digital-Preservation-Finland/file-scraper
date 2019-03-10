"""
Test for pdf 1.7 ghostscript scraper.
"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.ghostscript import GhostScript


SUPPORT_MIME = 'application/pdf'


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'validation'],
    [
        ('valid_1.7.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}, True),
        ('invalid_1.7_corrupted.pdf', {
            'purpose': 'Test corrupted file.',
            'stdout_part': 'Error: /undefined in obj',
            'stderr_part': 'Unrecoverable error, exit code 1'}, True),
        ('valid_A-2b.pdf', {
            'purpose': 'Test valid PDF/A file.',
            'stdout_part': '',
            'stderr_part': ''}, True),
        ('invalid_A-2b_valid_as_plain_pdf.pdf', {
            'purpose': 'Test invalid A-1b but valid as plain PDF',
            'inverse': True,
            'stdout_part': 'Error: /undefined in obj',
            'stderr_part': 'Truncated file'}, True),
        ('invalid_A-2b_xref_error.pdf', {
            'purpose': 'Test invalid as PDF and PDF/A.',
            'stdout_part': '',
            'stderr_part': 'An error occurred while reading an XREF table.'},
         True),
        ('valid_1.7.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': '',
            'stderr_part': ''}, False)
    ]
)
def test_scrape_files(filename, result_dict, validation):
    """Test scraper"""
    correct = parse_results(filename, SUPPORT_MIME,
                            result_dict, validation)
    scraper = GhostScript(correct.filename, correct.mimetype,
                          validation, correct.params)
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
    mime = SUPPORT_MIME
    ver = '1.7'
    assert GhostScript.is_supported(mime, ver, True)
    assert GhostScript.is_supported(mime, None, True)
    assert not GhostScript.is_supported(mime, ver, False)
    assert not GhostScript.is_supported(mime, 'foo', True)
    assert not GhostScript.is_supported('foo', ver, True)
