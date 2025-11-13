"""Schematron metadata model."""

from file_scraper.defaults import UNAV

from file_scraper.base import BaseMeta


class SchematronMeta(BaseMeta):
    """Metadata model for SchematronExtractor."""

    _supported = {"text/xml": []}  # Supported mimetypes
    _allow_versions = True

    def __init__(self, well_formed):
        """
        Initialize metadata model.

        :well_formed: Schematron well-formedness of XML file
        """
        self._well_formed = well_formed

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type."""
        return "text/xml" if self._well_formed else UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return file format version."""
        return "1.0" if self._well_formed else UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "text" if self._well_formed else UNAV
