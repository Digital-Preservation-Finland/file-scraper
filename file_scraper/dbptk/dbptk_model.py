"""Metadata model for SIARD"""

from file_scraper.base import BaseMeta


class DbptkMeta(BaseMeta):
    """Metadata model for SIARD scraped using dbptk."""

    _supported = {
        "application/x-siard": ["2.1.1", "2.2"]  # Supported mimetypes
    }

    @BaseMeta.metadata()
    def mimetype(self):
        """Return mimetype."""
        return "application/x-siard"

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
