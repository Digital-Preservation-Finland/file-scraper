"""Metadata model for TextfileScraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.utils import metadata


class TextFileMeta(BaseMeta):
    """Text file metadata model."""

    _supported = {"text/plain": []}
    _allow_versions = True

    def __init__(self, well_formed):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from scraper
        """
        self._well_formed = well_formed

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "text/plain" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """Return version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        return UNAP if self._well_formed else UNAV

    @metadata()
    def stream_type(self):
        """
        Return stream type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV


class TextEncodingMeta(BaseMeta):
    """Text encoding metadata model."""

    _supported = {"text/plain": [],
                  "text/csv": [],
                  "text/html": ["4.01", "5.0"],
                  "text/xml": ["1.0"],
                  "application/xhtml+xml": ["1.0", "1.1"]}
    _allow_versions = True

    def __init__(self, well_formed, charset, predefined_mimetype):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from scraper
        :charset: Encoding from scraper
        :predefined_mimetype: Predefined mimetype
        """
        self._well_formed = well_formed
        self._charset = charset
        self._predefined_mimetype = predefined_mimetype

    @metadata()
    def mimetype(self):
        """
        Return mimetype only if text/plain expected and no errors occured.

        Other scrapers are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if self._predefined_mimetype == "text/plain" and self._well_formed:
            return "text/plain"

        return UNAV

    @metadata()
    def version(self):
        """
        Return version only if text/plain expected and no errors occured.

        Other scrapers are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if self._predefined_mimetype == "text/plain" and self._well_formed:
            return UNAP
        return UNAV

    @metadata(important=True)
    def charset(self):
        """Return charset."""
        return self._charset

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text"
