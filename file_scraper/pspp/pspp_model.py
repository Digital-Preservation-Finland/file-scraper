"""Metadata model for PSPP scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class PsppMeta(BaseMeta):
    """Metadata model for pspp scraping."""

    _supported = {"application/x-spss-por": []}  # Supported mimetype
    _allow_versions = True                       # Allow any version

    def __init__(self, well_formed):
        """Initialize model.

        :well_formed: Well-formed status from scraper
        """
        self._well_formed = well_formed

    @metadata()
    def mimetype(self):
        """
        Return MIME type.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "application/x-spss-por" if self._well_formed else "(:unav)"

    @metadata()
    def version(self):
        """Return version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        return "(:unap)" if self._well_formed else "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        # pylint: disable=no-self-use
        return "binary"
