"""PSPP scraper."""
from __future__ import unicode_literals

import os
import shutil
import tempfile
from io import open as io_open

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.config import PSPP_PATH
from file_scraper.pspp.pspp_model import PsppMeta

SPSS_PORTABLE_HEADER = b"SPSS PORT FILE"


class PsppScraper(BaseScraper):
    """PSPP scraper."""

    _supported_metadata = [PsppMeta]
    _only_wellformed = True                        # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        # Check file header
        with io_open(self.filename, "rb") as input_file:
            first_line = input_file.readline()
        if SPSS_PORTABLE_HEADER not in first_line:
            self._errors.append("File is not SPSS Portable format.")

        # Try to convert file with pspp-convert. If conversion is succesful
        # (converted.por file is produced), the original file is well-formed.
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "converted.por")

        try:
            shell = Shell([
                PSPP_PATH,
                self.filename,
                temp_file
            ])
            if shell.stderr:
                self._errors.append(shell.stderr)
            self._messages.append(shell.stdout)
            if os.path.isfile(temp_file):
                self._messages.append("File conversion was succesful.")
            else:
                self._errors.append("File conversion failed.")
        finally:
            shutil.rmtree(temp_dir)
            for md_class in self._supported_metadata:
                self.streams.append(md_class(self._given_mimetype,
                                             self._given_version))
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
