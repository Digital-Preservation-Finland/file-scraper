"""Metadata model for PSPP scraper."""

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class PsppMeta(BaseMeta):
    """Metadata model for pspp scraping."""

    _supported = {"application/x-spss-por": []}  # Supported mimetype
    _allow_versions = True                       # Allow any version

    # pylint: disable=no-self-use
    @metadata()
    def version(self):
        """Return version."""
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
