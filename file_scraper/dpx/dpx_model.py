"""DPX scraper"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata, ensure_text


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    # Supported mimetype and version
    _supported = {"image/x-dpx": ["2.0", "1.0"]}

    def __init__(self, errors, messages, filename):
        """
        Initialize metadata model.
        
        :errors: Errors given by DPX scraper
        :messages: Messages given by DPX scraper
        :filename: DPX file name
        """
        self._errors = errors
        self._messages = messages
        self._filename = filename

    @metadata()
    def mimetype(self):
        """
        Return mimetype.
        
        The file is DPX compliant if there are no errors, and this will be
        returned only if predefined as DPX.
        """
        return "image/x-dpx" if not self._errors else "(:unav)"

    @metadata()
    def version(self):
        """Return version. The version is returned, if there are no errors."""
        if self._errors:
            return "(:unav)"

        for supported_version in self._supported["image/x-dpx"]:

            version_string = "File {}: Validated as V{}".format(
                ensure_text(self._filename), supported_version)

            if version_string in self._messages:
                return supported_version

        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"
