"""Module for scraping files with Jhove scraper"""
import mimeparse
from dpres_scraper.jhove_base import JHove
from dpres_scraper.utils import strip_zeros


NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove',
              'aes': 'http://www.aes.org/audioObject'}


class GifJHove(JHove):
    """JHove GIF file format scraper"""

    _supported = {'image/gif': []} 
    _only_wellformed = True
    _jhove_module = 'GIF-hul'

    def _s_version(self):
        """Jhove returns the version as '87a' or '89a' but '1987a'
        or '1989a' is used. Hence '19' is prepended to the version returned by
        Jhove"""
        return '19' + self.report_field("version")

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'image'


class HtmlJHove(JHove):
    """Jhove HTML file format scraper"""

    _supported = {'text/html': ['4.01'], 'application/xhtml+xml': []}
    _only_wellformed = True
    _jhove_module = 'HTML-hul'

    def _s_version(self):
        """Jhove returns the version as 'HTML 4.01' but in '4.01' is
        used. Hence we drop 'HTML ' prefix from the string returned by Jhove"""
        version = self.report_field("version")
        if len(version) > 0:
            version = version.split()[-1]
        return version

    def _get_charset_html(self):
        """Get the charset from the JHove report for HTML files"""
        query = '//j:property[j:name="Content"]//j:value/text()'
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            result_mimetype = mimeparse.parse_mime_type(results[0])
        except mimeparse.MimeTypeParseException:
            return None
        else:
            params = result_mimetype[2]
            return params.get('charset')

    def _get_charset_xml(self):
        """Get the charset from the JHove report for XHTML files"""
        query = '//j:property[j:name="Encoding"]//j:value/text()'
        results = self._report.xpath(query, namespaces=NAMESPACES)
        try:
            return results[0]
        except IndexError:
            # This will be handled by scrape_file()
            pass

    def _s_charset(self):
        """Get the charset from HTML/XML files"""
        if "xml" in self.mimetype:
            self._get_charset_xml()
        else:
            self._get_charset_html()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'char'


class JpegJHove(JHove):
    """JHove scraper for JPEG"""

    _supporteds = {'image/jpeg': []}
    _only_wellformed = True
    _jhove_module = 'JPEG-hul'

    def _s_version(self):
        """Return version
        """
        return None

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'image'


class TiffJHove(JHove):
    """JHove scraper for TIFF"""

    _supported = {'image/tiff': []}
    _only_wellformed = True
    _jhove_module = 'TIFF-hul'

    def _s_version(self):
        """Return version
        """
        return '6.0'

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'image'


class PdfJHove(JHove):
    """JHove scraper for PDF"""

    _supported = {'application/pdf': ['1.2', '1.3', '1.4', '1.5', '1.6']}
    _only_wellformed = True
    _jhove_module = 'PDF-hul'

    def _s_version(self):
        """Return version"""
        return self.report_field("version")

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class Utf8JHove(JHove):
    """JHove scraper for text UTF-8."""

    _supported = {'text/csv': [], 'text/plain': [], 'text/xml': [],
                  'text/html': [], 'application/xhtml+xml': []}
    _only_wellformed = True
    _jhove_module = 'UTF8-hul'

    def _s_mimetype(self):
        """We are only iterested in charset"""
        return None

    def _s_version(self):
        """We are only iterested in charset"""
        return None

    def _s_charset(self):
        """Return charset from JHOVE"""
        return self.report_field('format')

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'char'


class WavJHove(JHove):
    """JHove scraper for WAV and BWF audio data."""

    _supported = {'audio/x-wav': []}
    _only_wellformed = True
    _jhove_module = 'WAVE-hul'

    def _s_mimetype(self):
        """Check if mimetype is of a WAV type, otherwise call the same
        method from the superclass."""

        if self.report_field('mimeType').split(';')[0] == 'audio/vnd.wave':
            return 'audio/x-wav'
        else:
            super(WavJHove, self)._s_mimetype()

    def _s_version(self):
        """Set version as '2' if profile is BWF, otherwise we don't know.
        For now, we don't accept RF64."""

        if 'RF64' in self.report_field('profile'):
            self.errors('RF64 is not a supported format')
        elif 'BWF' in self.report_field('profile'):
            return '2'
        else:
            return None

    def aes_report_field(self, field):
        """Query elements with the aes namespace from the scraper's
        report."""

        query = '//aes:%s/text()' % field
        results = self._report.xpath(query, namespaces=NAMESPACES)
        return '\n'.join(results)

    def _s_num_channels(self):
        """Returns audio data from the report
        """
        return self.aes_report_field("numChannels")

    def _s_bits_per_sample(self):
        """Returns audio data from the report
        """
        return self.aes_report_field("bitDepth")

    def _s_sampling_frequency(self):
        """Returns audio data from the report
        """
        return strip_zeros(str(float(
            self.aes_report_field('sampleRate'))/1000))

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'audio'
