"""DPX scraper"""

from __future__ import unicode_literals

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.utils import ensure_text, encode_path


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]

    def scrape_file(self):
        """Scrape DPX."""

        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: "
                                  "Well-formed check not used.")
            return

        shell = ProcessRunner(["dpxv", encode_path(self.filename)])

        if shell.returncode != 0:
            raise DPXvError(ensure_text(shell.stderr))

        if shell.stderr:
            for err in ensure_text(shell.stderr).splitlines():
                self._errors.append(err)

        if shell.stdout:
            for out in ensure_text(shell.stdout).splitlines():
                self._messages.append(out)

        for md_class in self._supported_metadata:
            self.streams.append(
                md_class(
                    mimetype=self._given_mimetype,
                    version=self._given_version,
                    info=self.info(),
                    filename=self.filename))

        self._check_supported()


class DPXvError(Exception):
    """DPX scraper error."""
    pass
