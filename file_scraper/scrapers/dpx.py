"""DPX V2.0 scraper
"""
from file_scraper.base import BaseScraper, Shell


class Dpx(BaseScraper):
    """DPX scraper
    """

    _supported = {'image/x-dpx': ['2.0']}  # Supported mimetype and version
    _only_wellformed = True                # Only well-formed check

    def scrape_file(self):
        """Scrape DPX.
        """
        shell = Shell(['dpxv', self.filename])

        if shell.returncode != 0:
            raise DPXvError(shell.stderr)

        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._check_supported()
        self._collect_elements()

    def _s_version(self):
        """Return version
        """
        return '2.0'

    def _s_stream_type(self):
        """Return file type
        """
        return 'image'


class DPXvError(Exception):
    """DPX validator error."""
    pass
