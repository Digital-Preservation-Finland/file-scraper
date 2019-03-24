"""Scraper for various binary and text file formats
"""
from file_scraper.magic_base import TextMagic, BinaryMagic


class TextFileMagic(TextMagic):
    """Scraper for text files
    """
    # Supported mimetypes
    _supported = {'text/plain': [''], 'text/csv': ['']}
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        if self.mimetype != self._s_mimetype():
            return None
        return ''


class XmlFileMagic(TextMagic):
    """Scraper for xml files
    """

    _supported = {'text/xml': ['1.0']}  # Supported mimetypes
    _starttag = 'XML '             # Text before version in magic output
    _endtag = ' '                  # Text after version in magic output
    _allow_versions = True         # Allow any version

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """This is not a Schematron scraper, skip this in such case.
        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                            identification and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if 'schematron' in params:
            return False
        return super(XmlFileMagic, cls).is_supported(mimetype, version,
                                                     check_wellformed, params)


class XhtmlFileMagic(TextMagic):
    """Scraper for (x)html files
    """
    # Supported mimetypes
    _supported = {'application/xhtml+xml': ['1.0', '1.1']}
    _starttag = 'XML '      # Text before version in magic output
    _endtag = ' '           # Text after version in magic output
    _allow_versions = True  # Allow any version

    def _s_mimetype(self):
        """Modify result
        """
        mime = super(XhtmlFileMagic, self)._s_mimetype()
        if mime == 'text/xml':
            return 'application/xhtml+xml'
        return mime


class HtmlFileMagic(TextMagic):
    """Scraper for (x)html files
    """
    # Supported mimetypes
    _supported = {'text/html': ['4.01', '5.0']}
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        return None


class PdfFileMagic(BinaryMagic):
    """Scraper for PDF files
    """
    # Supported mimetype
    _supported = {'application/pdf': ['1.2', '1.3', '1.4', '1.5', '1.6',
                                      '1.7', 'A-1a', 'A-1b', 'A-2a', 'A-2b',
                                      'A-2u', 'A-3a', 'A-3b', 'A-3u']}
    _allow_versions = True  # Allow any version


class OfficeFileMagic(BinaryMagic):
    """Scraper for office files
    """
    # Supported mimetypes and versions
    _supported = {
        'application/vnd.oasis.opendocument.text': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.spreadsheet': [
            '1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.presentation': [
            '1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.graphics': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.formula': ['1.0', '1.2'],
        'application/msword': ['8.0', '8.5', '9.0', '10.0', '11.0'],
        'application/vnd.ms-excel': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.ms-powerpoint': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        'document': ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.'
        'spreadsheetml.sheet': ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.presentationml.'
        'presentation': ['12.0', '14.0', '15.0']}
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        return None


class ArcFileMagic(BinaryMagic):
    """Scraper for Arc files
    """
    # Supported mimetype
    _supported = {'application/x-internet-archive': ['1.0', '1.1']}
    _allow_versions = True  # Allow any version

    def _s_mimetype(self):
        """Return mimetype
        """
        if self._magic_mimetype == 'application/x-ia-arc':
            return 'application/x-internet-archive'
        return self._magic_mimetype

    def _s_version(self):
        """Return version
        """
        if self.mimetype != self._s_mimetype():
            return None
        if self._magic_version == '1':
            return '1.0'
        return self._magic_version


class PngFileMagic(BinaryMagic):
    """Scraper for PNG files
    """
    _supported = {'image/png': ['1.2']}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        if self.mimetype != self._s_mimetype():
            return None
        return '1.2'

    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class JpegFileMagic(BinaryMagic):
    """Scraper for JPEG files
    """

    _supported = {'image/jpeg': ['1.00', '1.01', '1.02', '2.0', '2.1',
                                 '2.2', '2.2.1']}  # Supported mimetype
    _starttag = 'standard '  # Text before version in magic output
    _endtag = ','            # Text after version in magic output
    _allow_versions = True   # Allow any version

    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class Jp2FileMagic(BinaryMagic):
    """Scraper for JP2 files
    """

    _supported = {'image/jp2': ['']}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        if self.mimetype != self._s_mimetype():
            return None
        return ''

    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class TiffFileMagic(BinaryMagic):
    """Scraper for TIFF files
    """

    _supported = {'image/tiff': ['6.0']}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Return version
        """
        if self.mimetype != self._s_mimetype():
            return None
        return '6.0'

    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'
