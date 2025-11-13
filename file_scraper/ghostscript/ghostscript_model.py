"""Metadata model for Ghostscript."""

from file_scraper.base import BaseMeta


class GhostscriptMeta(BaseMeta):
    """Metadata model for pdf files scraped by Ghostscript."""

    # Supported mimetype and versions
    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
