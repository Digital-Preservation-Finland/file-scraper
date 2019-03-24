"""
Tests for VeraPDF scraper for PDF/A files.
"""
import pytest
from tests.common import parse_results
from file_scraper.scrapers.verapdf import VeraPdf


MIMETYPE = 'application/pdf'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_X.pdf', {
            'purpose': 'Test valid file.',
            'stdout_part': 'PDF file is compliant with Validation Profile '
                           'requirements.',
            'stderr_part': ''}),
        ('invalid_X_payload_altered.pdf', {
            'purpose': 'Test payload altered file.',
            'stdout_part': '',
            'stderr_part': 'can not locate xref table'}),
        ('invalid_X_removed_xref.pdf', {
            'purpose': 'Test xref change.',
            'stdout_part': '',
            'stderr_part': 'In a cross reference subsection header'}),
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    for ver in ['A-1a', 'A-2b', 'A-3b']:
        filename = filename.replace('X', ver)
        correct = parse_results(filename, MIMETYPE,
                                result_dict, True)
        scraper = VeraPdf(correct.filename, correct.mimetype,
                          True, correct.params)
        scraper.scrape_file()

        if not correct.well_formed:
            correct.version = None
            correct.streams[0]['version'] = None

        assert scraper.mimetype == correct.mimetype
        assert scraper.version == correct.version
        assert scraper.streams == correct.streams
        assert scraper.info['class'] == 'VeraPdf'
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.7.pdf', {
            'purpose': 'Test valid PDF 1.7, but not valid PDF/A.',
            'inverse': True,
            'stdout_part': '',
            'stderr_part': 'is not compliant with Validation Profile'}),
        ('valid_1.4.pdf', {
            'purpose': 'Test valid PDF 1.4, but not valid PDF/A.',
            'inverse': True,
            'stdout_part': '',
            'stderr_part': 'is not compliant with Validation Profile'}),
    ]
)
def test_scraper_invalid_pdfa(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = VeraPdf(correct.filename, correct.mimetype,
                      True, correct.params)
    scraper.scrape_file()

    correct.version = None
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'VeraPdf'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_is_supported():
    """Test is_supported method"""
    mime = MIMETYPE
    ver = 'A-1b'
    assert VeraPdf.is_supported(mime, ver, True)
    assert VeraPdf.is_supported(mime, None, True)
    assert not VeraPdf.is_supported(mime, ver, False)
    assert not VeraPdf.is_supported(mime, 'foo', True)
    assert not VeraPdf.is_supported('foo', ver, True)


@pytest.mark.parametrize(
    'version', ['A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a', 'A-3b', 'A-3u']
)
def test_important(version):
    """Test important with cruical versions
    """
    scraper = VeraPdf('testfilename', 'application/pdf')
    scraper.version = version
    scraper.messages('Success')
    assert scraper.is_important() == {'version': version}
    scraper.errors('Error')
    assert scraper.is_important() == {}
