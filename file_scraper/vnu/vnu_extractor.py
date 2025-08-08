"""A HTML5 extractor module using The Nu Html Checker."""

import os
import re

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.logger import LOGGER
from file_scraper.vnu.vnu_model import VnuMeta
from file_scraper.defaults import UNAV


class VnuExtractor(BaseExtractor):
    """Vnu extractor. Supports only HTML version 5."""

    _supported_metadata = [VnuMeta]
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file using vnu.jar."""
        filterfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'vnu_filters.txt')
        shell = Shell([
                "vnu", "--verbose", "--filterfile", filterfile, self.filename
            ])

        if shell.stderr:
            self._errors.append(shell.stderr)
        if shell.returncode != 0:
            self._errors.append(
                f"Vnu returned invalid return code: {shell.returncode}\n"
                f"{shell.stderr}")
        self._messages.append(shell.stdout)

        if self.well_formed:
            self.streams = list(self.iterate_models(
                well_formed=self.well_formed))
            self._check_supported()

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        tool_shell = Shell(["vnu", "--version"])
        regex = r"([\d\.]+)"
        try:
            if tool_shell.returncode != 0:
                raise StopIteration
            version = next(
                re.finditer(regex, tool_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not retrieve VNU version from stdout: %s",
                tool_shell.stdout
            )
            version = UNAV

        return {
            "Validator.nu": {
                "version": version
            }
        }
