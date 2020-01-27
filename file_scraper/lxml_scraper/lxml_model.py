"""Metadata model for XML and HTML5 header encoding check with lxml. """
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class LxmlMeta(BaseMeta):
    """Metadata model for character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {"text/xml": ["1.0"], "text/html": ["5.0"]}
    _only_wellformed = True  # Only well-formed check

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
