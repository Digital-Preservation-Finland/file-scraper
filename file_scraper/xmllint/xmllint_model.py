"""Metadata model for xmllint."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class XmllintMeta(BaseMeta):
    """
    Xmllint metadata model.
    """

    _supported = {"text/xml": ["1.0"]}  # Supported mimetype
    _allow_versions = True

    def __init__(self, well_formed, tree):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from scraper
        :tree: XML element tree for the scraped file
        """
        self._well_formed = well_formed
        self._tree = tree

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "text/xml" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported and \
                self._tree.docinfo.xml_version:
            return self._tree.docinfo.xml_version
        return UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV
