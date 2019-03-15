"""Scraper for various binary and text file formats
"""
import os.path
import ctypes

try:
    ctypes.cdll.LoadLibrary('/opt/file-5.30/lib64/libmagic.so.1')
except OSError:
    print('/opt/file-5.30/lib64/libmagic.so.1 not found, MS Office detection '
          'may not work properly if file command library is older than 5.30.')
try:
    import magic
except ImportError:
    pass

from dpres_scraper.base import BaseScraper
from dpres_scraper.dicts import MIMETYPE_DICT


class BinaryMagic(BaseScraper):
    """Scraper for binary files"""

    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None          # Text after file format version in magic result.

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize scraper.
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._magic_mimetype = None  # Mimetype from magic
        self._magic_version = None   # Version from magic
        super(BinaryMagic, self).__init__(filename, mimetype,
                                          validation, params)

    def scrape_file(self):
        """Scrape binary file
        """
        if not os.path.exists(self.filename):
            self.errors('File not found.')
            self._collect_elements()
            return
        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            self._magic_mimetype = magic_.file(self.filename)
            magic_.close()

            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            self._magic_version = magic_.file(
                self.filename).split(self._starttag)[-1]
            magic_.close()
            if self._endtag:
                self._magic_version = self._magic_version.split(
                    self._endtag)[0]
            if self._s_mimetype() == self.mimetype or \
                    (self._s_mimetype() in MIMETYPE_DICT and \
                     MIMETYPE_DICT[self._s_mimetype()] == self.mimetype):
                self.messages('The file was scraped successfully.')
            else:
                self.errors('Given mimetype %s and detected mimetype %s do '
                            'not match.' % (self.mimetype, self._s_mimetype()))
        except Exception as e:
            self.errors('Error in scraping file.')
            self.errors(str(e))
        finally:
            self._check_supported()
            self._collect_elements()

    @property
    def well_formed(self):
        """Return well formed info
        """
        if not self._validation:
            return None
        if self._s_mimetype() == self.mimetype:
            return super(BinaryMagic, self).well_formed
        return False

    def _s_mimetype(self):
        """Return mimetype
        """
        return self._magic_mimetype

    def _s_version(self):
        """Return version
        """
        if self._magic_version == 'data':
            return None
        return self._magic_version

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class TextMagic(BaseScraper):
    """Scraper for text files
    """

    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None          # Text after file format version in magic result.

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize text magic scraper
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._magic_mimetype = None  # Mimetype from magic
        self._magic_version = None   # Version from magic
        self._magic_charset = None   # Charset from magic
        super(TextMagic, self).__init__(filename, mimetype, validation, params)

    def scrape_file(self):
        """Scrape text file
        """
        if not os.path.exists(self.filename):
            self.errors('File not found.')
            self._collect_elements()
            return
        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            self._magic_mimetype = magic_.file(self.filename)
            magic_.close()

            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            self._magic_version = magic_.file(
                self.filename).split(self._starttag)[-1]
            magic_.close()
            if self._endtag:
                self._magic_version = self._magic_version.split(
                    self._endtag)[0]

            magic_ = magic.open(magic.MAGIC_MIME_ENCODING)
            magic_.load()
            self._magic_charset = magic_.file(self.filename)
            magic_.close()
            if self._s_mimetype() == self.mimetype or \
                    (self._s_mimetype() in MIMETYPE_DICT and \
                     MIMETYPE_DICT[self._s_mimetype()] == self.mimetype):
                self.messages('The file was scraped successfully.')
            else:
                self.errors('Given mimetype %s and detected mimetype %s do '
                            'not match.' % (self.mimetype, self._s_mimetype()))
        except Exception as e:
            self.errors('Error in scraping file.')
            self.errors(str(e))
        finally:
            # self._check_supported()
            self._collect_elements()

    @property
    def well_formed(self):
        """Return well formed info
        """
        if not self._validation:
            return None
        if self._s_mimetype() == self.mimetype:
            return super(TextMagic, self).well_formed
        return False

    def _s_mimetype(self):
        """Return charset
        """
        return self._magic_mimetype

    def _s_version(self):
        """Return version
        """
        if self._magic_version == 'data':
            return None
        return self._magic_version

    def _s_charset(self):
        """Return charset
        """
        if self._magic_charset.upper() == 'BINARY':
            return None
        if self._magic_charset.upper() == 'US-ASCII':
            return 'UTF-8'
        elif self._magic_charset.upper() == 'ISO-8859-1':
            return 'ISO-8859-15'
        elif self._magic_charset.upper() == 'UTF-16LE' \
                or self._magic_charset.upper() == 'UTF-16BE':
            return 'UTF-16'
        else:
            return self._magic_charset.upper()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'text'
