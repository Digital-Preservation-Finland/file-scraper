"""Module for pngcheck scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.pngcheck.pngcheck_model import PngcheckMeta
from file_scraper.utils import encode_path


class PngcheckScraper(BaseScraper):
    """
    Pngcheck scraper.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_metadata = [PngcheckMeta]
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        shell = Shell(["pngcheck", encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append("Failed: returncode %s" % shell.returncode)
            self._errors.append(shell.stderr)

        self._messages.append(shell.stdout)

        # This scraper does not know anything about the MIME type, so checking
        # is not useful. Just add metadata models.
        for md_class in self._supported_metadata:
            self.streams.append(md_class(self._given_mimetype,
                                         self._given_version))

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
