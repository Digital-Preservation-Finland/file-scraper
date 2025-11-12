"""Metadata model for SIARD"""

from file_scraper.base import BaseMeta
from file_scraper.metadata import metadata


class DbptkMeta(BaseMeta):
    """Metadata model for SIARD scraped using dbptk."""

    _supported = {
        "application/x-siard": ["2.1.1", "2.2"]  # Supported mimetypes
    }

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return "application/x-siard"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
