"""Metadata model for dummy extractors."""

from __future__ import annotations

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV


class ExtractorNotFoundMeta(BaseMeta):
    """
    Metadata model for ExtractorNotFound extractor. Otherwise minimal model,
    but allows setting mimetype and version, if detected.
    """

    # TODO: What is the point of this metadata model? Could Scraper
    # simply raise exception when extractor is not found? TPASPKT-1669

    def __init__(self, mimetype=None, version=None):
        """
        Initialize with given mimetype and version.

        :mimetype: File MIME type
        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type"""
        if self._mimetype:
            return self._mimetype
        return UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return the file format version"""
        if self._version:
            return self._version
        return UNAV


class DetectedMimeVersionMeta(BaseMeta):
    """Metadata model based on detected/predefined metadata.

    This model is needed because there is no extractors for file formats
    that are preserved only bit-level, but file-scraper still has to
    detect them. The purpose of this model is to:

    1. Avoid ExtractorNotFoundMeta
    2. Set stream type to "binary"
    """

    _supported = {
        "application/x.fi-dpres.segy": ["(:unkn)", "1.0", "2.0"],
        "application/x.fi-dpres.atlproj": ["(:unap)"],
    }

    def __init__(self, mimetype: str | None, version: str | None) -> None:
        """
        Initialize with given mimetype and version.

        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @BaseMeta.metadata()
    def mimetype(self) -> str:
        """Return MIME type"""
        if self._mimetype:
            return self._mimetype
        return UNAV

    @BaseMeta.metadata()
    def version(self) -> str:
        """Return the file format version"""
        return self._version if self._version is not None else UNAV

    @BaseMeta.metadata()
    def stream_type(self) -> str:
        """Return stream type."""
        return "binary"


class DetectedEpubVersionMeta(DetectedMimeVersionMeta):
    """Identical with DetectedEpubVersionMeta but supports only EPUB.

    This model is needed because only proper epub extractor is
    JHoveEpubExtractor, which is used only when well-formedness is
    checked. When well-formedness is not checked, this model is used to:

    1. Avoid ExtractorNotFoundMeta
    2. Set stream type to "binary"
    """

    _supported = {
        "application/epub+zip": ["2.0.1", "3"],
    }


class DetectedSpssVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for SPSS Portable files.

    This model is needed because only proper spss extractor is
    PsppExtractor, which is used only when well-formedness is checked.
    When well-formedness is not checked, this model is used to:

    1. Avoid ExtractorNotFoundMeta
    2. Set version to "(:unap)"
    3. Set stream type to "binary"

    We allow all versions.
    """

    _supported = {
        "application/x-spss-por": []
    }
    _allow_any_version = True

    @BaseMeta.metadata()
    def version(self):
        """Return the file format version"""
        # TODO: Why extractors have to decide whether version is UNAP or
        # not? The same information could be automatically derived from
        # data in dpres-file-formats.
        return UNAP


class DetectedSiardVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for SIARD files.

    This model is needed because only proper siard extractor is
    DbptkExtractor, which is used only when well-formedness is checked.
    When well-formedness is not checked, this model is used to:

    1. Avoid ExtractorNotFoundMeta
    3. Set stream type to "binary"
    """

    _supported = {
        "application/x-siard": []
    }
    _allow_any_version = True
