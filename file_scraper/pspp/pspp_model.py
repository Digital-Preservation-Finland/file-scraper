"""Metadata model for PSPP extractor."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV


class PsppMeta(BaseMeta):
    """Metadata model for pspp scraping."""

    _supported = {"application/x-spss-por": []}  # Supported mimetype
    _allow_any_version = True

    def __init__(self, well_formed):
        """Initialize model.

        :well_formed: Well-formed status from extractor
        """
        self._well_formed = well_formed

    @BaseMeta.metadata()
    def mimetype(self):
        """
        Return MIME type.

        If the well-formed status from extractor is False,
        then we do not know the actual MIME type.
        """
        return "application/x-spss-por" if self._well_formed else UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        return UNAP if self._well_formed else UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
