"""Metadata model for xmllint."""

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class XmllintMeta(BaseMeta):
    """
    Xmllint metadata model.
    """

    _supported = {"text/xml": []}  # Supported mimetype
    _allow_versions = True

    def __init__(self, tree):
        """
        Initialize the metadata model.

        :tree: XML element tree for the scraped file
        """
        self._tree = tree
        super(XmllintMeta, self).__init__()

    @metadata()
    def version(self):
        """Return version."""
        return self._tree.docinfo.xml_version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return "text/xml"

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
