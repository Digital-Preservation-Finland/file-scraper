"""A HTML5 scraper module using The Nu Html Checker."""

from file_scraper.base import BaseScraper, Shell
from file_scraper.vnu.vnu_model import VnuMeta
from file_scraper.utils import ensure_str

VNU_PATH = "/usr/share/java/vnu/vnu.jar"


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
            self._errors.append(ensure_str(shell.stderr))
        self._messages.append(ensure_str(shell.stdout))

        if self.well_formed:
            for md_class in self._supported_metadata:
                self.streams.append(md_class())
            self._check_supported()
