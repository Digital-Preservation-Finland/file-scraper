"""
A HTML5 scraper module using The Nu Html Checker
(https://scraper.github.io/scraper/)
"""

from file_scraper.base import BaseScraper, Shell

VNU_PATH = "/usr/share/java/vnu/vnu.jar"


class Vnu(BaseScraper):
    """
    Vnu scraper supports only HTML version 5.0.
    """

    _supported = {'text/html': ['5.0']}  # Supported mimetypes
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """
        Scrape file using vnu.jar
        """
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        shell = Shell([
            'java', '-jar', VNU_PATH, '--verbose',
            self.filename])
        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._check_supported()
        self._collect_elements()

    def _s_version(self):
        """Return version
        """
        return '5.0'

    def _s_stream_type(self):
        """Return file type
        """
        return 'text'
