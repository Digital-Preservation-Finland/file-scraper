"""Metadata model for Warcs."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import ensure_text, metadata


class WarctoolsMeta(BaseMeta):
    """Metadata models for Warcs"""

    # Supported mimetype and versions
    _supported = {"application/warc": ["0.17", "0.18", "1.0"]}

    def __init__(self, well_formed, line=None):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from extractor.
        :line: The first line of the warc archive.
        """
        self._well_formed = well_formed
        self._line = line

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"

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
                self._line.split(b"WARC/", 1)[1].split(b" ")[0].strip()
            )
        return UNAV
