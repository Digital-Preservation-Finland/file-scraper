"""Metadata model for Warcs."""
from __future__ import unicode_literals

from file_scraper.defaults import UNAV
from file_scraper.utils import metadata, ensure_text
from file_scraper.base import BaseMeta


# pylint: disable=too-few-public-methods
class BaseWarctoolsMeta(BaseMeta):
    """Base metadata class for Warcs."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class GzipWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata model for compressed Warcs."""

    _supported = {"application/gzip": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def __init__(self, metadata_model):
        """
        Initialize the metadata model

        :metadata_model: WarcWarctoolsMeta object representing
                         the extracted warc.
        """
        self._metadata_model = metadata_model

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return self._metadata_model[0].mimetype()

    @metadata()
    def version(self):
        """Return the version."""
        return self._metadata_model[0].version()


class WarcWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata models for Warcs"""

    # Supported mimetype and versions
    _supported = {"application/warc": ["0.17", "0.18", "1.0"]}
    _allow_versions = True  # Allow any version

    def __init__(self, well_formed, line=None):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from scraper.
        :line: The first line of the warc archive.
        """
        self._well_formed = well_formed
        self._line = line

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        The file is a WARC file if there are not errors. This is returned only
        if predefined as a WARC file.
        """
        return "application/warc" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """Return the version."""
        if self._line is None:
            return UNAV
        if len(self._line.split(b"WARC/", 1)) > 1:
            return ensure_text(
                self._line.split(b"WARC/", 1)[1].split(b" ")[0].strip())
        return UNAV
