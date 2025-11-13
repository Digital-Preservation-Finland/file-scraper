"""Metadata model for Warchaeology."""

from __future__ import annotations

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV


class WarchaeologyMeta(BaseMeta):
    """Metadata model for Warchaeology."""

    _supported = {"application/warc": ["1.0", "1.1"]}

    def __init__(self, well_formed: bool, header: bytes | None = None) -> None:
        """Initialize the metadata model.

        :param well_formed: Well-formed status from extractor.
        :param header: WARC header.
        """
        self._well_formed = well_formed
        self._header = header

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"

    @BaseMeta.metadata()
    def mimetype(self) -> str:
        """Return the mimetype."""
        return "application/warc"

    @BaseMeta.metadata()
    def version(self) -> str:
        """Return the version."""
        if self._header is None:
            return UNAV
        header = self._header.decode("utf-8", errors="replace")
        lines = header.splitlines()
        if lines and lines[0].startswith("WARC/"):
            return lines[0].split("/")[1].strip()
        return UNAV
