"""Metadata models for JHove"""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata

NAMESPACES = {"j": "http://hul.harvard.edu/ois/xml/ns/jhove",
              "aes": "http://www.aes.org/audioObject"}


def get_field(report, field):
    """
    Return the value of a field from the given JHoves XML output.

    :returns: The value of the field (multiple values separated by a newline)
              or None if the report was None or field was not found in it.
    """
    if report is None:
        return None
    query = "//j:%s/text()" % field
    results = report.xpath(query, namespaces=NAMESPACES)
    if not results:
        return None
    return "\n".join(results)


class JHoveBaseMeta(BaseMeta):
    """Metadata that is common for all files scraped using JHove"""

    def __init__(self, report, errors, mimetype=None, version=None):
        """
        Initialize the metadata model.

        :report: JHove output as lxml.etree
        :errors: A list to which possible errors should be appended
        """
        self._report = report
        self._errors = errors
        super(JHoveBaseMeta, self).__init__(mimetype, version)

    @metadata()
    def mimetype(self):
        """Return mimetype given by JHove."""
        if self._given_mimetype:
            return self._given_mimetype
        return get_field(self._report, "mimeType")


class JHoveGifMeta(JHoveBaseMeta):
    """Metadata model for gif files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"image/gif": ["1987a", "1989a"]}
    _allow_versions = True

    @metadata()
    def version(self):
        """
        Return version.

        Jhove returns the version as "87a" or "89a" but "1987a"
        or "1989a" is used. Hence "19" is prepended to the version returned by
        Jhove
        """
        if self._given_mimetype and self._given_version:
            return self._given_version

        if get_field(self._report, "version"):
            return "19" + get_field(self._report, "version")
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"


class JHoveHtmlMeta(JHoveBaseMeta):
    """Metadata model for HTML files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"text/html": ["4.01"],
                  "application/xhtml+xml": ["1.0", "1.1"]}

    @metadata()
    def version(self):
        """
        Return version.

        Jhove returns the version as "HTML 4.01" but only the "4.01" part is
        used. Hence we drop "HTML " prefix from the string returned by Jhove
        """
        if self._given_mimetype and self._given_version:
            return self._given_version

        version = get_field(self._report, "version")
        if version:
            version = version.split()[-1]
        return version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        if self._given_mimetype:
            return self._given_mimetype

        mime = super(JHoveHtmlMeta, self).mimetype()
        if mime == "text/xml":
            return "application/xhtml+xml"
        return mime

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"


class JHoveJpegMeta(JHoveBaseMeta):
    """Metadata model for jpeg files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"image/jpeg": ["1.00", "1.01", "1.02", "2.0",
                                 "2.1", "2.2", "2.2.1"]}
    _allow_versions = True

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"


class JHoveTiffMeta(JHoveBaseMeta):
    """Metadata model for tiff files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"image/tiff": ["6.0"]}
    _allow_versions = True

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version
        return "6.0"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "image"


class JHovePdfMeta(JHoveBaseMeta):
    """Metadata model for pdf files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "A-1a", "A-1b"]}

    @metadata()
    def version(self):
        """Return version."""
        if self._given_mimetype and self._given_version:
            return self._given_version
        return get_field(self._report, "version")

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class JHoveWavMeta(JHoveBaseMeta):
    """Metadata model for wav files scraped with JHove"""
    # pylint: disable=no-self-use

    _supported = {"audio/x-wav": ["2"]}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        If the MIME type is a WAV type, audio/vnd.wave is returned, otherwise
        the same method from the superclass is called.
        """
        if self._given_mimetype:
            return self._given_mimetype

        if get_field(self._report, "mimeType") is not None and \
                (get_field(self._report, "mimeType").split(";")[0]
                 == "audio/vnd.wave"):
            return "audio/x-wav"

        return super(JHoveWavMeta, self).mimetype()

    @metadata()
    def version(self):
        """
        Return version.

        Set version as "2" if profile is BWF, otherwise we don"t know.
        For now, we don"t accept RF64.
        """
        if self._given_mimetype and self._given_version:
            return self._given_version

        if get_field(self._report, "profile") is None:
            return "(:unav)"
        if "RF64" in get_field(self._report, "profile"):
            self._errors.append("RF64 is not a supported format")
        elif "BWF" in get_field(self._report, "profile"):
            return "2"

        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "audio"


class JHoveUtf8Meta(JHoveBaseMeta):
    """
    Metadata model for UTF-8 text.

    We don't want to run this for all files, but just for UTF-8 text files
    separately. This must be run after actual scraping, since we have to know
    the charset of the file.
    """

    _supported = {}  # We will not run at normal stage
    _only_wellformed = True  # Only well-formed check
    _jhove_module = "UTF8-hul"  # JHove module

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"

    @metadata()
    def mimetype(self):
        return "(:unav)"

    @metadata()
    def version(self):
        return "(:unav)"
