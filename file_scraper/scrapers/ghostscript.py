"""PDF scraper implemented with ghostscript."""

from file_scraper.base import BaseScraper, Shell
from file_scraper.utils import metadata


class GhostScript(BaseScraper):
    """Ghostscript pdf scraper."""

    # Supported mimetype and versions
    _supported = {'application/pdf': ['1.7', 'A-2a', 'A-2b',
                                      'A-2u', 'A-3a', 'A-3b', 'A-3u']}
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        shell = Shell([
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage',
            self.filename])

        # Ghostscript will result 0 if it can repair errors.
        # However, stderr is not then empty.
        # This case should be handled as well-formed failure.
        if shell.stderr:
            self.errors(shell.stderr.decode('iso-8859-1').encode('utf8'))
        elif shell.returncode != 0:
            self.errors("Ghostscript returned return code: %s"
                        % shell.returncode)
        self.messages(shell.stdout.decode('iso-8859-1').encode('utf8'))
        self._check_supported()
        self._collect_elements()

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'binary'
