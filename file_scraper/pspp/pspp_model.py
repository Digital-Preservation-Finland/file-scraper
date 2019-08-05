"""Metadata model for PSPP scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class PsppMeta(BaseMeta):
    """Metadata model for pspp scraping."""

    _supported = {"application/x-spss-por": []}  # Supported mimetype
    _allow_versions = True                       # Allow any version

    @metadata()
    def stream_type(self):
        """Return file type."""
        # pylint: disable=no-self-use
        return "binary"
