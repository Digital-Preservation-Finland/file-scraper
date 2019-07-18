"""Metadata model for xmllint."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class XmllintMeta(BaseMeta):
    """
    Xmllint metadata model.
    """

    _supported = {"text/xml": ["1.0"]}  # Supported mimetype
    _allow_versions = True

    def __init__(self, tree, mimetype=None, version=None):
        """
        Initialize the metadata model.

        :tree: XML element tree for the scraped file
        """
        self._tree = tree
        super(XmllintMeta, self).__init__(mimetype, version)

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version
        return self._tree.docinfo.xml_version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype
        return "text/xml"

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
