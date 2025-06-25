"""PSPP scraper."""

import os
import shutil
import tempfile
import re
from io import open as io_open

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.logger import LOGGER
from file_scraper.pspp.pspp_model import PsppMeta

SPSS_PORTABLE_HEADER = b"SPSS PORT FILE"


class PsppScraper(BaseScraper):
    """PSPP scraper."""

    _supported_metadata = [PsppMeta]
    _only_wellformed = True                        # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        # Check file header
        with io_open(self.filename, "rb") as input_file:
            first_line = input_file.readline()
        if first_line.count(SPSS_PORTABLE_HEADER) != 1:
            self._errors.append("File is not SPSS Portable format.")

        # Try to convert file with pspp-convert. If conversion is succesful
        # (converted.por file is produced), the original file is well-formed.
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "converted.por")

        try:
            shell = Shell([
                "pspp-convert",
                self.filename,
                temp_file
            ])
            if shell.stderr:
                self._errors.append(shell.stderr)
            if shell.returncode != 0:
                self._errors.append(
                    f"PSPP returned invalid return code: {shell.returncode}\n"
                    f"{shell.stderr}")
            self._messages.append(shell.stdout)
            if os.path.isfile(temp_file):
                self._messages.append("File conversion was succesful.")
            else:
                self._errors.append("File conversion failed.")
        finally:
            shutil.rmtree(temp_dir)
            self.streams = list(self.iterate_models(
                well_formed=self.well_formed))
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNAV.
        """
        tool_shell = Shell(["pspp-convert", "--version"])

        regex = r"\(GNU PSPP\) ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, tool_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.debug(
                "Could not parse PSPP version from stdout: %s",
                tool_shell.stdout
            )
            version = UNAV
        return {"GNU PSPP": {"version": version}}
