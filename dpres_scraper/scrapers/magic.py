"""Scraper for various binary and text file formats
"""
from dpres_scraper.magic_base import TextMagic, BinaryMagic


class TextFileMagic(TextMagic):
    """Scraper for text files
    """
    # Supported mimetypes
    _supported = {'text/plain': [], 'text/csv': []}

    # pylint: disable=no-self-use
    def _s_version(self):
        """Return version
        """
        return ''


class XmlFileMagic(TextMagic):
    """Scraper for xml files
    """

    _supported = {'text/xml': []}  # Supported mimetypes
    _starttag = 'XML '             # Text before version in magic output
    _endtag = ' '                  # Text after version in magic output

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     validation=True, params=None):
        """This is not a Schematron validator, skip this in such case.
        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if 'schematron' in params:
            return False
        return super(XmlFileMagic, cls).is_supported(mimetype, version,
                                                     validation, params)


class HtmlFileMagic(TextMagic):
    """Scraper for (x)html files
    """
    # Supported mimetypes
    _supported = {'text/html': [],
                  'application/xhtml+xml': []}

    def _s_version(self):
        """Return version
        """
        return None


class PdfFileMagic(BinaryMagic):
    """Scraper for PDF files
    """
    # Supported mimetype
    _supported = {'application/pdf': []}


class OfficeFileMagic(BinaryMagic):
    """Scraper for office files
    """
    # Supported mimetype
    _supported = {
        'application/vnd.oasis.opendocument.text': [],
        'application/vnd.oasis.opendocument.spreadsheet': [],
        'application/vnd.oasis.opendocument.presentation': [],
        'application/vnd.oasis.opendocument.graphics': [],
        'application/vnd.oasis.opendocument.formula': [],
        'application/msword': [],
        'application/vnd.ms-excel': [],
        'application/vnd.ms-powerpoint': [],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        'document': [],
        'application/vnd.openxmlformats-officedocument.'
        'spreadsheetml.sheet': [],
        'application/vnd.openxmlformats-officedocument.presentationml.'
        'presentation': []}


class PngFileMagic(BinaryMagic):
    """Scraper for PNG files
    """
    _supported = {'image/png': []}  # Supported mimetypes

    def _s_version(self):
        """Return version
        """
        return '1.2'

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class JpegFileMagic(BinaryMagic):
    """Scraper for JPEG files
    """

    _supported = {'image/jpeg': []}  # Supported mimetype
    _starttag = 'standard '          # Text before version in magic output
    _endtag = ','                    # Text after version in magic output

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class Jp2FileMagic(BinaryMagic):
    """Scraper for JP2 files
    """

    _supported = {'image/jp2': []}  # Supported mimetype

    def _s_version(self):
        """Return version
        """
        return ''

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class TiffFileMagic(BinaryMagic):
    """Scraper for TIFF files
    """

    _supported = {'image/tiff': []}  # Supported mimetype

    def _s_version(self):
        """Return version
        """
        return '6.0'

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'
