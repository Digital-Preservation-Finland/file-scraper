"""Module for pngcheck extractor."""
import re

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.logger import LOGGER
from file_scraper.pngcheck.pngcheck_model import PngcheckMeta
from file_scraper.defaults import UNAV


class PngcheckExtractor(BaseExtractor[PngcheckMeta]):
    """
    Pngcheck extractor.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_metadata = [PngcheckMeta]
    _only_wellformed = True              # Only well-formed check

    _allow_unav_mime = True
    _allow_unav_version = True

    def extract(self):
        """Scrape file."""
        shell = Shell(["pngcheck", self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"Pngcheck returned invalid return code: {shell.returncode}"
                f"\n{shell.stderr}")

        self._messages.append(shell.stdout)

        # This extractor does not know anything about the MIME type,
        # so checking is not useful. Just add metadata models.
        self.streams = list(self.iterate_models())

        self._validate()

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """

        tool_shell = Shell(["pngcheck"], use_pty=True)
        # Find version with capture group to capture integers and dots
        # until any other character appears.
        regex = r"[vV]ersion ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, tool_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not find pngcheck version from stdout: %s",
                tool_shell.stdout
            )
            version = UNAV
        return {"PNGcheck": {"version": version}}
