"""Test the file_scraper.scrapers.warctools module"""
import pytest
from file_scraper.scrapers.warctools import GzipWarctools, WarcWarctools, \
    ArcWarctools
from tests.common import parse_results


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.0_.warc.gz', {
            'purpose': 'Test valid warc file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_1.0_.arc.gz', {
            'purpose': 'Test valid arc file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid__empty.warc.gz', {
            'purpose': 'Test empty warc file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'}),
        ('invalid__missing_data.warc.gz', {
            'purpose': 'Test invalid warc gzip.',
            'stdout_part': '',
            'stderr_part': 'unpack requires a string argument of length 4'}),
        ('invalid__missing_data.arc.gz', {
            'purpose': 'Test invalid arc gzip.',
            'stdout_part': '',
            'stderr_part': 'unpack requires a string argument of length 4'}),
        ('invalid__empty.arc.gz', {
            'purpose': 'Test empty arc file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'})
    ]
)
def test_gzip_scraper(filename, result_dict):
    """Test scraper"""
    if 'warc' in filename:
        mime = 'application/warc'
        classname = 'WarcWarctools'
    else:
        mime = 'application/x-internet-archive'
        classname = 'ArcWarctools'
    correct = parse_results(filename, mime,
                            result_dict, True)
    scraper = GzipWarctools(correct.filename, 'application/gzip',
                            True, correct.params)
    scraper.scrape_file()

    if correct.version == '' or correct.mimetype == \
            'application/x-internet-archive':
        correct.version = None
        correct.streams[0]['version'] = None
    if not correct.well_formed and correct.version is None:
        correct.mimetype = 'application/gzip'
        correct.streams[0]['mimetype'] = 'application/gzip'
        classname = 'GzipWarctools'

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == classname
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_0.17.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_0.18.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_1.0.warc', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_1.0_.warc.gz', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid_0.17_too_short_content_length.warc', {
            'purpose': 'Test short content length.',
            'stdout_part': '',
            'stderr_part': 'warc errors at'}),
        ('invalid__missing_data.warc.gz', {
            'purpose': 'Test missing data.',
            'stdout_part': '',
            'stderr_part': 'unpack requires a string argument of length 4'}),
        ('invalid_0.18_too_short_content_length.warc', {
            'purpose': 'Test short content length.',
            'stdout_part': '',
            'stderr_part': 'warc errors at'}),
        ('invalid__empty.warc', {
            'purpose': 'Test empty warc file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'}),
        ('invalid__empty.warc.gz', {
            'purpose': 'Test empty gz file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'})
    ]
)
def test_warc_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'application/warc',
                            result_dict, True)
    scraper = WarcWarctools(correct.filename, correct.mimetype,
                            True, correct.params)
    scraper.scrape_file()
    if correct.version == '':
        correct.version = None
    if correct.streams[0]['version'] == '':
        correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'WarcWarctools'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.0.arc', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('valid_1.0_.arc.gz', {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': ''}),
        ('invalid__empty.arc', {
            'purpose': 'Test empty arc file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'}),
        ('invalid__empty.arc.gz', {
            'purpose': 'Test empty gz file.',
            'stdout_part': '',
            'stderr_part': 'Empty file.'}),
        ('invalid_1.0_missing_field.arc', {
            'purpose': 'Test missing header',
            'stdout_part': '',
            'stderr_part': 'Exception: missing headers'}),
        ('invalid__missing_data.arc.gz', {
            'purpose': 'Test missing data.',
            'stdout_part': '',
            'stderr_part': 'unpack requires a string argument of length 4'})
    ]
)
def test_arc_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, 'application/x-internet-archive',
                            result_dict, True)
    scraper = ArcWarctools(correct.filename, correct.mimetype,
                           True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['version'] = None
    assert scraper.mimetype == correct.mimetype
    assert scraper.version is None  # Scraper can not solve version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'ArcWarctools'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_no_wellformed_gzip():
    """Test scraper without well-formed check"""
    scraper = GzipWarctools('valid_1.0_.warc.gz', 'application/gzip', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_no_wellformed_warc():
    """Test scraper without well-formed check"""
    scraper = WarcWarctools('valid_1.0_.warc', 'application/warc', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_no_wellformed_arc():
    """Test scraper without well-formed check"""
    scraper = ArcWarctools('valid_1.0_.arc', 'application/x-internet-archive',
                           False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_gzip_is_supported():
    """Test is_supported method"""
    mime = 'application/gzip'
    ver = ''
    assert GzipWarctools.is_supported(mime, ver, True)
    assert GzipWarctools.is_supported(mime, None, True)
    assert not GzipWarctools.is_supported(mime, ver, False)
    assert GzipWarctools.is_supported(mime, 'foo', True)
    assert not GzipWarctools.is_supported('foo', ver, True)


def test_warc_is_supported():
    """Test is_supported method"""
    mime = 'application/warc'
    ver = ''
    assert WarcWarctools.is_supported(mime, ver, True)
    assert WarcWarctools.is_supported(mime, None, True)
    assert not WarcWarctools.is_supported(mime, ver, False)
    assert WarcWarctools.is_supported(mime, 'foo', True)
    assert not WarcWarctools.is_supported('foo', ver, True)


def test_arc_is_supported():
    """Test is_supported method"""
    mime = 'application/x-internet-archive'
    ver = ''
    assert ArcWarctools.is_supported(mime, ver, True)
    assert ArcWarctools.is_supported(mime, None, True)
    assert not ArcWarctools.is_supported(mime, ver, False)
    assert ArcWarctools.is_supported(mime, 'foo', True)
    assert not ArcWarctools.is_supported('foo', ver, True)
