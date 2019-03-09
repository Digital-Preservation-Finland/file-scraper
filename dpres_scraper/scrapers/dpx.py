"""
This is an DPX V2.0 scraper
"""
from dpres_scraper.base import BaseScraper, Shell


class Dpx(BaseScraper):
    """DPX scraper
    """

    _supported = {'image/x-dpx': []}  # Supported mimetype
    _only_wellformed = True           # Only well-formed check

    def scrape_file(self):
        """Scrape DPX.
        """
        shell = Shell(['dpxv', self.filename])

        if shell.returncode != 0:
            raise DPXvError(shell.stderr)

        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'image'


class DPXvError(Exception):
    """DPX validator error."""
    pass
