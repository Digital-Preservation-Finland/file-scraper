"""
Metadata scraper for pdf files, based on Ghostscript.

This scraper does not scrape metadata but instead checks well-formedness of pdf
versions 1.7, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u.
"""

import shutil
import re

from file_scraper.base import BaseScraper
from file_scraper.config import get_value
from file_scraper.ghostscript.ghostscript_model import GhostscriptMeta
from file_scraper.shell import Shell
from file_scraper.utils import encode_path, ensure_text
from file_scraper.defaults import UNAV


class GhostscriptScraper(BaseScraper):
    """Ghostscript pdf scraper."""

    # Supported mimetype and versions
    _supported_metadata = [GhostscriptMeta]
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        gs_path = get_value("GHOSTSCRIPT_PATH")
        if not gs_path and shutil.which("gs"):
            gs_path = shutil.which("gs")
        shell = Shell([
            gs_path, "-o", "/dev/null", "-sDEVICE=nullpage",
            encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append(
                f"Ghostscript returned invalid return code: "
                f"{shell.returncode}\n{shell.stderr}"
                )

        # Ghostscript may print characters which cannot be converted to UTF-8
        stdout_message = ensure_text(shell.stdout_raw, errors='replace')
        stderr_message = ensure_text(shell.stderr_raw, errors='replace')

        # Ghostscript will result 0 if it can repair errors.
        # However, in those cases an error is logged to either _errors or
        # _messages. This case should be handled as well-formed failure.
        if stderr_message:
            self._errors.append(stderr_message)
            self._errors.append(stdout_message)

        # If no errors have been logged, the file is valid.
        else:
            self._messages.append(stdout_message)
            self._messages.append("Well-Formed and valid")

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    @property
    def well_formed(self):
        """
        Overwrite the normal well-formedness check to also look at the stdout.

        This is needed as ghostscript can log errors to stdout if it has been
        able to repair the file. In these cases, scraper messages contain
        "**** Error" or "**** Warning" (any capitalization is detected), which
        is interpreted as well-formedness failure.

        :returns: True if the file is well-formed, False if it is not.
        """
        for message in self._messages:
            if ("**** error" in message.lower() or
                    "**** warning" in message.lower()):
                return False
        return super().well_formed

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNAV.
        """
        gs_path = get_value("GHOSTSCRIPT_PATH")
        if not gs_path and shutil.which("gs"):
            gs_path = shutil.which("gs")
        version_shell = Shell([gs_path, "-version"])
        regex = r"Ghostscript ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, version_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            version = UNAV

        self._tools = {"ghostscript": {
            "version": version
            }
        }
        return self._tools
