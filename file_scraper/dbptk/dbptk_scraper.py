"""A SIARD scraper module using DBPTK-developer.

This scraper does not scrape metadata but instead checks well-formedness
of SIARD files.
"""

import os

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.dbptk.dbptk_model import DbptkMeta


class DbptkScraper(BaseScraper):
    """DBPTK scraper. Supports only SIARD files."""

    _supported_metadata = [DbptkMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file using dbptk."""
        # Set $PATH so that Java 8 is favored if it's installed
        path = f"/usr/lib/jvm/jre-1.8.0/bin{os.pathsep}{os.environ['PATH']}"
        shell = Shell([
            "dbptk",
            "validate",
            "-if",
            self.filename
        ], env={"PATH": path})

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
