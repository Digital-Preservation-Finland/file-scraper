"""A HTML5 scraper module using The Nu Html Checker."""
from __future__ import unicode_literals

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
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        shell = Shell([
            "java", "-jar", VNU_PATH, "--verbose",
            self.filename])

        if shell.stderr:
            self._errors.append(shell.stderr)
        self._messages.append(shell.stdout)

        if self.well_formed:
            self.iterate_models(errors=self._errors)
            self._check_supported()
