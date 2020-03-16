"""Metadata model for dummy scrapers."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class DummyMeta(BaseMeta):
    """Minimal metadata model for dummy scrapers."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Stream type is not known so return (:unav)."""
        return "(:unav)"


class DetectedBinaryVersionMeta(BaseMeta):
    """
    This model results the given file format MIME type and version for some
    file formats. The corresponding scraper gets the version as a parameter
    originally from a detector and results it as a scraper value.

    We don't currently know any other constructive way to get file format
    version for a few formats.
    """

    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.spreadsheet": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.presentation": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2"],
        "application/x-spss-por": []
    }
    _allow_versions = True

    def __init__(self, mimetype, version):
        """
        Initialize with given version.

        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @metadata()
    def mimetype(self):
        """Return MIME type"""
        if self._mimetype:
            return self._mimetype
        return "(:unav)"

    @metadata()
    def version(self):
        """Return the file format version"""
        if self.mimetype() == "application/x-spss-por":
            return "(:unap)"
        return self._version if self._version is not None else "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "binary" if self.mimetype() != "(:unav)" else "(:unav)"


class DetectedTextVersionMeta(DetectedBinaryVersionMeta):
    """
    Variation of DetectedBinaryVersionMeta model for some text files.

    Full scraping actually is able to result the same, but this is needed
    when Scraper is used for metadata collecting.
    """
    _supported = {
        "text/html": ["4.01", "5.0"],
        "text/xml": ["1.0"],
    }

    @metadata()
    def version(self):
        """Return version."""
        version = super(DetectedTextVersionMeta, self).version()
        if version == "(:unav)" and self.mimetype() == "text/xml":
            return "1.0"
        return version

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text" if self.mimetype() != "(:unav)" else "(:unav)"


class DetectedPdfaVersionMeta(DetectedBinaryVersionMeta):
    """
    Variation of DetectedBinaryVersionMeta model for PDF/A files.

    We allow only supported versions and keep it important.

    Full scraping actually is able to result the same, but this is needed
    when Scraper is used for metadata collecting.
    """
    # Supported mimetypes and versions
    _supported = {"application/pdf": ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u",
                                      "A-3a", "A-3b", "A-3u"]}
    _allow_versions = False  # No other versions allowed

    @metadata(important=True)
    def version(self):
        """Return the file format version"""
        return self._version if self._version is not None else "(:unav)"
