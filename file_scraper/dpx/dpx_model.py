"""DPX scraper"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata, ensure_text


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    # Supported mimetype and version
    _supported = {"image/x-dpx": ["2.0", "1.0"]}

    def __init__(self, errors, filename, messages):
        """Initialize metadata model."""
        self._errors = errors
        self._filename = filename
        self._messages = messages

    @metadata()
    def mimetype(self):
        """
        Return mimetype. The file is DPX xompliant if there are no errors.
        """
        return "image/x-dpx" if not self._errors else "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
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
