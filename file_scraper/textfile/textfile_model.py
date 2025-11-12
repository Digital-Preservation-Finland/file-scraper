"""Metadata model for TextfileExtractor."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.metadata import metadata


class TextFileMeta(BaseMeta):
    """Text file metadata model."""

    _supported = {"text/plain": []}
    _allow_versions = True

    def __init__(self, well_formed):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from extractor
        """
        self._well_formed = well_formed

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the well-formed status from extractor is False,
        then we do not know the actual MIME type.
        """
        return "text/plain" if self._well_formed is not False else UNAV

    @metadata()
    def version(self):
        """Return version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        return UNAP if self._well_formed is not False else UNAV

    @metadata()
    def stream_type(self):
        """
        Return stream type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed is not False else UNAV


class TextEncodingMeta(BaseMeta):
    """Text encoding metadata model."""

    _supported = {"text/plain": [],
                  "text/csv": [],
                  "text/html": ["4.01", "5"],
                  "text/xml": ["1.0"],
                  "application/xhtml+xml": ["1.0", "1.1"]}
    _allow_versions = True

    def __init__(self, well_formed, charset, predefined_mimetype):
        """
        Initialize metadata model.

        :well_formed: Well-formed status from extractor
        :charset: Encoding from extractor
        :predefined_mimetype: Predefined mimetype
        """
        self._well_formed = well_formed
        self._charset = charset
        self._predefined_mimetype = predefined_mimetype

    @metadata()
    def mimetype(self):
        """
        Return mimetype only if text/plain expected and no errors occured.

        Other extractors are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if (self._predefined_mimetype == "text/plain" and
                self._well_formed is not False):
            return "text/plain"

        return UNAV

    @metadata()
    def version(self):
        """
        Return version only if text/plain expected and no errors occured.

        Other extractors are not able to figure out the mimetype for plain text
        files with some encodings, such as UTF-16 without BOM or UTF-32.
        """
        if (self._predefined_mimetype == "text/plain" and
                self._well_formed is not False):
            return UNAP
        return UNAV

    @metadata(important=True)
    def charset(self):
        """Return charset."""
        return self._charset

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "text"
