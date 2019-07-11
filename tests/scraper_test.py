"""
Tests for main scraper.

This module tests that:
    - Monkeypatched is_textfile() returns True when scraper returns
      well-formed and False otherwise.
    - checksum() method returns correct checksums both using MD5 and SHA-1
      algorithms.
    - checksum() method raises ValueError when illegal algorithm is given.
    - checksum() method raises IOError when checksum calculation is attempted
      for a file that does not exist.
    - empty text files are not well-formed according to the scraper.
    - non-existent files are not well-formed according to the scraper.
    - giving None instead of a file name to the scraper results in successful
      scraping with a result of not well-formed.
"""
from __future__ import unicode_literals

import pytest

import file_scraper.scraper
from file_scraper.base import BaseScraper
from file_scraper.scraper import Scraper


class _TestScraper(BaseScraper):
    """Monkey patch for CheckTextFile class."""

    def scrape_file(self):
        """Do nothing."""
        pass

    @property
    def well_formed(self):
        return self.filename == b"textfile"


def test_is_textfile(monkeypatch):
    """Test that CheckTextFile well-formed value is returned."""
    monkeypatch.setattr(file_scraper.scraper, "TextfileScraper", _TestScraper)
    scraper = Scraper("textfile")
    assert scraper.is_textfile()
    scraper = Scraper("binaryfile")
    assert not scraper.is_textfile()


def test_checksum():
    """Test that checksum value of the file is returned."""
    scraper = Scraper("tests/data/text_plain/valid__utf8.txt")
    assert scraper.checksum() == "b40c60d0770eb7bd1a345725f857c61a"
    assert scraper.checksum("SHA-1") == \
        "a0d01fcbff5d86327d542687dcfd8b299d054147"
    with pytest.raises(ValueError):
        assert scraper.checksum("foo")
    with pytest.raises(IOError):
        scraper = Scraper("non_exists")
        assert scraper.checksum()


def test_empty_file():
    """Test empty file."""
    scraper = Scraper("test/data/text_plain/invalid__empty.txt")
    scraper.scrape()
    assert not scraper.well_formed


def test_missing_file():
    """Test missing file."""
    scraper = Scraper("missing_file")
    scraper.scrape()
    assert not scraper.well_formed

    scraper = Scraper(None)
    scraper.scrape()
    assert not scraper.well_formed
