"""Metadata model for Ghostscript."""

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class GhostscriptMeta(BaseMeta):
    """Metadata model for pdf files scraped by Ghostscript."""
    # pylint: disable=no-self-use

    # Supported mimetype and versions
    _supported = {"application/pdf": ["1.7", "A-2a", "A-2b", "A-2u", "A-3a",
                                      "A-3b", "A-3u"]}

    def __init__(self):
        pass

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
