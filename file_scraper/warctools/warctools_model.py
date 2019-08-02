"""Metadata models for Warcs and Arcs."""
from __future__ import unicode_literals

from file_scraper.utils import metadata, ensure_text
from file_scraper.base import BaseMeta


# pylint: disable=too-few-public-methods
class BaseWarctoolsMeta(BaseMeta):
    """Base metadata class for Warcs and Arcs."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class GzipWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata model for compressed Warcs and Arcs."""

    _supported = {"application/gzip": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def __init__(self, metadata_model, mimetype=None, version=None):
        """
        Initialize the metadata model

        :metadata_model: Either WarcWarctoolsMeta or ArcWarctoolsMeta object
                         representing the extracted warc or arc.
        """
        self._metadata_model = metadata_model
        super(GzipWarctoolsMeta, self).__init__(mimetype=mimetype,
                                                version=version)

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype

        return self._metadata_model[0].mimetype()

    @metadata()
    def version(self):
        """Return the version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        return self._metadata_model[0].version()


class WarcWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata models for Warcs"""

    # Supported mimetype and versions
    _supported = {"application/warc": ["0.17", "0.18", "1.0"]}
    _allow_versions = True  # Allow any version

    def __init__(self, line, mimetype=None, version=None):
        """
        Initialize the metadata model.

        :line: The first line of the warc archive.
        """
        self._line = line
        super(WarcWarctoolsMeta, self).__init__(mimetype=mimetype,
                                                version=version)

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype
        return "application/warc"

    @metadata()
    def version(self):
        """Return the version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        if len(self._line.split(b"WARC/", 1)) > 1:
            return ensure_text(
                self._line.split(b"WARC/", 1)[1].split(b" ")[0].strip())
        return "(:unav)"


class ArcWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata model for Arcs."""

    # Supported mimetype and varsions
    _supported = {"application/x-internet-archive": ["1.0", "1.1"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype
        return "application/x-internet-archive"
