"""Metadata model for HTML5"""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class VnuMeta(BaseMeta):
    """Metadata model for HTML 5.0 scraped using Vnu."""

    _supported = {"text/html": ["5.0"]}  # Supported mimetypes

    def __init__(self, well_formed):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from scraper
        """
        self._well_formed = well_formed

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "text/html" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """
        Return version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        return "5.0" if self._well_formed else UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV
