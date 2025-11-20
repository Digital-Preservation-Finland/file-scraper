"""Metadata model for dummy extractors."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.state import Mimetype


class UserDefinedMeta(BaseMeta):
    """
    User defined metadata model. Supports only user supplied metadata.
    This metadata won't require any extractor since user defined metadata
    is instantly available.
    """

    _allow_any_version = True

    def __init__(self, mimetype: Mimetype):
        super().__init__()
        self._supported = {mimetype.mimetype: [mimetype.version]}
        self._mimetype = mimetype

    @BaseMeta.metadata(important=True)
    def mimetype(self) -> str:
        if self._mimetype.mimetype is None:
            return UNAV
        return self._mimetype.mimetype

    @BaseMeta.metadata(important=True)
    def version(self) -> str:
        if self._mimetype.version is None:
            return UNAV
        return self._mimetype.version


class DummyMeta(BaseMeta):
    """Minimal metadata model for dummy extractors."""

    @BaseMeta.metadata()
    def stream_type(self):
        """Stream type is not known so return (:unav)."""
        return UNAV


class ExtractorNotFoundMeta(BaseMeta):
    """
    Metadata model for ExtractorNotFound extractor. Otherwise minimal model,
    but allows setting mimetype and version, if detected.
    """

    def __init__(self, mimetype=None, version=None):
        """
        Initialize with given mimetype and version.

        :mimetype: File MIME type
        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type"""
        if self._mimetype:
            return self._mimetype
        return UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return the file format version"""
        if self._version:
            return self._version
        return UNAV


class DetectedMimeVersionMeta(BaseMeta):
    """
    This model results the given file format MIME type and version for some
    file formats. The corresponding extractor gets the version as a parameter
    originally from a detector and results it as a extractor value.

    We don't currently know any other constructive way to get file format
    version for a few formats.

    We also use this model for file formats for bit-level preservation,
    to avoid message about missing extractor.
    """

    _supported = {
        "application/epub+zip": ["2.0.1", "3"],
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2",
                                                    "1.3"],
        "application/vnd.oasis.opendocument.spreadsheet": [
            "1.0", "1.1", "1.2", "1.3"],
        "application/vnd.oasis.opendocument.presentation": [
            "1.0", "1.1", "1.2", "1.3"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2",
                                                        "1.3"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2", "1.3"],
        "application/x.fi-dpres.segy": ["(:unkn)", "1.0", "2.0"],
        "application/x.fi-dpres.atlproj": ["(:unap)"],
        "audio/ac3": ["(:unap)"]
    }

    def __init__(self, mimetype, version):
        """
        Initialize with given mimetype and version.

        :version: File format version
        """
        self._mimetype = mimetype
        self._version = version

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type"""
        if self._mimetype:
            return self._mimetype
        return UNAV

    @BaseMeta.metadata()
    def version(self):
        """Return the file format version"""
        return self._version if self._version is not None else UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""

        # AC-3 is an audio stream, the other supported formats are
        # binary formats
        if self.mimetype() == "audio/ac3":
            return "audio"

        return "binary" if self.mimetype() != UNAV else UNAV


class DetectedSpssVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for SPSS Portable files.

    We allow all versions.

    Full scraping actually is able to result the same, but this is needed
    when extractor is used for metadata collecting.

    """
    _supported = {
        "application/x-spss-por": []
    }
    _allow_any_version = True

    @BaseMeta.metadata()
    def version(self):
        """Return the file format version"""
        return UNAP


class DetectedSiardVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for SIARD files.

    This extractor collects MIME type, file format version and stream type
    for SIARD files. It is used both when detecting file formats and in
    full scraping, as the DBPTK-extractor for SIARD files does not provide
    file format version or stream type.

    We allow all versions.
    """
    _supported = {
        "application/x-siard": []
    }
    _allow_any_version = True


class DetectedTextVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for some text files.

    Full scraping actually is able to result the same, but this is needed
    when Extractor is used for metadata collecting.
    """
    _supported = {
        "text/html": ["4.01", "5"],
        "text/xml": ["1.0"],
    }

    @BaseMeta.metadata()
    def version(self):
        """Return version."""
        version = super().version()
        if version == UNAV and self.mimetype() == "text/xml":
            return "1.0"
        return version

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type."""
        return "text" if self.mimetype() != UNAV else UNAV


class DetectedPdfaVersionMeta(DetectedMimeVersionMeta):
    """
    Variation of DetectedMimeVersionMeta model for PDF/A files.

    We keep the version important.

    Full scraping actually is able to result the same, but this is needed
    when extractor is used for metadata collecting.
    """
    # Supported mimetypes and versions
    _supported = {"application/pdf": ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u",
                                      "A-3a", "A-3b", "A-3u"]}

    @BaseMeta.metadata(important=True)
    def version(self):
        """Return the file format version"""
        return self._version if self._version is not None else UNAV
