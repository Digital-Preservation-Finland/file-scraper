"""Metadata model for TextfileScraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class TextFileMeta(BaseMeta):
    """Text file metadata model."""

    _supported = {"text/plain": []}
    _allow_versions = True

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text"


class TextEncodingMeta(BaseMeta):
    """Text encoding metadata model."""

    _supported = {"text/plain": [],
                  "text/csv": [],
                  "text/html": ["4.01", "5.0"],
                  "text/xml": ["1.0"],
                  "application/xhtml+xml": ["1.0", "1.1"]}
    _allow__versions = True

    def __init__(self, charset, mimetype=None, version=None):
        """Initialize metadata model. Add charset to attribute."""
        self._charset = charset
        super(TextEncodingMeta, self).__init__(mimetype, version)

    @metadata()
    def charset(self):
        """Return charset."""
        return self._charset

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "(:unav)"
