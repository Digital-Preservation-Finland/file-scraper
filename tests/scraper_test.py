"""Tests for main scraper
"""
import pytest
import file_scraper.scraper
from file_scraper.scraper import Scraper
from file_scraper.base import BaseScraper


class _TestScraper(BaseScraper):
    """Monkey patch for CheckTextFile class
    """
    def scrape_file(self):
        pass

    def _s_stream_type(self):
        return None

    @property
    def well_formed(self):
        if self.filename == 'textfile':
            return True
        else:
            return False


def test_is_textfile(monkeypatch):
    """Test that CheckTextFile well-formed value is returned.
    """
    monkeypatch.setattr(file_scraper.scraper, 'CheckTextFile', _TestScraper)
    scraper = Scraper('textfile')
    assert scraper.is_textfile()
    scraper = Scraper('binaryfile')
    assert not scraper.is_textfile()


def test_checksum():
    """Test that checksum value of the file is returned
    """
    scraper = Scraper('tests/data/text_plain/valid__utf8.txt')
    assert scraper.checksum() == 'b40c60d0770eb7bd1a345725f857c61a'
    assert scraper.checksum('SHA-1') == \
        'a0d01fcbff5d86327d542687dcfd8b299d054147'
    with pytest.raises(ValueError):
        assert scraper.checksum('foo')
    with pytest.raises(IOError):
        scraper = Scraper('non_exists')
        assert scraper.checksum()


def test_empty_file():
    """Test empty file.
    """
    scraper = Scraper('test/data/text_plain/invalid__empty.txt')
    scraper.scrape()
    assert not scraper.well_formed


def test_missing_file():
    """Test missing file.
    """
    scraper = Scraper('missing_file')
    scraper.scrape()
    assert not scraper.well_formed

    scraper = Scraper(None)
    scraper.scrape()
    assert not scraper.well_formed
