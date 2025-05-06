"""Module for pngcheck scraper."""

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.pngcheck.pngcheck_model import PngcheckMeta
from file_scraper.utils import encode_path
from file_scraper.defaults import UNAV
import re


class PngcheckScraper(BaseScraper):
    """
    Pngcheck scraper.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_metadata = [PngcheckMeta]
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        shell = Shell(["pngcheck", encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append("Pngcheck returned invalid return code: %s\n%s"
                                % (shell.returncode, shell.stderr))

        self._messages.append(shell.stdout)

        # This scraper does not know anything about the MIME type, so checking
        # is not useful. Just add metadata models.
        self.streams = list(self.iterate_models())

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def tools(self):
        """
        Collect used software for the Scraper
        """

        tool_shell = Shell(["pngcheck", "-v"], use_pty=True)
        """ Find version with capture group to capture integers and dots
            until any other character appears.
        """
        regex = r"[vV]ersion ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, tool_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            version = UNAV
        return {"pngcheck": {"version": version}}
