"""Metadata model for HTML5"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class VnuMeta(BaseMeta):
    """Metadata model for HTML 5.0 scraped using Vnu."""

    _supported = {"text/html": ["5.0"]}  # Supported mimetypes

    # pylint: disable=no-self-use
    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return "text/html"

    @metadata()
    def version(self):
        """Return version."""
        return "5.0"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
