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
        self._errors = errors
        self._tree = tree

    @metadata()
    def mimetype(self):
        """
        Return mimetype.
        
        The file is an XML file, if there are no errors. This will be returned
        only if predefined as an XML file.
        """
        if not self._errors:
            return "text/xml"
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported and \
                self._tree.docinfo.xml_version:
            return self._tree.docinfo.xml_version
        return "(:unav)"

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
