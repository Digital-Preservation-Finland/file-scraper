"""Metadata model for XML and HTML5 header encoding check with lxml. """
from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class LxmlMeta(BaseMeta):
    """Metadata model for character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {"text/xml": ["1.0"], "text/html": ["5.0"]}
    _only_wellformed = True  # Only well-formed check

    def __init__(self, tree):
        """
        Initialize the metadata class.

        :tree: etree parsed from the file that is being scraped
        """
        self._tree = tree
        super(LxmlMeta, self).__init__()

    @metadata()
    def _charset(self):
        """Return charset."""
        return self._tree.docinfo.encoding

    # pylint: disable=no-self-use
    @metadata()
    def _stream_type(self):
        """Return file type."""
        return "text"
