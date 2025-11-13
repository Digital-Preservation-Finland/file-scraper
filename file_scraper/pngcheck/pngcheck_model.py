"""Module for pngcheck extractor."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV


class PngcheckMeta(BaseMeta):
    """
    Metadata model for png files.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported = {"image/png": []}  # Supported mimetype
    _allow_any_version = True

    @BaseMeta.metadata()
    def stream_type(self):
        """We do not need to resolve stream type."""
        return UNAV
