"""Module for scraping files with Jhove scraper."""

try:
    import mimeparse
except ImportError:
    pass

from file_scraper.jhove_base import JHove
from file_scraper.utils import metadata

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}


class GifJHove(JHove):
    """JHove GIF file format scraper."""

    # Suported mimetype and versions
    _supported = {'image/gif': ['1987a', '1989a']}
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'GIF-hul'  # JHove module
    _allow_versions = True  # Allow any version

    @metadata()
    def _version(self):
        """
        Return version.

        Jhove returns the version as '87a' or '89a' but '1987a'
        or '1989a' is used. Hence '19' is prepended to the version returned by
        Jhove
        """
        if self.report_field("version"):
            return '19' + self.report_field("version")
        return None

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'image'


class HtmlJHove(JHove):
    """Jhove HTML file format scraper."""

    # Supported mimetypes and versions
    _supported = {'text/html': ['4.01'],
                  'application/xhtml+xml': ['1.0', '1.1']}
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'HTML-hul'  # JHove module

    @metadata()
    def _version(self):
        """
        Return version.

        Jhove returns the version as 'HTML 4.01' but in '4.01' is
        used. Hence we drop 'HTML ' prefix from the string returned by Jhove
        """
        version = self.report_field("version")
        if version:
            version = version.split()[-1]
        return version

    def _get_charset_html(self):
        """Get the charset from the JHove report for HTML files."""
        query = '//j:property[j:name="Content"]//j:value/text()'
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            result_mimetype = mimeparse.parse_mime_type(results[0])
            params = result_mimetype[2]
            return params.get('charset')
        except mimeparse.MimeTypeParseException:
            return None
        except IndexError:
            return None

    def _get_charset_xml(self):
        """Get the charset from the JHove report for XHTML files."""
        query = '//j:property[j:name="Encoding"]//j:value/text()'
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            return results[0]
        except IndexError:
            return None

    @metadata()
    def _mimetype(self):
        """Return MIME type."""
        mime = super(HtmlJHove, self)._mimetype()
        if mime == 'text/xml':
            return 'application/xhtml+xml'
        return mime

    @metadata()
    def _charset(self):
        """Get the charset from HTML/XML files."""
        if "xml" in self.mimetype:
            return self._get_charset_xml()
        return self._get_charset_html()

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'text'


class JpegJHove(JHove):
    """JHove scraper for JPEG."""

    # Suported mimetype and versions
    _supported = {'image/jpeg': ['1.00', '1.01', '1.02', '2.0',
                                 '2.1', '2.2', '2.2.1']}
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'JPEG-hul'  # JHove module
    _allow_versions = True  # Allow any version

    @metadata()
    def _version(self):
        """Return version."""
        return None

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'image'


class TiffJHove(JHove):
    """JHove scraper for TIFF."""

    _supported = {'image/tiff': ['6.0']}  # Supported mimetype
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'TIFF-hul'  # JHove module
    _allow_versions = True  # Allow any version

    @metadata()
    def _version(self):
        """Return version."""
        return '6.0'

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'image'


class PdfJHove(JHove):
    """JHove scraper for PDF."""

    # Supported mimetypes and versions
    _supported = {'application/pdf': ['1.2', '1.3', '1.4', '1.5', '1.6',
                                      'A-1a', 'A-1b']}
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'PDF-hul'  # JHove module

    @metadata()
    def _version(self):
        """Return version."""
        return self.report_field("version")

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'binary'


class Utf8JHove(JHove):
    """
    JHove scraper for UTF-8 text.

    We don't want to run this for all files, but just for UTF-8 text files
    separately. This must be run after actual scraping, since we have to know
    the charset of the file.
    """

    _supported = {}  # We will not run at normal stage
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'UTF8-hul'  # JHove module

    @metadata()
    def _mimetype(self):
        """Return None as we are only iterested in charset."""
        return None

    @metadata()
    def _version(self):
        """Return None as we are only iterested in charset."""
        return None

    @metadata()
    def _charset(self):
        """Return charset from JHOVE."""
        if self.well_formed:
            return 'UTF-8'
        return self.report_field('format')

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'text'

    def _check_supported(self):
        """Do nothing: we dont care about the mimetype or version."""
        pass


class WavJHove(JHove):
    """JHove scraper for WAV and BWF audio data."""

    _supported = {'audio/x-wav': ['2', '']}  # Supported mimetype
    _only_wellformed = True  # Only well-formed check
    _jhove_module = 'WAVE-hul'  # Jhove module
    _allow_versions = True  # Allow any version

    @metadata()
    def _mimetype(self):
        """
        Return mimetype.

        If the MIME type is a WAV type, audio/vnd.wave is returned, otherwise
        the same method from the superclass is called.
        """
        if self.report_field('mimeType') is not None and \
                (self.report_field('mimeType').split(';')[0]
                 == 'audio/vnd.wave'):
            return 'audio/x-wav'

        return super(WavJHove, self)._mimetype()

    @metadata()
    def _version(self):
        """
        Return version.

        Set version as '2' if profile is BWF, otherwise we don't know.
        For now, we don't accept RF64.
        """
        if self.report_field('profile') is None:
            return None
        if 'RF64' in self.report_field('profile'):
            self.errors('RF64 is not a supported format')
        elif 'BWF' in self.report_field('profile'):
            return '2'

        return None

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'audio'
