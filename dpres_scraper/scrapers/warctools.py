"""Warc file scraper
"""

import gzip
import tempfile
from dpres_scraper.utils import sanitize_string
from dpres_scraper.base import BaseScraper, Shell


class GzipWarctools(BaseScraper):
    """ Scraper for compressed Warcs and Arcs.
    """

    _supported = {'application/gzip': []}  # Supported mimetype
    _only_wellformed = True                # Only well-formed check
    _allow_versions = True                 # Allow any version

    def scrape_file(self):
        """Scrape file. If Warc fails, try Arc.
        """
        for class_ in [WarcWarctools, ArcWarctools]:
            scraper = class_(self.filename, None)
            scraper.scrape_file()
            if scraper.well_formed:
                self.mimetype = scraper.mimetype
                self.version = scraper.version
                self.streams = scraper.streams
                self.info = scraper.info
                self.messages(scraper.messages())
                self.errors(scraper.errors())
                return

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class WarcWarctools(BaseScraper):
    """Implements WARC file format scraper using Internet Archives warctools
    scraper.
    .. seealso:: https://github.com/internetarchive/warctools
    """

    # Supported mimetype and versions
    _supported = {'application/warc': ['0.17', '0.18', '1.0']}
    _only_wellformed = True                # Only well-formed check
    _allow_versions = True                 # Allow any version

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

        self.mimetype = 'application/warc'
        self.version = line.split("WARC/", 1)[1].split(" ")[0].strip()
        self._check_supported()
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class ArcWarctools(BaseScraper):
    """Scraper for older arc files
    """
    # Supported mimetype and varsions
    _supported = {'application/x-internet-archive': ['1.0', '1.1']}
    _only_wellformed = True  # Only well-formed check
    _allow_versions = True   # Allow any version

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
                sanitized_string = sanitize_string(utf8string)
                # encode string to utf8 before adding to errors
                self.errors(sanitized_string.encode('utf-8'))

            self.messages(shell.stdout)

        self.mimetype = 'application/x-internet-archive'
        self._check_supported()
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
