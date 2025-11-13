"""DPX extractor"""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV


class DpxMeta(BaseMeta):
    """Metadata model for dpx files."""

    # Supported mimetype and version
    _supported = {"image/x-dpx": ["2.0", "1.0"]}

    def __init__(self, well_formed, output, filename):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from DPX extractor
        :output: Messages given by DPX extractor
        :filename: DPX file name
        """
        self._well_formed = well_formed
        self._output = output
        self._filename = filename

    @BaseMeta.metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from extractor is False,
        then we do not know the actual MIME type.
        """
        return "image/x-dpx" if self._well_formed else UNAV

    @BaseMeta.metadata()
    def version(self):
        """
        Return file format version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if not self._well_formed:
            return UNAV

        for supported_version in self._supported["image/x-dpx"]:

            version_string = f"V{supported_version}"

            if version_string == self._output["version"]:
                return supported_version

        return UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "image" if self._well_formed else UNAV
