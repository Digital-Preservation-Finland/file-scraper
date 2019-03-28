"""
Tests for VeraPDF scraper for PDF/A files.

This module tests that:
    - For pdf versions A-1a, A-2b and A-3b, MIME type, version, streams and
      well-formedness are scraped correctly. This is tested using one
      well-formed file and two erroneous ones (one with altered payload and
      one in which a xref entry has been removed) for each version.
    - For well-formed files, scraper messages contain "PDF file is compliant
      with Validation Profile requirements".
    - For the files with altered payload, scraper errors contain "can not
      locate xref table".
    - For the files with removed xref entry, scraper errors contain "In a
      cross reference subsection header".
    - For files that are valid PDF 1.7 or 1.4 but not valid PDF/A, MIME type,
      version and streams are scraped correctly but they are reported as
      not well-formed.
    - When well-formedness is not checked, scraper messages contain "Skipping
      scraper" and well_formed is None.
    - The scraper supports MIME type application/pdf with versions A-1b or
      None when well-formedness is checked, but does not support them when
      well-formedness is not checked. The scraper also does not support  made
      up MIME types or versions.
    - Versions A-1a, A-1b, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u are recorded
      recorded in dict returned by get_important() function when scraper
      messages contain "Success", but when scraper errors contain "Error",
      the dict is empty.
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
    """Test scraper with PDF/A."""
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
    """Test scraper with files that are not valid PDF/A."""
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


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = VeraPdf('tests/data/application_pdf/valid_A-1a.pdf',
                      'application/pdf', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
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
    """Test important with cruical versions."""
    scraper = VeraPdf('testfilename', 'application/pdf')
    scraper.version = version
    scraper.messages('Success')
    assert scraper.get_important() == {'version': version}
    scraper.errors('Error')
    assert scraper.get_important() == {}
