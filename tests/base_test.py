"""
Tests for extractor base.

This module tests:
    - Shell command execution.
    - That is_supported() method returns correct values for a variety of
      mimetypes and versions.
    - That messages and errors are returned properly.
    - That extractor attributes and well_formed property are set and retrieved
      correctly
    - That _check_supported() method gives error messages properly
    - That initialization of detector works properly
"""
from pathlib import Path

import pytest

from file_scraper.base import BaseExtractor, BaseMeta, BaseDetector
from file_scraper.utils import metadata
from tests.common import partial_message_included


class BaseMetaBasic(BaseMeta):
    """Metadata model supporting specific versions of one MIME type"""

    _supported = {"test/mimetype": ["0.1", "0.2"]}  # Supported file formats


class BaseExtractorBasic(BaseExtractor):
    """
    A very basic extractor for only specific versions of one MIME type.

    This extractor allows only one specific version in is_supported()
    and is used for metadata collection.
    """

    _supported_metadata = [BaseMetaBasic]  # Supported metadata models

    def extract(self):
        """Do nothing, scraping not needed here."""
        self.streams.append(BaseMetaBasic([]))

    def tools(self):
        pass


class BaseMetaVersion(BaseMeta):
    """Basic metadata model supporting all versions of a single MIME type."""

    _allow_versions = True  # Allow all versions
    _supported = {"test/mimetype": []}  # Supported file formats


class BaseExtractorVersion(BaseExtractorBasic):
    """
    A very basic extractor for multiple versions.

    This extractor that allows any given version in is_supported()
    and is used for metadata collection
    """

    _supported_metadata = [BaseMetaVersion]  # Supported metadata models


class BaseExtractorWellFormed(BaseExtractorBasic):
    """extractor that allows only scraping for well_formed result."""

    _only_wellformed = True  # Use only when checking well-formedness


class BaseDetectorTest(BaseDetector):
    """Basic detector."""

    # pylint: disable=too-few-public-methods
    def detect(self):
        """
        Test detection which simply equates to assigning predefined values as
        results.
        """
        self.mimetype = self._predefined_mimetype
        self.version = self._predefined_version

    def tools(self):
        pass


@pytest.mark.parametrize(
    ["extractor_class", "mimetype", "version", "check_wellformed",
     "supported"],
    [
        (BaseExtractorBasic, "test/mimetype", "0.1", True, True),
        (BaseExtractorBasic, "test/mimetype", None, True, True),
        (BaseExtractorBasic, "test/mimetype", "0.1", False, True),
        (BaseExtractorBasic, "test/notsupported", "0.1", True, False),
        (BaseExtractorBasic, "test/mimetype", "X", True, False),
        (BaseExtractorVersion, "test/mimetype", "0.1", True, True),
        (BaseExtractorVersion, "test/mimetype", None, True, True),
        (BaseExtractorVersion, "test/mimetype", "0.1", False, True),
        (BaseExtractorVersion, "test/notsupported", "0.1", True, False),
        (BaseExtractorVersion, "test/mimetype", "X", True, True),
        (BaseExtractorWellFormed, "test/mimetype", "0.1", True, True),
        (BaseExtractorWellFormed, "test/mimetype", None, True, True),
        (BaseExtractorWellFormed, "test/mimetype", "0.1", False, False),
        (BaseExtractorWellFormed, "test/notsupported", "0.1", False, False),
        (BaseExtractorWellFormed, "test/mimetype", "X", True, False),
    ]
)
def test_is_supported(extractor_class, mimetype, version, check_wellformed,
                      supported):
    """
    Test extractor's is_supported() method.

    :mimetype: File MIME type
    :version: File format version
    :check_wellformed: True for well-formed check, False otherwise
    :supported: Expected boolean result from is_supported()
    """
    assert (extractor_class.is_supported(mimetype, version,
                                         check_wellformed) ==
            supported)


def test_messages_errors():
    """Test extractors's messages and errors."""
    extractor = BaseExtractorBasic(Path("testfilename"), "test/mimetype")
    # pylint: disable=protected-access
    extractor._messages.append("test message")
    extractor._messages.append("test message 2")
    extractor._messages.append("")
    extractor._errors.append("test error")
    extractor._errors.append("test error 2")
    assert extractor.messages() == ["test message", "test message 2"]
    assert extractor.errors() == ["test error", "test error 2"]


def test_extractor_properties():
    """Test extractors's attributes and well_formed property."""
    extractor = BaseExtractorBasic(
        filename=Path("testfilename"), mimetype="test/mime",
        params={"test": "value"})
    # pylint: disable=protected-access
    extractor._messages.append("success")
    assert extractor.well_formed
    extractor._errors.append("error")
    assert not extractor.well_formed

    assert extractor.filename == Path("testfilename")
    # pylint: disable=protected-access
    assert extractor._params == {"test": "value"}


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


class BaseExtractorSupported(BaseExtractor):
    """Basic extractor using BaseMetaCustom metadata model."""

    def extract(self):
        pass

    _supported_metadata = [BaseMetaCustom]

    def tools(self):
        pass


@pytest.mark.parametrize(
    ["extractor_class", "mimetype", "version", "errors"],
    [
        (BaseExtractorSupported, "test/mimetype", "0.1", None),
        (BaseExtractorBasic, "test/mimetype", None,
         "type test/mimetype with version None is not supported"),
        (BaseExtractorBasic, "test/mimetype", "0.0",
         "type test/mimetype with version 0.0 is not supported"),
        (BaseExtractorBasic, "test/falsemime", "0.1",
         "type test/falsemime with version 0.1 is not supported"),
        (BaseExtractorBasic, None, "0.1",
         "None is not a supported MIME type")
    ]
)
def test_check_supported(extractor_class, mimetype, version, errors):
    """
    Test extractor's _check_supported() method.

    :extractor_class: Test extractor class
    :mimetype: File MIME type
    :version: File format version
    :errors: Expected errors
    """
    # pylint: disable=protected-access
    extractor = extractor_class(Path("testfilename"), mimetype)
    extractor.streams.append(BaseMetaCustom(mimetype=mimetype,
                                            version=version))
    extractor._check_supported()
    if not errors:
        assert not extractor.errors()
    else:
        assert partial_message_included(errors, extractor.errors())


def test_base_detector():
    """Test base detector initialization and mimetype normalization."""
    detector = BaseDetectorTest(
        filename=Path("testfilename"), mimetype="TEST/MIME", version="0.0")
    assert detector.filename == Path("testfilename")
    assert detector.mimetype is None
    assert detector.version is None
    detector.detect()
    assert detector.mimetype == "test/mime"
    assert detector.version == "0.0"


def test_tools():
    """
    Test that the base implementation of tools returns UNAV.
    """
    extractor = BaseExtractorBasic(Path("testfilename"), "test/mimetype")
    assert extractor.tools() is None
