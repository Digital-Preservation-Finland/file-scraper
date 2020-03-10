"""Metadata model for HTML5"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class VnuMeta(BaseMeta):
    """Metadata model for HTML 5.0 scraped using Vnu."""

    _supported = {"text/html": ["5.0"]}  # Supported mimetypes


    def __init__(self, errors):
        """Initialize the metadata model."""
        self._errors = errors

    @metadata()
    def mimetype(self):
        """
        Return mimetype.
        
        The file is a HTML5 file if there are no errors. This will be returned
        only if predefined as HTML5.
        """
        if not self._errors:
            return "text/html"
        return "(:unav)"

    @metadata()
    def version(self):
        """
        Return version.
        
        The file is a HTML5 file if there are no errors. This will be returned
        only if predefined as HTML5.
        """
        if not self._errors:
            return "5.0"
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
