"""Metadata model for Ghostscript."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class GhostscriptMeta(BaseMeta):
    """Metadata model for pdf files scraped by Ghostscript."""
    # pylint: disable=no-self-use

    # Supported mimetype and versions
    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
