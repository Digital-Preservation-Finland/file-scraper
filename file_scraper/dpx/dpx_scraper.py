"""DPX V2.0 scraper."""
from file_scraper.base import BaseScraper, Shell
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.utils import ensure_str


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True                # Only well-formed check

    def scrape_file(self):
        """Scrape DPX."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        shell = Shell(["dpxv", self.filename])

        if shell.returncode != 0:
            raise DPXvError(ensure_str(shell.stderr))

        if shell.stderr:
            self._errors.append(ensure_str(shell.stderr))
        if shell.stdout:
            self._messages.append(ensure_str(shell.stdout))

        for md_class in self._supported_metadata:
            self.streams.append(md_class())

        self._check_supported()


class DPXvError(Exception):
    """DPX scraper error."""
    pass
