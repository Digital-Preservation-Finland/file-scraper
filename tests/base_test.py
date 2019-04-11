"""
Tests for scraper base.

This module tests:
    - Shell command execution.
    - That is_supported() method returns correct values for a variety of
      mimetypes and versions.
    - That messages and errors are recorded and returned properly.
    - That scraper attributes and well_formed property are set and retrieved
      correctly
    - That _collect_elements() method works and is able to gather all results
      from metadata methods
    - Concatenation of strings or empty lists with and without prefix
"""
import subprocess
from file_scraper.base import (Shell, BaseScraper, BaseDetector, concat,
                               SkipElementException)
import file_scraper.utils


def test_shell(monkeypatch):
    """Test Shell class."""

    # pylint: disable=unused-argument
    def _run_command(cmd, stdout=subprocess.PIPE, env=None):
        return (42, b'output message', b'error message')

    monkeypatch.setattr(file_scraper.base, 'run_command', _run_command)
    shell = Shell('testcommand')
    assert shell.returncode == 42
    assert shell.stdout == b'output message'
    assert shell.stderr == b'error message'


class BaseScraperBasic(BaseScraper):
    """
    A very basic scraper for only specific versions of one MIME type.

    This scraper allows only one specific version in is_supported()
    and is used for metadata collection.
    """

    _supported = {'test/mimetype': ['0.1', '0.2']}

    def scrape_file(self):
        pass

    @file_scraper.utils.metadata()
    def _version(self):
        return self.version

    @file_scraper.utils.metadata()
    def _stream_type(self):
        return 'test_stream'


class BaseScraperVersion(BaseScraperBasic):
    """
    A very basic scraper for multiple versions.

    This scraper that allows any given version in is_supported()
    and is used for metadata collection
    """

    _allow_versions = True

    # pylint: disable=no-self-use
    @file_scraper.utils.metadata()
    def _skip_this(self):
        raise SkipElementException()

    @file_scraper.utils.metadata()
    def _collect_this(self):
        return 'collected'


class BaseScraperWellFormed(BaseScraperBasic):
    """Scraper that allows only scraping for well_formed result."""

    _only_wellformed = True


class BaseDetectorBasic(BaseDetector):
    """Basic detector."""

    # pylint: disable=too-few-public-methods
    def detect(self):
        pass


def test_is_supported():
    """Test scraper's is_supported() method."""
    assert BaseScraperBasic.is_supported('test/mimetype', '0.1', True)
    assert not BaseScraperBasic.is_supported('test/mimetype', None, True)
    assert BaseScraperBasic.is_supported('test/mimetype', '0.1', False)
    assert not BaseScraperBasic.is_supported('test/notsupported', '0.1', True)
    assert not BaseScraperBasic.is_supported('test/mimetype', 'X', True)

    assert BaseScraperVersion.is_supported('test/mimetype', '0.1', True)
    assert BaseScraperVersion.is_supported('test/mimetype', None, True)
    assert BaseScraperVersion.is_supported('test/mimetype', '0.1', False)
    assert not BaseScraperVersion.is_supported('test/notsupported', '0.1',
                                               True)
    assert BaseScraperVersion.is_supported('test/mimetype', 'X', True)

    assert BaseScraperWellFormed.is_supported('test/mimetype', '0.1', True)
    assert not BaseScraperWellFormed.is_supported('test/mimetype', None, True)
    assert not BaseScraperWellFormed.is_supported('test/mimetype', '0.1',
                                                  False)
    assert not BaseScraperWellFormed.is_supported('test/notsupported', '0.1',
                                                  True)
    assert not BaseScraperWellFormed.is_supported('test/mimetype', 'X', True)


def test_messages_errors():
    """Test scraper's messages and errors."""
    scraper = BaseScraperBasic('testfilename', 'test/mimetype')
    scraper.messages('test message')
    scraper.messages('test message 2')
    scraper.errors('test error')
    scraper.errors('test error 2')
    assert scraper.messages() == 'test message\ntest message 2'
    assert scraper.errors() == 'ERROR: test error\nERROR: test error 2'


def test_scraper_properties():
    """Test scraper's attributes and well_formed property."""
    scraper = BaseScraperBasic('testfilename', 'test/mimetype', True,
                               {'test': 'value'})
    scraper.messages('success')
    assert scraper.well_formed
    scraper.errors('error')
    assert not scraper.well_formed

    assert scraper.filename == 'testfilename'
    assert scraper.mimetype == 'test/mimetype'
    # pylint: disable=protected-access
    assert scraper._check_wellformed
    assert scraper._params == {'test': 'value'}

    scraper = BaseScraperBasic('testfilename', 'test/mimetype', False)
    scraper.messages('success')
    assert scraper.well_formed is None
    scraper.errors('error')
    assert scraper.well_formed is None


def test_collect_elements():
    """Test scraper's _collect_elements() method."""
    scraper = BaseScraperBasic('testfilename', 'test/mimetype')
    scraper._collect_elements()  # pylint: disable=protected-access
    assert scraper.streams == {
        0: {'mimetype': 'test/mimetype', 'version': None,
            'stream_type': 'test_stream', 'index': 0}}
    scraper = BaseScraperVersion('testfilename', 'test/mimetype')
    scraper.version = '0.1'
    scraper._collect_elements()  # pylint: disable=protected-access
    assert scraper.streams == {
        0: {'mimetype': 'test/mimetype', 'version': '0.1',
            'stream_type': 'test_stream', 'index': 0,
            'collect_this': 'collected'}}


def test_check_supported():
    """Test scraper's _check_supported() method."""
    # pylint: disable=protected-access
    scraper = BaseScraperBasic('testfilename', 'test/mimetype')
    scraper._check_supported()
    assert scraper.errors() == ''

    scraper = BaseScraperBasic('testfilename', 'test/mimetype')
    scraper.version = '0.1'
    scraper._check_supported()
    assert scraper.errors() == ''

    scraper = BaseScraperBasic('testfilename', 'test/mimetype')
    scraper.version = '0.0'
    scraper._check_supported()
    assert scraper.errors() == 'ERROR: Version 0.0 is not supported.'

    scraper = BaseScraperBasic('testfilename', 'test/falsemime')
    scraper.version = '0.1'
    scraper._check_supported()
    assert scraper.errors() == 'ERROR: Mimetype test/falsemime is not ' \
                               'supported.'

    scraper = BaseScraperBasic('testfilename', None)
    scraper._check_supported()
    assert scraper.errors() == 'ERROR: None is not supported mimetype.'


def test_base_detector():
    """Test base detector."""
    detector = BaseDetectorBasic('testfilename')
    assert detector.filename == 'testfilename'


def test_concat():
    """Test concat function."""
    assert concat([]) == ''
    assert concat(['test']) == 'test'
    assert concat(['test', 'test']) == 'test\ntest'
    assert concat([], 'prefix:') == ''
    assert concat(['test'], 'prefix:') == 'prefix:test'
    assert concat(['test', 'test'], 'prefix:') == 'prefix:test\nprefix:test'
