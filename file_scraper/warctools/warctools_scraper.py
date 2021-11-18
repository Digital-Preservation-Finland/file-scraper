"""Warc file scraper."""
from __future__ import unicode_literals

import gzip
import os.path
from io import open as io_open

import six

from file_scraper.base import BaseScraper
from file_scraper.defaults import UNAV
from file_scraper.shell import Shell
from file_scraper.warctools.warctools_model import (GzipWarctoolsMeta,
                                                    WarctoolsMeta)


class WarctoolsScraper(BaseScraper):
    """
    Implements WARC file format scraper for metadata collecting.

    This scraper uses Internet Archives warctools scraper.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_metadata = [WarctoolsMeta]

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
        return super(WarctoolsScraper, cls).is_supported(
            mimetype, version, check_wellformed, params)

    def scrape_file(self):
        """Scrape WARC file."""
        try:
            # First assume archive is compressed
            with gzip.open(self.filename) as warc_fd:
                line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            with io_open(self.filename, "rb") as warc_fd:
                line = warc_fd.readline()
        except Exception as exception:  # pylint: disable=broad-except
            # Compressed but corrupted gzip file
            self._errors.append(six.text_type(exception))
            return

        self._messages.append("File was analyzed successfully.")
        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, line=line))
        self._check_supported()


class WarctoolsFullScraper(WarctoolsScraper):
    """
    Implements WARC file format scraper for validation.

    This scraper uses Internet Archives warctools scraper.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_metadata = [WarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Use the default is_supported method from BaseScraper.
        Super class has a special is_supported() method.

        :mimetype: MIME type of a file
        :version: Version of a file. Defaults to None.
        :check_wellformed: True for scraping with well-formedness check, False
                           for skipping the check. Defaults to True.
        :params: None
        :returns: True if the MIME type and version are supported, False if not
        """
        if cls._only_wellformed and not check_wellformed:
            return False
        return any(x.is_supported(mimetype, version) for x in
                   cls._supported_metadata)

    def scrape_file(self):
        """Scrape WARC file."""
        size = os.path.getsize(self.filename)
        if size == 0:
            self._errors.append("Empty file.")
            return
        shell = Shell(["warcvalid", self.filename])

        if shell.returncode != 0:
            self._errors.append("Failed: returncode %s" % shell.returncode)
            # Filter some trash printed by warcvalid.
            filtered_errors = [line for line in shell.stderr.split("\n")
                               if u"ignored line" not in line]
            self._errors.append("\n".join(filtered_errors))
            return

        self._messages.append(shell.stdout)

        super(WarctoolsFullScraper, self).scrape_file()


class GzipWarctoolsScraper(WarctoolsFullScraper):
    """Scraper for compressed Warcs."""

    _supported_metadata = [GzipWarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    def info(self):
        """
        Return scraper info.

        If WarctoolsScraper could scrape the gzip file,
        that class is reported as the scraper class. For failures,
        the class is GzipWarctoolsScraper.
        """
        info = super(GzipWarctoolsScraper, self).info()
        if self.streams:
            info["class"] = "WarctoolsFullScraper"
        return info

    def _check_supported(self, allow_unav_mime=False, allow_unav_version=False,
                         allow_unap_version=False):
        """
        Check that the scraped MIME type and version are supported.

        This scraper uses the Warc scraper to check the file and get the
        metadata, so in addition to the normal metadata model check, it is also
        sufficient if the Warc scraper supports the MIME type and
        version combination.
        """
        if not self.streams:
            self._errors.append("MIME type not supported by this scraper.")

        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()
        if version == UNAV:
            version = None

        # Check own metadata models for support: if supporting model is found,
        # no further checking is needed.
        for md_class in self._supported_metadata:
            if mimetype in md_class.supported_mimetypes():
                return

        # also check the used scraper class: final result of warc,
        # corresponding to the compressed file, is also ok
        if WarctoolsFullScraper.is_supported(mimetype, version):
            return

        self._errors.append("MIME type {} with version {} is not "
                            "supported.".format(mimetype, version))
