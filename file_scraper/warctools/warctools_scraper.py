"""Warc file scraper."""
from __future__ import unicode_literals

import gzip
import os.path
import tempfile
from io import open as io_open

import six

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.utils import ensure_text, sanitize_string, encode_path
from file_scraper.warctools.warctools_model import (ArcWarctoolsMeta,
                                                    GzipWarctoolsMeta,
                                                    WarcWarctoolsMeta)


class GzipWarctoolsScraper(BaseScraper):
    """Scraper for compressed Warcs and Arcs."""

    _supported_metadata = [GzipWarctoolsMeta]
    _only_wellformed = True  # Only well-formed check
    _scraper = None

    def scrape_file(self):
        """Scrape file. If Warc fails, try Arc."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        for class_ in [WarcWarctoolsScraper, ArcWarctoolsScraper]:
            self._scraper = class_(self.filename, True)
            self._scraper.scrape_file()

            # pylint: disable=protected-access
            if self._messages and not self._scraper.well_formed:
                self._messages = self._messages + self._scraper._messages
            else:
                self._messages = self._scraper._messages
            if self._errors and not self._scraper.well_formed:
                self._errors = self._errors + self._scraper._errors
            else:
                self._errors = self._scraper._errors

            if self._scraper.well_formed:
                for md_model in self._supported_metadata:
                    self.streams.append(md_model(self._scraper.streams))
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
        shell = ProcessRunner(["warcvalid", self.filename])

        if shell.returncode != 0:
            self._errors.append("Failed: returncode %s" % shell.returncode)
            # Filter some trash printed by warcvalid.
            filtered_errors = [line for line in shell.stderr.split(b"\n")
                               if b"ignored line" not in line]
            self._errors.append(ensure_text(b"\n".join(filtered_errors)))
            return

        self._messages.append(ensure_text(shell.stdout))

        warc_fd = gzip.open(self.filename)
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with io_open(self.filename, "rb") as warc_fd:
                line = warc_fd.readline()
        except Exception as exception:  # pylint: disable=broad-except
            # Compressed but corrupted gzip file
            self._errors.append(six.text_type(exception))
            warc_fd.close()
            return

        self._messages.append("File was analyzed successfully.")
        for md_class in self._supported_metadata:
            self.streams.append(md_class(line))
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
            shell = ProcessRunner(command=["arc2warc",
                                           encode_path(self.filename)],
                                  output_file=warcfile)
            if shell.returncode != 0:
                self._errors.append("Failed: returncode %s" %
                                    shell.returncode)
                # replace non-utf8 characters
                utf8string = shell.stderr.decode("utf8", errors="replace")
                # remove non-printable characters
                sanitized_string = sanitize_string(utf8string)
                # encode string to utf8 before adding to errors
                self._errors.append(
                    ensure_text(sanitized_string.encode("utf-8")))
                return
            self._messages.append("File was analyzed successfully.")
            self._messages.append(ensure_text(shell.stdout))

        for md_class in self._supported_metadata:
            self.streams.append(md_class())
