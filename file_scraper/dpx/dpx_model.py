"""DPX V2.0 scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    _supported = {"image/x-dpx": ["2.0"]}  # Supported mimetype and version

    # pylint: disable=no-self-use
    @metadata()
    def mimetype(self):
        return "image/x-dpx"

    @metadata()
    def version(self):
        """Return version."""
        return "2.0"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"
