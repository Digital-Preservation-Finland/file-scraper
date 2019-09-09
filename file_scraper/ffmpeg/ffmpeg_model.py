"""Metadata model for FFMpeg scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class FFMpegSimpleMeta(BaseMeta):
    """
    A simple metadata class for not scraping any metadata using FFMpeg.

    See FFMpegMeta docstring for reasons to use this metadata model.
    """

    # Supported mimetypes
    _supported = {"video/mpeg": [], "video/mp4": [],
                  "audio/mpeg": [], "audio/mp4": [],
                  "video/MP1S": [], "video/MP2P": [],
                  "video/MP2T": [], "video/x-matroska": [],
                  "video/quicktime": [], "video/dv": []}
    _allow_versions = True   # Allow any version

    @metadata()
    def stream_type(self):
        """
        This metadata model scrapes nothing, return (:unav).
        """
        # pylint: disable=no-self-use
        return "(:unav)"
