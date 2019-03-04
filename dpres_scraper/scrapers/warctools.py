"""Warc file scraper
"""

import gzip
import tempfile
import unicodedata
import string

from dpres_scraper.base import BaseScraper, Shell


def sanitaze_string(dirty_string):
    """Strip non-printable control characters from unicode string"""
    sanitazed_string = "".join(
        char for char in dirty_string if unicodedata.category(char)[0] != "C"
        or char in string.printable)
    return sanitazed_string


class WarcWarctools(BaseScraper):

    """Implements WARC file format scraper using Internet Archives warctools
    scraper.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported = {'application/warc': []}
    _only_wellformed = True

    def __init__(self, filename, mimetype, validation=True):
        """
        """
        self._version = None
        super(WarcWarctools, self).__init__(filename, mimetype, validation)

    def scrape_file(self):

        shell = Shell(['warcvalid', self.filename])

        if shell.returncode != 0:
            self.errors("Validation failed: returncode %s" % shell.returncode)
            # Filter some trash printed by warcvalid.
            filtered_errors = \
                "\n".join([line for line in shell.stderr.split('\n')
                           if 'ignored line' not in line])
            self.errors(filtered_errors)

        self.messages(shell.stdout)

        warc_fd = gzip.open(self.filename)
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with open(self.filename, 'r') as warc_fd:
                line = warc_fd.readline()
        except Exception as exception:
            # Compressed but corrupted gzip file
            self.errors(str(exception))
            self._collect_elements()
            return

        self._version = line.split("WARC/", 1)[1].split(" ")[0]
        self._collect_elements()

    def _s_version(self):
        """Return version
        """
        return self._version

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class ArcWarctools(BaseScraper):
    """Scraper for older arc files
    """

    _supported = {'application/x-internet-archive': []}
    _only_wellformed = True

    def scrape_file(self):
        """Scrape ARC file by converting to WARC using Warctools' arc2warc
        converter."""

        with tempfile.NamedTemporaryFile(prefix="scraper-warctools.") \
                as warcfile:
            shell = Shell(command=['arc2warc', self.filename],
                          output_file=warcfile)

            if shell.returncode != 0:
                self.errors("Validation failed: returncode %s" %
                            shell.returncode)
                # replace non-utf8 characters
                utf8string = shell.stderr.decode('utf8', errors='replace')
                # remove non-printable characters
                sanitazed_string = sanitaze_string(utf8string)
                # encode string to utf8 before adding to errors
                self.errors(sanitazed_string.encode('utf-8'))

            self.messages(shell.stdout)

        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
