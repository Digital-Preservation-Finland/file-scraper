"""Metadata model for TextfileScraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class TextFileMeta(BaseMeta):
    """Text file metadata model."""

    _supported = {"text/plain": []}
    _allow_versions = True

    def __init__(self, errors):
        """
        Initialize metadata model.
        
        :errors: Error messages from scraper
        """
        self._errors = errors

    @metadata()
    def mimetype(self):
        """
        Return mimetype.
        
        The file is text/plain compliant if there are no errors. This will
        be returned only if predefined as plain text.
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
        """
        Return stream type.
        
        The file is text if there are no errors. This will be returned
        only if predefined as plain text.
        """
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

    def __init__(self, errors, charset, predefined_mimetype):
        """
        Initialize metadata model.
        
        :errors: Errors from scraper
        :charset: Encoding from scraper
        :predefined_mimetype: Predefined mimetype
        """
        self._errors = errors
        self._charset = charset
        self._predefined_mimetype = predefined_mimetype

    @metadata()
    def mimetype(self):
        """
        Return mimetype only if text/plain expected and no errors occured.

        Other scrapers are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if self._predefined_mimetype == "text/plain" and not self._errors:
            return "text/plain"
        else:
            return "(:unav)"

    @metadata()
    def version(self):
        """
        Return version only if text/plain expected and no errors occured.

        Other scrapers are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if self._predefined_mimetype == "text/plain" and not self._errors:
            return "(:unap)"
        else:
            return "(:unav)"

    @metadata(important=True)
    def charset(self):
        """Return charset."""
        return self._charset

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text"
