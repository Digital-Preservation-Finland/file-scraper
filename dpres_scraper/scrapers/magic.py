"""Scraper for various binary and text file formats
"""
from dpres_scraper.magic_base import TextMagic, BinaryMagic


class TextFileMagic(TextMagic):
    """Scraper for text files
    """

    _supported = {'text/plain': [], 'text/csv': []}

    # pylint: disable=no-self-use
    def _s_version(self):
        """Return version
        """
        return ''


class XmlFileMagic(TextMagic):
    """Scraper for xml files
    """

    _supported = {'text/xml': []}
    _starttag = 'XML '
    _endtag = ' '


class HtmlFileMagic(TextMagic):
    """Scraper for (x)html files
    """

    _supported = {'text/html': [],
                  'application/xhtml+xml': []}

    def _s_version(self):
        """Return version
        """
        return None


class PdfFileMagic(BinaryMagic):
    """Scraper for PDF files
    """

    _supported = {'application/pdf': []}


class OfficeFileMagic(BinaryMagic):
    """Scraper for office files
    """

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
    _only_wellformed = True


class PngFileMagic(BinaryMagic):
    """Scraper for PNG files
    """

    _supported = {'image/png': []}

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

    _supported = {'image/jpeg': []}
    _starttag = 'standard '
    _endtag = ','

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'


class Jp2FileMagic(BinaryMagic):
    """Scraper for JP2 files
    """

    _supported = {'image/jp2': []}

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

    _supported = {'image/tiff': []}

    def _s_version(self):
        """Return version
        """
        return '6.0'

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'
