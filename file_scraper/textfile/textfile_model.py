"""Metadata model for TextfileScraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class TextFileMeta(BaseMeta):
    """Text file metadata model."""

    _supported = {"text/plain": []}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """
        Return mimetype. The file is text/plain compliant if there are no
        errors.
        """
        if not self._errors:
            return "text/plain"
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
        if not self._errors:
            return "(:unap)"
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type. It is text, if no errors."""
        if not self._errors:
            return "text"
        return "(:unav)"


class TextEncodingMeta(BaseMeta):
    """Text encoding metadata model."""

    _supported = {"text/plain": [],
                  "text/csv": [],
                  "text/html": ["4.01", "5.0"],
                  "text/xml": ["1.0"],
                  "application/xhtml+xml": ["1.0", "1.1"]}
    _allow_versions = True

    def __init__(self, charset, mimetype=None, version=None):
        """Initialize metadata model. Add charset to attribute."""
        self._charset = charset
        super(TextEncodingMeta, self).__init__(mimetype, version)

    @metadata(important=True)
    def charset(self):
        """Return charset."""
        return self._charset

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text"
