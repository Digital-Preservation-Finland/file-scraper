"""Metadata model for FFMpeg scraper."""
from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class FFMpegMeta(BaseMeta):
    """
    Metadata model for a selection of video files.

    This metadata model is used with mpeg, mp4, MP1s, MP2T, MP2P, quicktime,
    matroska and dv files.
    """

    # Supported mimetypes
    _supported = {"video/mpeg": [], "video/mp4": [],
                  "audio/mpeg": [], "audio/mp4": [],
                  "video/MP1S": [], "video/MP2P": [],
                  "video/MP2T": [], "video/x-matroska": [],
                  "video/quicktime": [], "video/dv": []}
    _allow_versions = True   # Allow any version

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return None
