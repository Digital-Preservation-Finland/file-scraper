"""Metadata models for JHove"""

try:
    import mimeparse
except ImportError:
    pass

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.utils import metadata

NAMESPACES = {"j_harvard": "http://hul.harvard.edu/ois/xml/ns/jhove",
              "j_opf": "http://schema.openpreservation.org/ois/xml/ns/jhove",
              "aes": "http://www.aes.org/audioObject"}


def get_field(report, field):
    """
    Return the value of a field from the given JHoves XML output.

    :report: JHOVE XML report
    :field: Element name from the XML report
    :returns: The value of the field (multiple values separated by a newline)
              or None if the report was None or field was not found in it.
    """
    if report is None:
        return UNAV
    query = f"(//j_harvard:{field} | //j_opf:{field})/text()"
    results = report.xpath(query, namespaces=NAMESPACES)
    if not results:
        return UNAV
    return "\n".join(results)


class JHoveBaseMeta(BaseMeta):
    """Metadata that is common for all files scraped using JHove"""

    def __init__(self, well_formed, report):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from extractor
        :report: JHove output as lxml.etree
        """
        self._well_formed = well_formed
        self._report = report

    @metadata()
    def mimetype(self):
        """Return mimetype given by JHove."""
        return get_field(self._report, "mimeType")


class JHoveGifMeta(JHoveBaseMeta):
    """Metadata model for gif files scraped with JHove"""

    _supported = {"image/gif": ["1987a", "1989a"]}
    _allow_versions = True

    @metadata()
    def version(self):
        """
        Return version.

        Jhove returns the version as "87a" or "89a" but "1987a"
        or "1989a" is used. Hence "19" is prepended to the version returned by
        Jhove.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if not self._well_formed:
            return UNAV
        if get_field(self._report, "version") in ["87a", "89a"]:
            return "19" + get_field(self._report, "version")
        return UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "image" if self._well_formed else UNAV


class JHoveHtmlMeta(JHoveBaseMeta):
    """Metadata model for HTML files scraped with JHove"""

    _supported = {"text/html": ["4.01"],
                  "application/xhtml+xml": ["1.0", "1.1"]}

    @metadata(important=True)
    def version(self):
        """
        Return version.

        Jhove returns the version as "HTML 4.01" but only the "4.01" part is
        used. Hence we drop "HTML " prefix from the string returned by Jhove.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if not self._well_formed:
            return UNAV
        version = get_field(self._report, "version")
        if version:
            version = version.split()[-1]
        return version

    def _get_charset_html(self):
        """Get the charset from the JHove report for HTML files."""
        query = ('(//j_harvard:property[j_harvard:name="Content"]//j_harvard:'
                 'value | //j_opf:property[j_opf:name="Content"]//j_opf:'
                 'value)/text()')
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            result_mimetype = mimeparse.parse_mime_type(results[0])
            params = result_mimetype[2]
            return params.get("charset")
        except (mimeparse.MimeTypeParseException, IndexError):
            return UNAV

    def _get_charset_xml(self):
        """Get the charset from the JHove report for XHTML files."""
        query = ('(//j_harvard:property[j_harvard:name="Encoding"]//j_harvard:'
                 'value | //j_opf:property[j_opf:name="Encoding"]//j_opf:'
                 'value)/text()')
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            return results[0]
        except IndexError:
            return UNAV

    @metadata()
    def mimetype(self):
        """
        Return MIME type.

        If the well-formed status from extractor is False,
        then we do not know the actual MIME type.
        """
        if not self._well_formed:
            return UNAV
        mime = super().mimetype()
        if mime == "text/xml" and \
                get_field(self._report, "format") == "XHTML":
            return "application/xhtml+xml"
        return mime

    @metadata()
    def charset(self):
        """Get the charset from HTML/XML files."""
        if self._report is None:
            return UNAV
        if "xml" in self.mimetype():
            return self._get_charset_xml()
        return self._get_charset_html()

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV


class JHoveJpegMeta(JHoveBaseMeta):
    """Metadata model for jpeg files scraped with JHove"""

    _supported = {"image/jpeg": ["1.00", "1.01", "1.02", "2.0",
                                 "2.1", "2.2", "2.2.1"]}
    _allow_versions = True

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "image" if self._well_formed else UNAV


class JHoveTiffMeta(JHoveBaseMeta):
    """Metadata model for tiff files scraped with JHove"""

    _supported = {"image/tiff": ["6.0"]}
    _allow_versions = True

    @metadata()
    def version(self):
        """
        Return version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        return "6.0" if self._well_formed else UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "image" if self._well_formed else UNAV


class JHovePdfMeta(JHoveBaseMeta):
    """Metadata model for pdf files scraped with JHove"""

    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}

    @metadata()
    def version(self):
        """
        Return version.

        We want to always return the version, since JHove can read the version
        number even from PDF versions it does not fully support and thus might
        erroneously claim are not well-formed. Actually invalid files have
        their version marked as UNAV since the field is missing from the JHove
        report.
        """
        return get_field(self._report, "version")

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class JHoveWavMeta(JHoveBaseMeta):
    """Metadata model for wav files scraped with JHove"""

    _supported = {"audio/x-wav": ["", "2"]}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """
        Return mimetype.

        The mimeType element for WAV files can also include other information,
        separated from the actual mimetype by a semicolon. This extra
        information is ignored.

        If the MIME type is a WAV type, audio/vnd.wave is returned, otherwise
        the same method from the superclass is called.
        """
        mimetype_element = get_field(self._report, "mimeType")
        if mimetype_element:
            # There's a maximum of one semicolon and the string is short, so we
            # wouldn't really get a performance boost.
            # pylint: disable=use-maxsplit-arg
            reported_mimetype = mimetype_element.split(";")[0]
            if reported_mimetype == "audio/vnd.wave":
                return "audio/x-wav"

        return super().mimetype()

    @metadata(important=True)
    def version(self):
        """
        Return version.

        Set version as "2" or "(:unap)" if profile is BWF or PCMWAVEFORMAT,
        respectively. For now, we don't accept RF64.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if not self._well_formed:
            return UNAV

        profile = get_field(self._report, "profile")
        if profile is None:
            return UNAV
        if "RF64" in profile:
            return UNAV
        if "BWF" in profile:
            return "2"
        if "PCMWAVEFORMAT" in profile:
            return UNAP

        return UNAV

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "audio" if self._well_formed else UNAV


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

    @metadata()
    def charset(self):
        """Return charset from JHOVE."""
        if "Well-formed and valid" in get_field(self._report, "status"):
            return "UTF-8"
        return get_field(self._report, "format")

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "text" if self._well_formed else UNAV

    @metadata()
    def mimetype(self):
        """We don't know the mimetype."""
        return UNAV

    @metadata()
    def version(self):
        """We don't know the version."""
        return UNAV


class JHoveEpubMeta(JHoveBaseMeta):
    """Metadata model for EPUB files scraped with JHove"""

    _supported = {"application/epub+zip": ["2.0.1", "3"]}

    @metadata()
    def version(self):
        """
        Return version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if self._well_formed:
            jhove_version = get_field(self._report, "version")
            # Map all versions 3.x to 3
            if jhove_version.startswith("3."):
                return "3"
            return jhove_version
        return UNAV

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class JHoveDngMeta(JHoveBaseMeta):
    """Metadata model for dng files scraped with JHove"""

    _supported = {"image/x-adobe-dng": []}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        mime = super().mimetype()
        if mime == "image/tiff":
            return "image/x-adobe-dng"
        return mime

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image" if self._well_formed else UNAV


class JHoveAiffMeta(JHoveBaseMeta):
    """Metadata model for AIFF files scraped with JHove"""

    _supported = {"audio/x-aiff": ["", "1.3"]}
    _allow_versions = True

    @metadata()
    def stream_type(self):
        """
        Return file type.

        If the well-formed status from extractor is False,
        then we do not know the actual stream type.
        """
        return "audio" if self._well_formed else UNAV

    @metadata()
    def version(self):
        """
        Set version as "1.3" or "(:unap)" if profile is AIFF or AIFF-C
        respectively.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        profile = get_field(self._report, "profile")
        if profile is None:
            return UNAV
        if "AIFF-C" in profile:
            return UNAP
        if "AIFF" in profile:
            return "1.3"
        return UNAV
