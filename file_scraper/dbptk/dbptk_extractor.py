"""A SIARD extractor module using DBPTK-developer.

This extractor does not scrape metadata but instead checks well-formedness
of SIARD files.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.logger import LOGGER
from file_scraper.defaults import UNAV
from file_scraper.dbptk.dbptk_model import DbptkMeta


class DbptkExtractor(BaseExtractor):
    """DBPTK (Database Prevervation Toolkit) extractor.
    Supports only SIARD files."""

    _supported_metadata = [DbptkMeta]
    _only_wellformed = True  # Only well-formed check

    def __init__(
        self,
        filename: Path,
        mimetype: str,
        version: str | None = None,
        params: dict | None = None,
    ) -> None:
        super().__init__(filename, mimetype, version, params)
        self._path = f"/usr/lib/jvm/jre-1.8.0/bin{os.pathsep} \
        {os.environ['PATH']}"

    def extract(self) -> None:
        """Scrape file using dbptk."""
        # Set $PATH so that Java 8 is favored if it's installed

        shell = Shell(["dbptk", "validate", "-if",
                       self.filename], env={"PATH": self._path})

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

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        # command without arguments prints default output,
        # which includes the version
        tool_shell = Shell(["dbptk"], env={"PATH": self._path})

        # Regex for finding the version of dbptk

        # Find string "DBPTK Developer (version"
        # optionally capture group of words, numbers, dashes and dots
        # until a closing parenthesis.

        try:
            version = next(
                re.finditer(r"DBPTK Developer \(version ([\w\-.]*)\)$",
                            tool_shell.stdout, re.MULTILINE)
            ).groups()[0]
            return {"DBPTK Developer": {"version":  version}}
        except StopIteration:
            LOGGER.warning(
                "Could not find version for dbptk from stdout: %s",
                tool_shell.stdout
            )
            self._errors.append("Could not parse version number from CLI "
                                "output")
            return {"DBPTK Developer": {"version": UNAV}}
