"""Metadata model for SIARD"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class DbptkMeta(BaseMeta):
    """Metadata model for SIARD scraped using dbptk."""

    _supported = {
        "application/x-siard": ["2.1.1", "2.2"]  # Supported mimetypes
    }

    def __init__(self, well_formed, version):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from scraper
        :version: File format version from scraper
        """
        self._well_formed = well_formed
        self._version = version

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "application/x-siard" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """
        Return file format version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        return self._version if self._well_formed else UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "binary" if self._well_formed else UNAV
