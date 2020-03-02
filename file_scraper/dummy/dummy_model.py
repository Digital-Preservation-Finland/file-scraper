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


class DetectedVersionMeta(BaseMeta):
    """Give the detected file format version."""

    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.spreadsheet": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.presentation": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2"],
        "text/html": ["4.01", "5.0"],
        "text/xml": ["1.0"],
    }
    _allow_versions = True

    def __init__(self, version):
        """Initialize with given version."""
        self._version = version

    @metadata()
    def version(self):
        """Return the file format version"""
        return self._version if self._version is not None else "(:unav)"

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Stream type is not known so return (:unav)."""
        return "(:unav)"
