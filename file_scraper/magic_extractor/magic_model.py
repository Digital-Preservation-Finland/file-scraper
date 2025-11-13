"""Metadata models for files scraped using magic."""
import re

from file_scraper.base import BaseMeta
from file_scraper.defaults import MIMETYPE_DICT, UNAP, UNAV

from file_scraper.utils import normalize_charset


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

    @BaseMeta.metadata()
    def mimetype(self):
        """
        Return MIME type.

        If the mimetype returned by magic is present as a key in MIMETYPE_DICT,
        its value is returned instead of that reported by magic.
        """
        mimetype = self._magic_result['magic_mime_type']

        # DV detection with unpatched file library
        mime_check = mimetype == "application/octet-stream"
        dv_magic_result = "DIF (DV) movie file (PAL)"
        magic_check = self._magic_result['magic_none'] == dv_magic_result
        if mime_check and magic_check:
            mimetype = "video/x-dv"

        mimetype = MIMETYPE_DICT.get(mimetype, mimetype)
        if mimetype == self._predefined_mimetype:
            return mimetype
        return UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return file format version."""
        magic_version = self._magic_result['magic_none']
        if magic_version is not None:
            magic_version = magic_version.split(self._starttag)[-1]
        if self._endtag:
            magic_version = magic_version.split(self._endtag)[0]
        if magic_version == "data":
            return UNAV
        return magic_version


class BinaryMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of binary files."""

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class TextMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of text files."""

    @BaseMeta.metadata()
    def charset(self):
        """Return charset."""
        magic_charset = self._magic_result['magic_mime_encoding']
        return normalize_charset(magic_charset)

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "text"


class TextFileMagicMeta(TextMagicBaseMeta):
    """Metadata models for plain text and csv files."""

    _supported = {"text/plain": [], "text/csv": [], "application/json": []}
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        return UNAP


class XmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xml files."""

    _supported = {"text/xml": ["1.0"]}  # Supported mimetypes
    _starttag = "XML "             # Text before version in magic output
    _endtag = " "                  # Text after version in magic output
    _allow_versions = True         # Allow any version

    @BaseMeta.metadata()
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
        version = super().version()
        try:
            if version not in ["1.0"]:
                raise ValueError(
                    f"Invalid version '{version}'. XML version must be '1.0'.")
            return version
        except ValueError:
            return UNAV


class XhtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xhtml files."""

    # Supported mimetypes
    _supported = {"application/xhtml+xml": ["1.0", "1.1"]}
    _starttag = "XML "      # Text before version in magic output
    _endtag = " "           # Text after version in magic output
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type."""
        mime = self._magic_result['magic_mime_type']
        if mime in ["application/xml", "text/xml", "text/html",
                    "application/xhtml+xml"]:
            return "application/xhtml+xml"
        return UNAV


class HtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for html files."""

    # Supported mimetypes
    _supported = {"text/html": ["4.01", "5"]}

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        return UNAV


class PdfFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PDF files."""

    # Supported mimetype
    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def version(self):
        """Return PDF file format version."""
        # In EL9 "file" can return (password protected) for a valid A-1a even
        # though the file is not password protected. What it should return is
        # that the file uses deflate. See
        # https://bugzilla.redhat.com/show_bug.cgi?id=2213761
        # After EL9, "file" will also list the amount of pages for the PDF.
        # This regex will return only the version number without any of the
        # extra information that "file" gives.
        orig_version = super().version()
        filtered_version = re.match(r'(\d+\.\d+)', orig_version)
        if filtered_version is not None:
            return filtered_version.group(1)

        return orig_version


class OfficeFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for office files."""

    # Supported mimetypes and versions
    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2",
                                                    "1.3"],
        "application/vnd.oasis.opendocument.spreadsheet": ["1.0", "1.1",
                                                           "1.2", "1.3"],
        "application/vnd.oasis.opendocument.presentation": ["1.0", "1.1",
                                                            "1.2", "1.3"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2",
                                                        "1.3"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2", "1.3"],
        "application/msword": ["97-2003"],
        "application/vnd.ms-excel": ["8X"],
        "application/vnd.ms-powerpoint": ["97-2003"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": ["2007 onwards"],
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet": ["2007 onwards"],
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": ["2007 onwards"]}
    _allow_versions = True  # Allow any version

    _mimes_unav_versions = [
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/vnd.oasis.opendocument.graphics",
        "application/vnd.oasis.opendocument.formula",
    ]

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            if self.mimetype() in self._mimes_unav_versions:
                return UNAV
            return self._supported[self.mimetype()][0]
        return UNAV


class PngFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PNG files."""

    _supported = {"image/png": ["1.2"]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "1.2"
        return UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class AiffFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for AIFF files."""

    _supported = {"audio/x-aiff": ["", "1.3"]}  # Supported mimetype
    _allow_versions = True   # Allow any version

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "audio"

    @BaseMeta.metadata()
    def version(self):
        """Return version based on if the data is an AIFF audio type
        or an AIFF-C compressed audio type.

        AIFF audio format version is hard coded to 1.3, since earlier
        format versions relate to the Apple II file type note
        implementation and were deprecated almost immediately in favor
        of version 1.3.

        AIFF-C compressed audio format
        """

        if 'aiff-c' in self._magic_result['magic_none'].lower():
            return UNAP
        if 'aiff audio' in self._magic_result['magic_none'].lower():
            return '1.3'
        return UNAV


class JpegFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JPEG files."""

    _supported = {"image/jpeg": ["1.00", "1.01", "1.02", "2.0", "2.1",
                                 "2.2", "2.2.1"]}  # Supported mimetype
    _starttag = "standard "  # Text before version in magic output
    _endtag = ","            # Text after version in magic output
    _allow_versions = True   # Allow any version

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"

    @BaseMeta.metadata()
    def version(self):
        """Return JFIF version when available. Version is determined as in
        BaseMagicMeta version() unless the file has been identified as
        Exif standard. The character case in the result is dependent on
        the version of the magic library, and therefore we handle this
        case-independently."""

        exif_magic_line = "jpeg image data, exif standard"

        if self._magic_result['magic_none'].lower().startswith(
                exif_magic_line):
            return UNAV
        return super().version()


class Jp2FileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JP2 files."""

    _supported = {"image/jp2": [""]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return UNAP
        return UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class TiffFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for TIFF files."""

    _supported = {"image/tiff": ["6.0"]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        if self.mimetype() in self._supported:
            return "6.0"
        return UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class GifFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for GIF files."""

    _supported = {"image/gif": ["1987a", "1989a"]}
    _allow_versions = True
    _endtag = ","

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        version = super().version()
        if version in ["87a", "89a"]:
            return "19" + version
        return version

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"
