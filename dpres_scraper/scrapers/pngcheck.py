"""Module for pngcheck scraper"""

from dpres_scraper.base import BaseScraper, Shell


class Pngcheck(BaseScraper):

    """ Pngcheck scraper
    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported = {'image/png': []}  # Supported mimetype
    _only_wellformed = True         # Only well-formed check

    def scrape_file(self):
        """Scrape file
        """

        shell = Shell(['pngcheck', self.filename])

        if shell.returncode != 0:
            self.errors("Failed: returncode %s" % shell.returncode)
            self.errors(shell.stderr)

        self.messages(shell.stdout)
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'image'
