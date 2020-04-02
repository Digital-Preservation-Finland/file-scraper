"""
Tests for scraper base.

This module tests:
    - Shell command execution.
    - That is_supported() method returns correct values for a variety of
      mimetypes and versions.
    - That messages and errors are returned properly.
    - That scraper attributes and well_formed property are set and retrieved
      correctly
    - That _check_supported() method gives error messages properly
    - That initialization of detector works properly
"""
from __future__ import unicode_literals

import pytest

from file_scraper.base import BaseScraper, BaseMeta, BaseDetector
from file_scraper.utils import metadata
from tests.common import partial_message_included


class BaseMetaBasic(BaseMeta):
    """Metadata model supporting specific versions of one MIME type"""

    _supported = {"test/mimetype": ["0.1", "0.2"]}  # Supported file formats


class BaseScraperBasic(BaseScraper):
    """
    A very basic scraper for only specific versions of one MIME type.

    This scraper allows only one specific version in is_supported()
    and is used for metadata collection.
    """

    _supported_metadata = [BaseMetaBasic]  # Supported metadata models

    def scrape_file(self):
        """Do nothing, scraping not needed here."""
        self.streams.append(BaseMetaBasic([]))


class BaseMetaVersion(BaseMeta):
    """Basic metadata model supporting all versions of a single MIME type."""

    _allow_versions = True  # Allow all versions
    _supported = {"test/mimetype": []}  # Supported file formats


class BaseScraperVersion(BaseScraperBasic):
    """
    A very basic scraper for multiple versions.

    This scraper that allows any given version in is_supported()
    and is used for metadata collection
    """

    _supported_metadata = [BaseMetaVersion]  # Supported metadata models


class BaseScraperWellFormed(BaseScraperBasic):
    """Scraper that allows only scraping for well_formed result."""

    _only_wellformed = True  # Use only when checking well-formedness


class BaseDetectorBasic(BaseDetector):
    """Basic detector."""

    # pylint: disable=too-few-public-methods
    def detect(self):
        """Do not detect anything"""
        pass


@pytest.mark.parametrize(
    ["scraper_class", "mimetype", "version", "check_wellformed", "supported"],
    [
        (BaseScraperBasic, "test/mimetype", "0.1", True, True),
        (BaseScraperBasic, "test/mimetype", None, True, True),
        (BaseScraperBasic, "test/mimetype", "0.1", False, True),
        (BaseScraperBasic, "test/notsupported", "0.1", True, False),
        (BaseScraperBasic, "test/mimetype", "X", True, False),
        (BaseScraperVersion, "test/mimetype", "0.1", True, True),
        (BaseScraperVersion, "test/mimetype", None, True, True),
        (BaseScraperVersion, "test/mimetype", "0.1", False, True),
        (BaseScraperVersion, "test/notsupported", "0.1", True, False),
        (BaseScraperVersion, "test/mimetype", "X", True, True),
        (BaseScraperWellFormed, "test/mimetype", "0.1", True, True),
        (BaseScraperWellFormed, "test/mimetype", None, True, True),
        (BaseScraperWellFormed, "test/mimetype", "0.1", False, False),
        (BaseScraperWellFormed, "test/notsupported", "0.1", False, False),
        (BaseScraperWellFormed, "test/mimetype", "X", True, False),
    ]
)
def test_is_supported(scraper_class, mimetype, version, check_wellformed,
                      supported):
    """
    Test scraper's is_supported() method.

    :mimetype: File MIME type
    :version: File format version
    :check_wellformed: True for well-formed check, False otherwise
    :supported: Expected boolean result from is_supported()
    """
    assert (scraper_class.is_supported(mimetype, version, check_wellformed) ==
            supported)


def test_messages_errors():
    """Test scraper's messages and errors."""
    scraper = BaseScraperBasic("testfilename", "test/mimetype")
    # pylint: disable=protected-access
    scraper._messages.append("test message")
    scraper._messages.append("test message 2")
    scraper._messages.append("")
    scraper._errors.append("test error")
    scraper._errors.append("test error 2")
    assert scraper.messages() == ["test message", "test message 2"]
    assert scraper.errors() == ["test error", "test error 2"]


def test_scraper_properties():
    """Test scraper's attributes and well_formed property."""
    scraper = BaseScraperBasic(
        filename="testfilename", mimetype="test/mime",
        params={"test": "value"})
    # pylint: disable=protected-access
    scraper._messages.append("success")
    assert scraper.well_formed
    scraper._errors.append("error")
    assert not scraper.well_formed

    assert scraper.filename == "testfilename"
    # pylint: disable=protected-access
    assert scraper._params == {"test": "value"}


class BaseMetaCustom(BaseMeta):
    """Metadata model that uses MIME type and version given to constructor."""

    _supported = {"test/mimetype": ["0.1"]}  # Supported file formats

    def __init__(self, mimetype, version):
        """
        Initialize metadata model

        :mimetype: File MIME type
        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @metadata()
    def mimetype(self):
        """Return MIME type"""
        return self._mimetype

    @metadata()
    def version(self):
        """Return file format version"""
        return self._version


class BaseScraperSupported(BaseScraper):
    """Basic scraper using BaseMetaCustom metadata model."""

    _supported_metadata = [BaseMetaCustom]


@pytest.mark.parametrize(
    ["scraper_class", "mimetype", "version", "errors"],
    [
        (BaseScraperSupported, "test/mimetype", "0.1", None),
        (BaseScraperBasic, "test/mimetype", None,
         "type test/mimetype with version None is not supported"),
        (BaseScraperBasic, "test/mimetype", "0.0",
         "type test/mimetype with version 0.0 is not supported"),
        (BaseScraperBasic, "test/falsemime", "0.1",
         "type test/falsemime with version 0.1 is not supported"),
        (BaseScraperBasic, None, "0.1",
         "None is not a supported MIME type")
    ]
)
def test_check_supported(scraper_class, mimetype, version, errors):
    """
    Test scraper's _check_supported() method.

    :scraper_class: Test scraper class
    :mimetype: File MIME type
    :version: File format version
    :errors: Expected errors
    """
    # pylint: disable=protected-access
    scraper = scraper_class("testfilename", mimetype)
    scraper.streams.append(BaseMetaCustom(mimetype=mimetype,
                                          version=version))
    scraper._check_supported()
    if not errors:
        assert not scraper.errors()
    else:
        assert partial_message_included(errors, scraper.errors())


def test_base_detector():
    """Test base detector initialization."""
    detector = BaseDetectorBasic(
        filename="testfilename", mimetype="test/mime", version="0.0")
    assert detector.filename == "testfilename"
    # pylint: disable=protected-access
    assert detector._given_mimetype == "test/mime"
    assert detector._given_version == "0.0"
