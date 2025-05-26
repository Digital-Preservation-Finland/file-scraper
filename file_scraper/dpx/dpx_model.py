"""DPX scraper"""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata, ensure_text


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    # Supported mimetype and version
    _supported = {"image/x-dpx": ["2.0", "1.0"]}

    def __init__(self, well_formed, messages, filename):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from DPX scraper
        :messages: Messages given by DPX scraper
        :filename: DPX file name
        """
        self._well_formed = well_formed
        self._messages = messages
        self._filename = filename

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from scraper is False,
        then we do not know the actual MIME type.
        """
        return "image/x-dpx" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """
        Return file format version.

        If the well-formed status from scraper is False,
        then we do not know the actual version.
        """
        if not self._well_formed:
            return UNAV

        for supported_version in self._supported["image/x-dpx"]:

            version_string = (f"File {ensure_text(self._filename)}: Validated "
                              f"as V{supported_version}")

            if version_string in self._messages:
                return supported_version

        return UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from scraper is False,
        then we do not know the actual stream type.
        """
        return "image" if self._well_formed else UNAV
