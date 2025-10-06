"""Metadata model for Warchaeology."""

from __future__ import annotations

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


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

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"

    @metadata()
    def mimetype(self) -> str:
        """Return the mimetype."""
        return "application/warc"

    @metadata()
    def version(self) -> str:
        """Return the version."""
        if self._header is None:
            return UNAV
        header = self._header.decode("utf-8", errors="replace")
        lines = header.splitlines()
        if lines and lines[0].startswith("WARC/"):
            return lines[0].split("/")[1].strip()
        return UNAV

    @classmethod
    def is_supported(
        cls,
        mimetype: str | None,
        version: str | None = None,
        params: dict | None = None,
    ) -> bool:
        """
        Report whether this model supports the given MIME type and version.

        :param mimetype: MIME type to be checked
        :param version: Version to be checked, defaults to None
        :param params: Parameter dict that can be used by some metadata models.
        :returns: True if MIME type is supported and all versions are allowed
            or the version is supported too.
        """
        if mimetype not in cls._supported:
            return False
        # Warchaeology cannot read WARC files without version information,
        # so None is not considered a valid version
        return (
            version in cls._supported[mimetype] or cls._allow_versions
        )
