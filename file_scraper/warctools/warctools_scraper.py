"""Warc file scraper."""
from __future__ import unicode_literals

import gzip
import os.path
import tempfile
from io import open as io_open

import six

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.utils import sanitize_bytestring, encode_path
from file_scraper.warctools.warctools_model import (ArcWarctoolsMeta,
                                                    GzipWarctoolsMeta,
                                                    WarcWarctoolsMeta)


class WarcWarctoolsScraper(BaseScraper):
    """
    Implements WARC file format scraper.

    This scraper uses Internet Archives warctools scraper.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_metadata = [WarcWarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape WARC file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
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
        self.iterate_models(errors=self._errors, line=line)
        self._check_supported()


class ArcWarctoolsScraper(BaseScraper):
    """Scraper for older arc files."""

    _supported_metadata = [ArcWarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """
        Scrape ARC file by converting to WARC.

        This is done using Warctools" arc2warc converter.
        """
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        size = os.path.getsize(self.filename)
        if size == 0:
            self._errors.append("Empty file.")
            return
        with tempfile.NamedTemporaryFile(prefix="scraper-warctools.") \
                as warcfile:
            shell = Shell(
                command=["arc2warc", encode_path(self.filename)],
                stdout=warcfile)
            if shell.returncode != 0:
                self._errors.append("Failed: returncode %s" % shell.returncode)
                self._errors.append(sanitize_bytestring(shell.stderr_raw))
                return
            self._messages.append("File was analyzed successfully.")
            if shell.stdout:
                self._messages.append(shell.stdout)
        self.iterate_models(errors=self._errors)
        self._check_supported(allow_unav_version=True)


class GzipWarctoolsScraper(BaseScraper):
    """Scraper for compressed Warcs and Arcs."""

    _supported_metadata = [GzipWarctoolsMeta]
    _only_wellformed = True  # Only well-formed check
    _scraper = None

    _supported_scrapers = [WarcWarctoolsScraper, ArcWarctoolsScraper]

    def scrape_file(self):
        """Scrape file. If Warc fails, try Arc."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        original_messages = self._messages
        for class_ in self._supported_scrapers:
            if class_ == WarcWarctoolsScraper:
                mime = "application/warc"
            else:
                mime = "application/x-internet-archive"
            self._scraper = class_(filename=self.filename, mimetype=mime)
            self._scraper.scrape_file()

            # pylint: disable=protected-access
            if self._messages and not self._scraper.well_formed:
                self._messages = self._messages + self._scraper._messages
            else:
                self._messages = original_messages + self._scraper._messages
            if self._errors and not self._scraper.well_formed:
                self._errors = self._errors + self._scraper._errors
            else:
                self._errors = self._scraper._errors

            if self._scraper.well_formed:
                self.iterate_models(metadata_model=self._scraper.streams)
                self._check_supported()
                break

    def info(self):
        """
        Return scraper info.

        If either WarcWarctoolsScraper or ArcWarctoolsScraper could scrape the
        gzip file, that class is reported as the scraper class. For failures,
        the class is GzipWarctoolsScraper.
        """
        info = super(GzipWarctoolsScraper, self).info()
        if self.streams:
            info["class"] = self._scraper.__class__.__name__
        return info

    def _check_supported(self, allow_unav_mime=False, allow_unav_version=False,
                         allow_unap_version=False):
        """
        Check that the scraped MIME type and version are supported.

        This scraper uses the two other scrapers to check the file and get the
        metadata, so in addition to the normal metadata model check, it is also
        sufficient if that at least one of the tried scrapers supports the MIME
        type and version combination.
        """
        if not self.streams:
            self._errors.append("MIME type not supported by this scraper.")

        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()
        if version == "(:unav)":
            version = None

        # Check own metadata models for support: if supporting model is found,
        # no further checking is needed.
        for md_class in self._supported_metadata:
            if mimetype in md_class.supported_mimetypes():
                return

        # also check the used scraper classes: final result of arc or warc,
        # corresponding to the compressed file, is also ok
        for scraper_class in self._supported_scrapers:
            if scraper_class.is_supported(mimetype, version):
                return

        self._errors.append("MIME type {} with version {} is not "
                            "supported.".format(mimetype, version))
