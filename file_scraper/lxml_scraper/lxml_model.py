"""Metadata model for XML and HTML5 header encoding check with lxml. """
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class LxmlMeta(BaseMeta):
    """Metadata model for character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {"text/xml": ["1.0"], "text/html": ["4.01", "5.0"]}

    def __init__(self, errors, tree):
        """
        Initialize the metadata class.

        :errors: Errors from scraper.
        :tree: etree parsed from the file that is being scraped
        """
        self._tree = tree
        super(LxmlMeta, self).__init__(errors)

    @metadata()
    def version(self):
        """Return version."""
        if "<!DOCTYPE html>" in self._tree.docinfo.doctype:
            return "5.0"
        if "HTML 4.01" in self._tree.docinfo.doctype:
            return "4.01"
        return "(:unav)"

    @metadata()
    def charset(self):
        """Return charset."""
        return self._tree.docinfo.encoding

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
