"""A HTML5 scraper module using The Nu Html Checker."""
from __future__ import unicode_literals

import os

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.config import VNU_PATH
from file_scraper.vnu.vnu_model import VnuMeta


class VnuScraper(BaseScraper):
    """Vnu scraper. Supports only HTML version 5.0."""

    _supported_metadata = [VnuMeta]
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file using vnu.jar."""
        filterfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vnu_filters.txt')
        shell = Shell([
            "java", "-jar", VNU_PATH, "--verbose",
            "--filterfile", filterfile,
            self.filename])

        if shell.stderr:
            self._errors.append(shell.stderr)
        self._messages.append(shell.stdout)

        if self.well_formed:
            self.streams = list(self.iterate_models(
                well_formed=self.well_formed))
            self._check_supported()
