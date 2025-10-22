"""Warc file extractor."""

import gzip
import os.path
from io import open as io_open

from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAC, UNAV
from file_scraper.logger import LOGGER
from file_scraper.shell import Shell
from file_scraper.warctools.warctools_model import WarctoolsMeta


class WarctoolsExtractor(BaseExtractor[WarctoolsMeta]):
    """
    Implements WARC file format extractor for metadata collecting.

    This extractor uses Internet Archives warctools extractor.

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
        return super().is_supported(
            mimetype, version, check_wellformed, params)

    def extract(self):
        """Scrape WARC file."""
        try:
            # First assume archive is compressed
            with gzip.open(self.filename) as warc_fd:
                line = warc_fd.readline()
                LOGGER.debug("WARC %s is GZIP compressed", self.filename)
        except OSError:
            # Not compressed archive
            with io_open(self.filename, "rb") as warc_fd:
                line = warc_fd.readline()
                LOGGER.debug(
                    "WARC %s is uncompressed", self.filename
                )
        except Exception as exception:  # pylint: disable=broad-except
            # Compressed but corrupted gzip file
            self._errors.append(str(exception))
            return

        self._messages.append("File was analyzed successfully.")
        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, line=line))
        self._check_supported()

    def tools(self):
        return {}


class WarctoolsFullExtractor(WarctoolsExtractor):
    """
    Implements WARC file format extractor for validation.

    This extractor uses Internet Archives warctools extractor.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_metadata = [WarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Use the default is_supported method from BaseExtractor.
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

    def extract(self):
        """Scrape WARC file."""
        size = os.path.getsize(self.filename)
        if size == 0:
            self._errors.append("Empty file.")
            return
        shell = Shell(["warcvalid", self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"Warctools returned invalid return code: "
                f"{shell.returncode}\n{shell.stderr}")
            # Filter some trash printed by warcvalid.
            filtered_errors = [line for line in shell.stderr.split("\n")
                               if "ignored line" not in line]
            self._errors.append("\n".join(filtered_errors))
            return

        self._messages.append(shell.stdout)

        super().extract()

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        # TODO TPASPKT-1506 add version information to warctools.
        return {"warctools": {"version": UNAC}}


class GzipWarctoolsExtractor(WarctoolsFullExtractor):
    """Extractor for compressed Warcs."""

    _supported_metadata = [WarctoolsMeta]
    _only_wellformed = True  # Only well-formed check

    def info(self):
        """
        Return extractor info.

        If WarctoolsExtractor could scrape the gzip file,
        that class is reported as the extractor class. For failures,
        the class is GzipWarctoolsExtractor.
        """
        info = super().info()
        if self.streams:
            info["class"] = "WarctoolsFullExtractor"
        return info

    def _check_supported(self, allow_unav_mime=False, allow_unav_version=False,
                         allow_unap_version=False):
        """
        Check that the scraped MIME type and version are supported.

        This extractor uses the Warc extractor to check the file and get the
        metadata, so in addition to the normal metadata model check, it is also
        sufficient if the Warc extractor supports the MIME type and
        version combination.
        """
        if not self.streams:
            self._errors.append("MIME type not supported by this extractor.")

        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()
        if version == UNAV:
            version = None

        # Check own metadata models for support: if supporting model is found,
        # no further checking is needed.
        for md_class in self._supported_metadata:
            if mimetype in md_class.supported_mimetypes():
                return

        # also check the used extractor class: final result of warc,
        # corresponding to the compressed file, is also ok
        if WarctoolsFullExtractor.is_supported(mimetype, version):
            return

        self._errors.append(
            f"MIME type {mimetype} with version {version} is not supported.")
