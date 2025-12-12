"""Warc file extractor."""

import gzip
import os.path
from io import open as io_open

from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAC
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
        self._validate()

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
