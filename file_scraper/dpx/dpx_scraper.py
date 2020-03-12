"""DPX scraper"""

from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.utils import encode_path


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True

    def scrape_file(self):
        """Scrape DPX."""
        shell = Shell(["dpxv", encode_path(self.filename)])

        if shell.returncode != 0:
            raise DPXvError(shell.stderr)

        if shell.stderr:
            self._errors += list(shell.stderr.splitlines())

        if shell.stdout:
            self._messages += list(shell.stdout.splitlines())

        self.iterate_models(errors=self._errors,
                            messages=self._messages,
                            filename=self.filename)

        self._check_supported()


class DPXvError(Exception):
    """DPX scraper error."""
    pass
