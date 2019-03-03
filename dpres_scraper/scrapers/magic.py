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
    _version_tag = 'XML '

    def _s_version(self):
        """Return version
        """
        return self._magic_version


class HtmlFileMagic(TextMagic):
    """Scraper for (x)html files
    """

    _supported = {'text/html': [],
                  'application/xhtml+xml': []}


class BinaryFileMagic(BinaryMagic):
    """Scraper for binary files
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


class ImageFileMagic(BinaryMagic):
    """Scraper for image files
    """

    _supported = {
        'image/png': [], 'image/jpeg': [], 'image/jp2': [], 'image/tiff': []}
    _only_wellformed = True

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'
