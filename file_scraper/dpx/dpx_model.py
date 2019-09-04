"""DPX V2.0 scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata, ensure_text


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    # Supported mimetype and version
    _supported = {"image/x-dpx": ["2.0", "1.0"]}

    def __init__(self, **kwargs):

        super(DpxMeta, self).__init__(kwargs["mimetype"], kwargs["version"])
        self.messages = kwargs["info"]["messages"]
        self.filename = ensure_text(kwargs["filename"])

    # pylint: disable=no-self-use
    @metadata()
    def mimetype(self):
        if self._given_mimetype:
            return self._given_mimetype
        return "image/x-dpx"

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        for _version in self._supported["image/x-dpx"]:
            if self.version_string(_version) in self.messages:
                return _version

        return super(DpxMeta, self).version()

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"

    def version_string(self, version):
        """Validator output line about DPX version."""

        return "File {} validated as V{}".format(self.filename, version)
