"""Metadata models for files scraped using magic."""
from __future__ import unicode_literals

import ctypes

import six

from file_scraper.base import BaseMeta
from file_scraper.defaults import MIMETYPE_DICT
from file_scraper.utils import encode_path, metadata

try:
    from file_scraper.defaults import MAGIC_LIBRARY

    ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
except OSError:
    print("%s not found, MS Office detection may not work properly if "
          "file command library is older." % MAGIC_LIBRARY)
try:
    import magic as magic
except ImportError:
    pass


class BaseMagicMeta(BaseMeta):
    """The base class for all metadata models using magic."""
    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None  # Text after file format version in magic result.

    def __init__(self, filename, errors, mimetype=None, version=None):
        """Imitialize the metadata model."""
        self._filename = filename
        self._errors = errors
        super(BaseMagicMeta, self).__init__(mimetype=mimetype, version=version)

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype

        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            mimetype = magic_.file(encode_path(self._filename))
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analysing file")
            self._errors.append(six.text_type(exception))
            return None
        finally:
            magic_.close()

        if mimetype in MIMETYPE_DICT:
            mimetype = MIMETYPE_DICT[mimetype]
        return mimetype

    @metadata()
    def version(self):
        if self._given_mimetype and self._given_version:
            return self._given_version

        try:
            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            magic_version = magic_.file(
                encode_path(self._filename)).split(self._starttag)[-1]
            magic_version = six.text_type(magic_version)
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analysing file")
            self._errors.append(six.text_type(exception))
            return None
        finally:
            magic_.close()

        if self._endtag:
            return magic_version.split(self._endtag)[0]
        return magic_version


class BinaryMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of binary files."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        magic_version = super(BinaryMagicBaseMeta, self).version()
        if magic_version == "data":
            return None
        return magic_version


class TextMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of text files."""

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        version = super(TextMagicBaseMeta, self).version()
        if version == "data":
            return None
        return version

    @metadata()
    def charset(self):
        """Return charset."""
        try:
            magic_ = magic.open(magic.MAGIC_MIME_ENCODING)
            magic_.load()
            magic_charset = magic_.file(encode_path(self._filename))
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analyzing file")
            self._errors.append(six.text_type(exception))
            return None
        finally:
            magic_.close()

        if magic_charset is None or magic_charset.upper() == "BINARY":
            return None
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
    """Metadata models for plaintext and csv files."""

    _supported = {"text/plain": [], "text/csv": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        return "(:unap)"


class XmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xml files."""

    _supported = {"text/xml": ["1.0"]}  # Supported mimetypes
    _starttag = "XML "             # Text before version in magic output
    _endtag = " "                  # Text after version in magic output
    _allow_versions = True         # Allow any version

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     params=None):
        """
        Return True if given MIME type and version are supported.

        This is not a Schematron scraper, skip this in such case.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" in params:
            return False
        return super(XmlFileMagicMeta, cls).is_supported(mimetype, version,
                                                         params)


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
        mime = super(XhtmlFileMagicMeta, self).mimetype()
        if mime == "text/xml":
            return "application/xhtml+xml"
        return mime


class HtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for html files."""

    # Supported mimetypes
    _supported = {"text/html": ["4.01", "5.0"]}

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

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
        if self._given_mimetype and self._given_version:
            return self._given_version

        return "(:unav)"


class ArcFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for Arc files."""

    # Supported mimetype
    _supported = {"application/x-internet-archive": ["1.0", "1.1"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        if self._given_mimetype:
            return self._given_mimetype

        magic_mimetype = super(ArcFileMagicMeta, self).mimetype()
        if magic_mimetype == "application/x-ia-arc":
            return "application/x-internet-archive"
        return magic_mimetype

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        if self.mimetype() not in self._supported:
            return None
        version = super(ArcFileMagicMeta, self).version()
        if version == "1":
            version = "1.0"
        return version


class PngFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PNG files."""

    _supported = {"image/png": ["1.2"]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version

        if self.mimetype() not in self._supported:
            return None
        return "1.2"

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
        if self._given_mimetype and self._given_version:
            return self._given_version

        if self.mimetype() not in self._supported:
            return None
        return ""

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
        if self._given_mimetype and self._given_version:
            return self._given_version

        if self.mimetype() not in self._supported:
            return None
        return "6.0"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"
