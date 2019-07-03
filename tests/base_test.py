"""
Tests for scraper base.

This module tests:
    - Shell command execution.
    - That is_supported() method returns correct values for a variety of
      mimetypes and versions.
    - That messages and errors are returned properly.
    - That scraper attributes and well_formed property are set and retrieved
      correctly
"""
import subprocess
import pytest

import file_scraper.base
from file_scraper.base import (ProcessRunner, BaseScraper, BaseMeta,
                               BaseDetector)
from file_scraper.utils import metadata


def test_shell(monkeypatch):
    """Test ProcessRunner class."""

    # pylint: disable=unused-argument
    def _run_command(cmd, stdout=subprocess.PIPE, env=None):
        return (42, b"output message", b"error message")

    monkeypatch.setattr(file_scraper.base, "run_command", _run_command)
    shell = ProcessRunner("testcommand")
    assert shell.returncode == 42
    assert shell.stdout == b"output message"
    assert shell.stderr == b"error message"


class BaseMetaBasic(BaseMeta):
    """Metadata model supporting specific versions of one MIME type"""

    _supported = {"test/mimetype": ["0.1", "0.2"]}


class BaseScraperBasic(BaseScraper):
    """
    A very basic scraper for only specific versions of one MIME type.

    This scraper allows only one specific version in is_supported()
    and is used for metadata collection.
    """

    _supported_metadata = [BaseMetaBasic]

    def scrape_file(self):
        """Do nothing, scraping not needed here."""
        pass


class BaseMetaVersion(BaseMeta):
    """Basic metadata model supporting all versions of a single MIME type."""

    _allow_versions = True
    _supported = {"test/mimetype": []}


class BaseScraperVersion(BaseScraperBasic):
    """
    A very basic scraper for multiple versions.

    This scraper that allows any given version in is_supported()
    and is used for metadata collection
    """

    _supported_metadata = [BaseMetaVersion]


class BaseScraperWellFormed(BaseScraperBasic):
    """Scraper that allows only scraping for well_formed result."""

    _only_wellformed = True


class BaseDetectorBasic(BaseDetector):
    """Basic detector."""

    # pylint: disable=too-few-public-methods
    def detect(self):
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
    """Test scraper's is_supported() method."""
    assert (scraper_class.is_supported(mimetype, version, check_wellformed) ==
            supported)


def test_messages_errors():
    """Test scraper's messages and errors."""
    scraper = BaseScraperBasic("testfilename", "test/mimetype")
    # pylint: disable=protected-access
    scraper._messages.append("test message")
    scraper._messages.append("test message 2")
    scraper._errors.append("test error")
    scraper._errors.append("test error 2")
    assert scraper.messages() == "test message\ntest message 2"
    assert scraper.errors() == "ERROR: test error\nERROR: test error 2"


def test_scraper_properties():
    """Test scraper's attributes and well_formed property."""
    scraper = BaseScraperBasic("testfilename", True, {"test": "value"})
    # pylint: disable=protected-access
    scraper._messages.append("success")
    assert scraper.well_formed
    scraper._errors.append("error")
    assert not scraper.well_formed

    assert scraper.filename == "testfilename"
    # pylint: disable=protected-access
    assert scraper._check_wellformed
    assert scraper._params == {"test": "value"}

    scraper = BaseScraperBasic("testfilename", False)
    scraper._messages.append("success")
    assert scraper.well_formed is None
    scraper._errors.append("error")
    assert scraper.well_formed is None


class BaseMetaCustom(BaseMeta):
    """Metadata model that uses MIME type and version given to constructor."""

    _supported = {"test/mimetype": ["0.1"]}

    def __init__(self, mimetype, version):
        self._mimetype = mimetype
        self._version = version

    @metadata()
    def mimetype(self):
        return self._mimetype

    @metadata()
    def version(self):
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
    """Test scraper's _check_supported() method."""
    # pylint: disable=protected-access
    scraper = scraper_class("testfilename", mimetype)
    scraper.streams.append(BaseMetaCustom(mimetype, version))
    scraper._check_supported()
    if not errors:
        assert scraper.errors() == ""
    else:
        assert errors in scraper.errors()


def test_base_detector():
    """Test base detector."""
    detector = BaseDetectorBasic("testfilename")
    assert detector.filename == "testfilename"
