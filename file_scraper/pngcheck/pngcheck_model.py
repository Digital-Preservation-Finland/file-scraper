"""Module for pngcheck scraper."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class PngcheckMeta(BaseMeta):
    """
    Metadata model for png files.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported = {"image/png": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """We do not need to resolve stream type."""
        return UNAV
