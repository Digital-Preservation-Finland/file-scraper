"""Schematron metadata model."""
from file_scraper.utils import metadata
from file_scraper.base import BaseMeta


class SchematronMeta(BaseMeta):
    """Metadata model for SchematronScraper."""

    _supported = {"text/xml": []}  # Supported mimetypes
    _allow_versions = True

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"
