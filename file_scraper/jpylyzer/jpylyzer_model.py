"""Metadata model for jp2 files."""
from file_scraper.base import BaseMeta


class JpylyzerMeta(BaseMeta):
    """Metadata model for jp2 files."""

    _supported = {"image/jp2": []}
    _allow_versions = True   # Allow any version
