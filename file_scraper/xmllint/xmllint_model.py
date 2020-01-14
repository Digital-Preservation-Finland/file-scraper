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

    def __init__(self, errors, tree):
        """
        Initialize the metadata model.

        :tree: XML element tree for the scraped file
        """
        self._tree = tree
        super(XmllintMeta, self).__init__(errors=errors)

    @metadata()
    def mimetype(self):
        """Return mimetype. The file is XML, if no errors."""
        if not self._errors:
            return "text/xml"
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
        return self._tree.docinfo.xml_version

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
