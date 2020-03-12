"""Metadata models for files scraped using magic."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.defaults import MIMETYPE_DICT
from file_scraper.utils import metadata


class BaseMagicMeta(BaseMeta):
    """The base class for all metadata models using magic."""
    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None  # Text after file format version in magic result.

    def __init__(self, magic_result, pre_mimetype):
        """Initialize the metadata model.

        :magic_result: Values resulted from magic module as Python dict
        :pre_mimetype: Predefined mimetype
        """
        self._magic_result = magic_result
        self._predefined_mimetype = pre_mimetype

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        mimetype = self._magic_result['magic_mime_type']
        if mimetype in MIMETYPE_DICT:
            mimetype = MIMETYPE_DICT[mimetype]
        if mimetype == self._predefined_mimetype:
            return mimetype
        return "(:unav)"

    @metadata()
    def version(self):
        """Return file format version."""
        magic_version = self._magic_result['magic_none']
        if magic_version is not None:
            magic_version = magic_version.split(self._starttag)[-1]
        if self._endtag:
            magic_version = magic_version.split(self._endtag)[0]
        if magic_version == "data":
            return "(:unav)"
        return magic_version


class BinaryMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of binary files."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class TextMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of text files."""

    @metadata()
    def charset(self):
        """Return charset."""
        magic_charset = self._magic_result['magic_mime_encoding']

        if magic_charset is None or magic_charset.upper() == "BINARY":
            return "(:unav)"
        if magic_charset.upper() == "US-ASCII":
            return "UTF-8"
        if magic_charset.upper() == "ISO-8859-1":
            return "ISO-8859-15"
        if magic_charset.upper() == "UTF-16LE" \
                or magic_charset.upper() == "UTF-16BE":
            return "UTF-16"

        return magic_charset.upper()

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"


class TextFileMagicMeta(TextMagicBaseMeta):
    """Metadata models for plain text and csv files."""

    _supported = {"text/plain": [], "text/csv": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "(:unap)"
        return "(:unav)"


class XmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xml files."""

    _supported = {"text/xml": ["1.0"]}  # Supported mimetypes
    _starttag = "XML "             # Text before version in magic output
    _endtag = " "                  # Text after version in magic output
    _allow_versions = True         # Allow any version

    @classmethod
    def is_supported(cls, magic_result, version=None,
                     params=None):
        """
        Return True if given MIME type and version are supported.

        This is not a Schematron scraper, skip this in such case.

        :magic_result: Values resulted from magic module as dict
        :version: Identified version (if needed)
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" in params:
            return False
        return super(XmlFileMagicMeta, cls).is_supported(magic_result, version,
                                                         params)

    @metadata()
    def version(self):
        """
        Return the XML version.

        For some files, e.g. XML files without header, the version might not be
        successfully determined. In those cases, the field used for determining
        the version can contain e.g. "ASCII text, with very long lines",
        resulting in the version being "ASCII". As XML versions are always
        decimal numbers, non-numerical outputs should not be returned.

        We do not currently support XML 1.1. in dPres specifications.
        """
        version = super(XmlFileMagicMeta, self).version()
        try:
            if version not in ["1.0"]:
                raise ValueError(
                    "Invalid version '{}'. "
                    "XML version must be '1.0'.".format(version))
            return version
        except ValueError:
            return "(:unav)"


class XhtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xhtml files."""

    # Supported mimetypes
    _supported = {"application/xhtml+xml": ["1.0", "1.1"]}
    _starttag = "XML "      # Text before version in magic output
    _endtag = " "           # Text after version in magic output
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        mime = self._magic_result['magic_mime_type']
        if mime in ["application/xml", "text/xml", "text/html",
                    "application/xhtml+xml"]:
            return "application/xhtml+xml"
        return "(:unav)"


class HtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for html files."""

    # Supported mimetypes
    _supported = {"text/html": ["4.01", "5.0"]}

    @metadata()
    def version(self):
        """Return version."""
        return "(:unav)"


class PdfFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PDF files."""

    # Supported mimetype
    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}
    _allow_versions = True  # Allow any version


class OfficeFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for office files."""

    # Supported mimetypes and versions
    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.spreadsheet": ["1.0", "1.1",
                                                           "1.2"],
        "application/vnd.oasis.opendocument.presentation": ["1.0", "1.1",
                                                            "1.2"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2"],
        "application/msword": ["8.0", "8.5", "9.0", "10.0", "11.0"],
        "application/vnd.ms-excel": ["8.0", "9.0", "10.0", "11.0"],
        "application/vnd.ms-powerpoint": ["8.0", "9.0", "10.0", "11.0"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": ["12.0", "14.0", "15.0"],
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet": ["12.0", "14.0", "15.0"],
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": ["12.0", "14.0", "15.0"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        return "(:unav)"


class ArcFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for Arc files."""

    # Supported mimetype
    _supported = {"application/x-internet-archive": ["1.0", "1.1"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        magic_mimetype = super(ArcFileMagicMeta, self).mimetype()
        if magic_mimetype == "application/x-ia-arc":
            return "application/x-internet-archive"
        return magic_mimetype

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return "(:unav)"
        version = super(ArcFileMagicMeta, self).version()
        if version == "1":
            version = "1.0"
        return version


class WarcFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for Arc files."""

    # Supported mimetype
    _supported = {"application/warc": ["0.17", "0.18", "1.0"]}
    _allow_versions = True  # Allow any version
    _endtag = "\\"

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return "(:unav)"
        return super(WarcFileMagicMeta, self).version()


class PngFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PNG files."""

    _supported = {"image/png": ["1.2"]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "1.2"
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class JpegFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JPEG files."""

    _supported = {"image/jpeg": ["1.00", "1.01", "1.02", "2.0", "2.1",
                                 "2.2", "2.2.1"]}  # Supported mimetype
    _starttag = "standard "  # Text before version in magic output
    _endtag = ","            # Text after version in magic output
    _allow_versions = True   # Allow any version

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class Jp2FileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JP2 files."""

    _supported = {"image/jp2": [""]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "(:unap)"
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class TiffFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for TIFF files."""

    _supported = {"image/tiff": ["6.0"]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "6.0"
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class GifFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for GIF files."""

    _supported = {"image/gif": ["1987a", "1989a"]}
    _allow_versions = True
    _endtag = ","

    @metadata()
    def version(self):
        """Return version."""
        version = super(GifFileMagicMeta, self).version()
        if version in ["87a", "89a"]:
            return "19" + version
        return version

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"
