"""A HTML5 scraper module using The Nu Html Checker."""

from file_scraper.base import BaseScraper, Shell
from file_scraper.utils import metadata, ensure_str

VNU_PATH = "/usr/share/java/vnu/vnu.jar"


class Vnu(BaseScraper):
    """Vnu scraper. Supports only HTML version 5.0."""

    _supported = {'text/html': ['5.0']}  # Supported mimetypes
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file using vnu.jar."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        shell = Shell([
            'java', '-jar', VNU_PATH, '--verbose',
            self.filename])
        self.errors(ensure_str(shell.stderr))
        self.messages(ensure_str(shell.stdout))
        self._check_supported()
        self._collect_elements()

    @metadata()
    def _version(self):
        """Return version."""
        return '5.0'

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'text'
