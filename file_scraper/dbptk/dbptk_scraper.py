"""A SIARD scraper module using DBPTK-developer."""
from __future__ import unicode_literals

import zipfile

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.config import DBPTK_PATH
from file_scraper.dbptk.dbptk_model import DbptkMeta
from file_scraper.utils import decode_path


class DbptkScraper(BaseScraper):
    """DBPTK scraper. Supports only SIARD files."""

    _supported_metadata = [DbptkMeta]
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize DBPTK scraper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters needed for the scraper
        """
        self._version = None
        super(DbptkScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    def scrape_file(self):
        """Scrape file using dbptk-app.jar and check version within
        the file itself using zipfile.
        """
        shell = Shell([
            "java",
            "-jar",
            DBPTK_PATH,
            "validate",
            "-if",
            self.filename])

        report = shell.stdout

        if all(("Validation process finished the SIARD is valid." in report,
                "Number of errors [0]" in report)):
            self._messages.append(report)
        else:
            self._errors.append("Validator returned error.")
            self._errors.append(report)
            self._errors.append(shell.stderr)

        version_folders = []
        # The zipfile module prefer filepaths as strings
        filename = decode_path(self.filename)
        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename) as zipf:
                version_folders = [
                    x for x in zipf.namelist() if "header/siardversion" in x]
        for version_folder in version_folders:
            # Get version from siardversion path
            if not version_folder.endswith("siardversion/"):
                version = version_folder.strip("/").split("/")[-1]
                # Version 2.1 is identical to version 2.1.1
                if version == "2.1":
                    version = "2.1.1"
                self._version = version
                break

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, version=self._version))
        self._check_supported()
