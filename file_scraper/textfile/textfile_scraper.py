"""Module for checking if the file is suitable as text file or not."""
from __future__ import unicode_literals

import io
import six
from file_scraper.base import BaseScraper
from file_scraper.defaults import UNAV
from file_scraper.exceptions import (ForbiddenCharacterError,
                                     UnknownEncodingError)
from file_scraper.magiclib import file_command
from file_scraper.utils import iter_utf_bytes
from file_scraper.textfile.textfile_model import (TextFileMeta,
                                                  TextEncodingMeta)


class TextfileScraper(BaseScraper):
    """
    Text file detection scraper.

    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.

    The tool is not able to detect UTF-16 files without BOM or UTF-32 files.
    """

    _supported_metadata = [TextFileMeta]

    @property
    def well_formed(self):
        """TextfileScraper is not able to check well-formedness.

        :returns: False if TextfileScraper can not open or handle the file,
                  None otherwise.
        """
        valid = super(TextfileScraper, self).well_formed
        if not valid:
            return valid

        return None

    def _file_mimetype(self):
        """
        Detect mimetype with the soft option that excludes libmagick.

        :returns: file mimetype
        """
        params = ["-be", "soft", "--mime-type"]
        shell = file_command(self.filename, params)
        if shell.stderr:
            self._errors.append(shell.stderr)

        return shell.stdout.strip()

    def scrape_file(self):
        """Check MIME type determined by libmagic."""
        charset = self._params.get("charset", None)
        if charset is not None and charset.upper() in ["UTF-32", "UTF-16"]:
            self._messages.append(
                "Scraper not supported with charset %s. Predefined metadata "
                "is collected." % charset)
        else:
            self._messages.append("Trying text detection...")

            mimetype = self._file_mimetype()
            if mimetype == "text/plain":
                self._messages.append("File is a text file.")
            else:
                self._errors.append(
                    "File is not a text file, or it is a UTF-16 file without "
                    "BOM or a UTF-32 file.")
        self.streams = list(self.iterate_models(
            well_formed=self.well_formed))
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True)


class TextEncodingMetaScraper(BaseScraper):
    """
    Scraper to set predefined character encoding to metadata.

    This is run in the iterator only when well-formed checking is not done.
    Otherwise the charset information is not collected with some encondings,
    such as UTF-16 without BOM and UTF-32.
    """
    _supported_metadata = [TextEncodingMeta]

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize scraper. Add given charset.

        :filename: File name
        :mimetype: File MIME type
        :version: File format version
        :params: Extra parameters as dict, the following is required:
                 charset: File character encoding
        """
        super(TextEncodingMetaScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)
        self._charset = self._params.get("charset", UNAV)

    @property
    def well_formed(self):
        """TextEncodingMetaScraper is not able to check well-formedness.

        :returns: False if TextEncodingMetaScraper can not open or handle
                  the file,
                  None otherwise.
        """
        valid = super(TextEncodingMetaScraper, self).well_formed
        if not valid:
            return valid

        return None

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Support only when no checking of well-formedness is done.

        :mimetype: MIME type of a file
        :version: Version of a file. Defaults to None.
        :check_wellformed: True for scraping with well-formedness check, False
                           for skipping the check. Defaults to True.
        :params: None
        :returns: True if the MIME type and version are supported, False if not
        """
        if check_wellformed:
            return False
        return super(TextEncodingMetaScraper, cls).is_supported(
            mimetype, version, check_wellformed, params)

    def scrape_file(self):
        """No actual scraping. Set the predefined character encoding value."""
        self._messages.append("Setting character encoding.")
        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, charset=self._charset,
            predefined_mimetype=self._predefined_mimetype))
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True)


class TextEncodingScraper(BaseScraper):
    """
    Text encoding scraper.

    Tries to use decode() and checks some of illegal character values.

    The rules for decoding validation are following:

    - For UTF-32 we try pre-decoding first 1024 bytes with UTF-32BE first and
      use it if it succeeds, but switch to UTF-32 if it fails.
    - For UTF-16 we try decoding with UTF-16 first. This must success or the
      file is not UTF-16 file. If success, then we also need to try UTF-8. If
      that fails, the file is UTF-16, otherwise UTF-8.
    - For UTF-8 we just try decoding with UTF-8. This must success or the file
      is not valid UTF-8 file.
    - For ISO-8859-15 files we try decoding with ISO-8859-15 first. This must
      success or the file is not valid ISO-8859-15 file. If success, then
      we also need to try ASCII. If ASCII succeeds, it is also ISO-8859-15
      file. If ASCII fails, we also need to try UTF-8. If that fails, the
      file is ISO-8859-15, otherwise UTF-8.
    """
    _supported_metadata = [TextEncodingMeta]
    _only_wellformed = True
    _chunksize = 20*1024**2
    # Limit file read in MB, 0 = unlimited. Must be divisible by _chunksize
    _limit = 5*_chunksize

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize scraper. Add given charset.

        :filename: File name
        :mimetype: File MIME type
        :version: File format version
        :params: Extra parameters as dict, the following is required:
                 charset: File character encoding
        """
        super(TextEncodingScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)
        self._charset = self._params.get("charset", UNAV)

    def scrape_file(self):
        """
        Validate the file with decoding it with given character encoding.
        """
        if self._charset in [None, UNAV]:
            self._errors.append("Character encoding not defined.")
            return
        try:
            with io.open(self.filename, "rb") as infile:
                position = 0
                probably_utf8 = None  # Not suggesting UTF-8 if empty file

                charset = self._predetect_charset(infile)
                for chunk in iter_utf_bytes(infile, self._chunksize,
                                            self._charset):

                    self._decode_chunk(chunk, charset, position)

                    # If all of the chucks result True here, we most
                    # likely have UTF-8. Or in other words, if any of the
                    # chuncks result False, then we don't have UTF-8.
                    if probably_utf8 in [True, None]:
                        # Will remain False, if once got such value
                        probably_utf8 = self._utf8_contradiction(
                            chunk, position)

                    position = position + len(chunk)
                    if position >= self._limit and self._limit > 0:
                        self._messages.append(
                            "First %s bytes read, we skip the remainder." % (
                                self._limit))
                        break

                if probably_utf8:
                    self._errors.append(
                        "Character decoding error: The character encoding "
                        "passed with UTF-8 and it contains characters "
                        "colliding with the given encoding %s. Most likely "
                        "the file is UTF-8 file." % self._charset.upper())
                else:
                    self._messages.append(
                        "Character encoding validated successfully.")

        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                six.text_type(err))
        except (ForbiddenCharacterError, UnknownEncodingError) as exception:
            self._errors.append("Character decoding error: %s" % exception)

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, charset=self._charset,
            predefined_mimetype=self._predefined_mimetype))
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def _predetect_charset(self, infile):
        """
        Predetect charset.

        In some cases, more accurate encoding information may be needed
        to do the decoding. Currently, this applies to UTF-32, which
        does not work, if the file is UTF-32BE and does not have BOM.
        """
        chunk = infile.read(1024)
        infile.seek(0)
        if self._charset == "UTF-32":
            try:
                self._decode_chunk(chunk, "UTF-32BE", 0)
                return "UTF-32BE"
            except (ForbiddenCharacterError, UnknownEncodingError):
                pass
        return self._charset

    def _utf8_contradiction(self, chunk, position):
        """
        Check that UTF-8 does not make a contradiction.

        With file passed with given decodings UTF-16 or ISO-8859-15 there is
        a chance that the file is actually UTF-8.

        E.g. "abcd".encode("UTF-8").decode("UTF-16") == u"\u6261\u6463"

        If the file is ASCII file, then it can be accepted with ISO-8859-15
        and there is no contradiction with UTF-8. If ASCII decoding fails
        then UTF-8 decoding should fail too. Otherwise, we do probably have
        UTF-8 file.

        :chunk: Byte chunk from a file
        :position: Chunk position in file
        :returns: True if there is UTF-8 contradiction, otherwise False
        """
        if self._charset.upper() in ["UTF-8", "UTF-32"]:
            return False

        if self._charset.upper() == "ISO-8859-15":
            try:
                # If ASCII works, then also ISO-8859-15 is OK
                self._decode_chunk(chunk, "ASCII", position)
                return False
            except (ForbiddenCharacterError, UnknownEncodingError):
                # If ASCII did not work, then charset can be (almost) anything
                pass

        # If ASCII did not work, but UTF-8 works, then we quite probably have
        # UTF-8.
        try:
            self._decode_chunk(chunk, "UTF-8", position)
        except (ForbiddenCharacterError, UnknownEncodingError):
            # If it was not UTF-8, then we have to believe the given charset
            return False
        return True

    # pylint: disable=no-self-use
    def _decode_chunk(self, chunk, charset, position):
        """
        Decode given chunk and check forbidden characters.

        The forbidden characters are the ASCII control characters, in
        exception of horizontal tab, carriage return, and line feed,
        which are allowed.

        :chunk: Byte chunk from a file
        :charset: Decoding charset
        :position: Chunk position in a file
        :raises UnknownEncodingError: When the decoding was unsuccessful
        :raises ForbiddenCharacterError: When a forbidden character was
            found.
        """
        try:
            decoded_chunk = chunk.decode(charset)
        except (UnicodeError, UnicodeDecodeError, LookupError) as err:
            six.raise_from(UnknownEncodingError(err), err)

        forbidden = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
                     "\x07", "\x08", "\x0B", "\x0C", "\x0E", "\x0F", "\x10",
                     "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17",
                     "\x18", "\x19", "\x1A", "\x1B", "\x1C", "\x1D", "\x1E",
                     "\x1F", "\x7F"]

        if charset.upper() == 'ISO-8859-15':
            # Add ISO-8859-15 control characters to the list of forbidden
            # characters
            forbidden += ["\x80", "\x81", "\x82", "\x83", "\x84", "\x85",
                          "\x86", "\x87", "\x88", "\x89", "\x8A", "\x8B",
                          "\x8C", "\x8D", "\x8E", "\x8F", "\x90", "\x91",
                          "\x92", "\x93", "\x94", "\x95", "\x96", "\x97",
                          "\x98", "\x99", "\x9A", "\x9B", "\x9C", "\x9D",
                          "\x9E", "\x9F"]

        for forb_char in forbidden:
            index = decoded_chunk.find(forb_char)
            if index > -1:
                raise ForbiddenCharacterError(
                    "Illegal character '%s' in position %s" % (
                        repr(forb_char)[1:-1], (position+index)))
