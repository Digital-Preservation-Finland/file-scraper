"""A SIARD scraper module using DBPTK-developer.

This scraper does not scrape metadata but instead checks well-formedness
of SIARD files.
"""

import os
import re

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.dbptk.dbptk_model import DbptkMeta


class DbptkScraper(BaseScraper):
    """DBPTK (Database Prevervation Toolkit) scraper.
    Supports only SIARD files."""

    _supported_metadata = [DbptkMeta]
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename, mimetype, version=None, params=None):
        super().__init__(filename, mimetype, version, params)
        self._path = f"/usr/lib/jvm/jre-1.8.0/bin{os.pathsep} \
        {os.environ['PATH']}"

    def scrape_file(self):
        """Scrape file using dbptk."""
        # Set $PATH so that Java 8 is favored if it's installed

        shell = Shell([
            "dbptk",
            "validate",
            "-if",
            self.filename
        ], env={"PATH": self._path})

        report = shell.stdout

        # Read and parse validation report
        if all(("Validation process finished the SIARD is valid." in report,
                "Number of errors [0]" in report)):
            self._messages.append(report)
        else:
            self._errors.append("Validator returned error.")
            self._errors.append(report)
            self._errors.append(shell.stderr)

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_version=True)

    def tools(self):
        """
        Collect used software for the Scraper
        """
        # command without arguments prints default output,
        # which includes the version
        toolShell = Shell(["dbptk", ""], env={"PATH": self._path})
        """
        Regex for finding the version of dbptk

        Find string "DBPTK Developer (version"
        optionally capture group of words, numbers, dashes and dots
        until a closing parenthesis.
        """
        try:
            version = next(
                re.finditer(r"DBPTK Developer \(version ([\w\d\-.]*)\)$",
                            toolShell.stdout, re.MULTILINE)
            ).groups()[0]
            return {"dbptk-developer": {"version":  version}}
        except StopIteration:
            self._errors.append("Could not parse version number from CLI "
                                "output")
            return {"dbptk-developer": {"version": UNAV}}
