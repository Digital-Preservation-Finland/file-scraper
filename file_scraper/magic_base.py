"""Scraper for various binary and text file formats."""
# pylint: disable=ungrouped-imports
import os.path
import ctypes

try:
    from file_scraper.defaults import MAGIC_LIBRARY

    ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
except OSError:
    print('%s not found, MS Office detection may not work properly if '
          'file command library is older.' % MAGIC_LIBRARY)

try:
    import magic
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.defaults import MIMETYPE_DICT
from file_scraper.utils import encode, metadata


class BinaryMagic(BaseScraper):
    """Scraper for binary files."""

    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None  # Text after file format version in magic result.

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                            identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._magic_mimetype = None  # Mimetype from magic
        self._magic_version = None  # Version from magic
        super(BinaryMagic, self).__init__(filename, mimetype,
                                          check_wellformed, params)

    def scrape_file(self):
        """Scrape binary file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        if not os.path.exists(self.filename):
            self.errors('File not found.')
            self._collect_elements()
            return
        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            self._magic_mimetype = magic_.file(encode(self.filename))
            magic_.close()

            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            self._magic_version = magic_.file(
                encode(self.filename)).split(self._starttag)[-1]
            magic_.close()
            if self._endtag:
                self._magic_version = self._magic_version.split(
                    self._endtag)[0]
            if self._mimetype() == self.mimetype or \
                    (self._mimetype() in MIMETYPE_DICT and
                     MIMETYPE_DICT[self._mimetype()] == self.mimetype):
                self.messages('The file was analyzed successfully.')
            else:
                self.errors('Given mimetype %s and detected mimetype %s do '
                            'not match.' % (self.mimetype, self._mimetype()))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self.errors('Error in analyzing file.')
            self.errors(str(e))
        finally:
            self._check_supported()
            self._collect_elements()

    @property
    def well_formed(self):
        """Return well-formedness info."""
        if not self._check_wellformed:
            return None
        if self._mimetype() == self.mimetype:
            return super(BinaryMagic, self).well_formed
        return False

    @metadata()
    def _mimetype(self):
        """Return mimetype."""
        return self._magic_mimetype

    @metadata()
    def _version(self):
        """Return version."""
        if self._magic_version == 'data':
            return None
        return self._magic_version

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'binary'


class TextMagic(BaseScraper):
    """Scraper for text files."""

    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None  # Text after file format version in magic result.

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize text magic scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._magic_mimetype = None  # Mimetype from magic
        self._magic_version = None  # Version from magic
        self._magic_charset = None  # Charset from magic
        super(TextMagic, self).__init__(filename, mimetype, check_wellformed,
                                        params)

    def scrape_file(self):
        """Scrape text file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        if not os.path.exists(self.filename):
            self.errors('File not found.')
            self._collect_elements()
            return
        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            self._magic_mimetype = magic_.file(encode(self.filename))
            magic_.close()

            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            self._magic_version = magic_.file(
                encode(self.filename)).split(self._starttag)[-1]
            magic_.close()
            if self._endtag:
                self._magic_version = self._magic_version.split(
                    self._endtag)[0]

            magic_ = magic.open(magic.MAGIC_MIME_ENCODING)
            magic_.load()
            self._magic_charset = magic_.file(encode(self.filename))
            magic_.close()
            if self._mimetype() == self.mimetype or \
                    (self._mimetype() in MIMETYPE_DICT and
                     MIMETYPE_DICT[self._mimetype()] == self.mimetype):
                self.messages('The file was analyzed successfully.')
            else:
                self.errors('Given mimetype %s and detected mimetype %s do '
                            'not match.' % (self.mimetype, self._mimetype()))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self.errors('Error in analyzing file.')
            self.errors(str(e))
        finally:
            self._check_supported()
            self._collect_elements()

    @property
    def well_formed(self):
        """Return well formed info."""
        if not self._check_wellformed:
            return None
        if self._mimetype() == self.mimetype:
            return super(TextMagic, self).well_formed
        return False

    @metadata()
    def _mimetype(self):
        """Return charset."""
        return self._magic_mimetype

    @metadata()
    def _version(self):
        """Return version."""
        if self._magic_version == 'data':
            return None
        return self._magic_version

    @metadata()
    def _charset(self):
        """Return charset."""
        if self._magic_charset is None:
            return None
        if self._magic_charset.upper() == 'BINARY':
            return None
        if self._magic_charset.upper() == 'US-ASCII':
            return 'UTF-8'
        if self._magic_charset.upper() == 'ISO-8859-1':
            return 'ISO-8859-15'
        if self._magic_charset.upper() == 'UTF-16LE' \
                or self._magic_charset.upper() == 'UTF-16BE':
            return 'UTF-16'

        return self._magic_charset.upper()

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'text'
