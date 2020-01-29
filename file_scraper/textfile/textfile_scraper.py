"""Module for checking if the file is uitable as text file or not."""
from __future__ import unicode_literals

import io
import six
from file_scraper.base import BaseScraper
from file_scraper.magiclib import file_command
from file_scraper.textfile.textfile_model import (TextFileMeta,
                                                  TextEncodingMeta)


class TextfileScraper(BaseScraper):
    """
    Text file detection scraper.

    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.
    """

    _supported_metadata = [TextFileMeta]

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
        self._messages.append("Trying text detection...")

        mimetype = self._file_mimetype()
        if mimetype == "text/plain":
            self._messages.append("File is a text file.")
            for md_class in self._supported_metadata:
                self.streams.append(md_class())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
        else:
            self._errors.append("File is not a text file")


class TextEncodingScraper(BaseScraper):
    """
    Text encoding scraper.

    Tries to use decode() and checks some of illegal character values.
    """

    _supported_metadata = [TextEncodingMeta]

    def __init__(self, filename, check_wellformed=True, params=None):
        """Initialize scraper. Add given charset."""
        if params is None:
            params = {}
        self._charset = params.get("charset", "(:unav)")
        super(TextEncodingScraper, self).__init__(
            filename, check_wellformed, params)

    def scrape_file(self):
        """
        Validate the file with decoding it with given character encoding.
        """
        chunksize = 20*1024*1024  # chunk size
        limit = 100  # Limit file read in MB, 0 = unlimited

        if self._charset in [None, "(:unav)"]:
            self._errors.append("Character encoding not defined.")
            self._add_metadata()
            return
        if not self._check_wellformed:
            self._messages.append("No character encoding validation done, "
                                  "setting predefined encoding value.")
            self._add_metadata()
            return

        try:
            with io.open(self.filename, "rb") as infile:
                position = 0
                probably_utf8 = None  # Not suggesting UTF-8 if empty file

                chunk = infile.read(chunksize)
                while len(chunk) > 0:
                    # Using just UTF-32 to UTF-32BE without BOM does not work.
                    # We have to try UTF-32BE instead. If it does not work,
                    # we use given charset.
                    passby = False
                    if self._charset == "UTF-32":
                        try:
                            self._decode_chunk(chunk, "UTF-32BE", position)
                            passby = True
                        except (ValueError, UnicodeError):
                            pass

                    # Decoding must work with given charset
                    if not passby:
                        self._decode_chunk(chunk, self._charset, position)

                    # Decoding to UTF-16 and ISO-8859-15 might work also with
                    # UTF-8 files. Therefore, we want to know that it is not
                    # UTF-8. If all of the chucks result True here, we most
                    # likely have UTF-8. Or in other words, if any of the
                    # chuncks result False, then we don't have UTF-8.
                    if probably_utf8 in [True, None]:
                        # Will remain False, if once got such value
                        probably_utf8 = self._utf8_contradiction(
                            chunk, position)

                    position = position + chunksize
                    if position > limit*1024*1024 and limit > 0:
                        self._messages.append(
                            "First %s MB read, we skip the remainder." % (
                                limit))
                        break
                    chunk = infile.read(chunksize)


                if probably_utf8:
                    self._errors.append(
                        "Character decoding error: The character encoding "
                        "passed with UTF-8, so therefore the given encoding "
                        "%s is most likely wrong." % self._charset.upper())
                else:
                    self._messages.append(
                        "Character encoding validated successfully.")

        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                six.text_type(err))
        except (ValueError, UnicodeDecodeError) as exception:
            self._errors.append("Character decoding error: %s" % exception)
        finally:
            if infile:
                infile.close()

        self._add_metadata()

    def _utf8_contradiction(self, chunk, position):
        """
        Check that UTF-8 does not make a contradiction.

        With file passed with given encodings UTF-16 or ISO-8859-15 there is
        a chance that the file is actually UTF-8. If the file is ASCII file,
        then it can be accepted with ISO-8859-15 and there is no contradiction
        with UTF-8. If ASCII decoding fails then UTF-8 decoding should fail
        too. Otherwise, we do probably have UTF-8 file.

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
            except (ValueError, UnicodeError):
                # If ASCII did not work, then charset can be (almost) anything
                pass

        # If ASCII did not work, but UTF-8 works, then we quite probably have
        # UTF-8.
        try:
            self._decode_chunk(chunk, "UTF-8", position)
        except (ValueError, UnicodeDecodeError):
            # If it was not UTF-8, then we have to believe the given charset
            return False
        return True

    def _decode_chunk(self, chunk, charset, position):
        """
        Decode given chunk.

        :chunk: Byte chunk from a file
        :charset: Decoding charset
        :position: Chunk position in a file
        """
        decoded_chunk = chunk.decode(charset)
        if self._charset.upper() == "UTF-32":
            return

        forbidden = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
                     "\x07", "\x08", "\x0B", "\x0C", "\x0E", "\x0F", "\x10",
                     "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17",
                     "\x18", "\x19", "\x1A", "\x1B", "\x1C", "\x1D", "\x1E",
                     "\x1F", "\xFF"]
        for forb_char in forbidden:
            index = decoded_chunk.find(forb_char)
            if index > -1:
                raise ValueError(
                    "Illegal character '%s' in position %s" % (
                        forb_char, (position+index)))

    def _add_metadata(self):
        """Add metadata to model."""
        for md_class in self._supported_metadata:
            self.streams.append(md_class(self._charset,
                                         self._given_mimetype,
                                         self._given_version))
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
