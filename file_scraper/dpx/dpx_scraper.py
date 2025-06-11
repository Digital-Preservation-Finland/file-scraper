"""DPX scraper"""

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.defaults import UNKN


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True

    def scrape_file(self):
        """Scrape DPX."""

        shell = Shell(["dpxv-3", self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"DPX returned invalid return code: {shell.returncode}\n"
                f"{shell.stderr}")

        if shell.stderr:
            self._errors += list(shell.stderr.splitlines())

        if shell.stdout:
            self._messages += list(shell.stdout.splitlines())

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, messages=self._messages,
            filename=self.filename))

        self._check_supported()

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNKN.
        """
        # TODO TPASPKT-1502 dpx_validator is hardcoded to work from
        # an rpm package and the validator cli doesn't have a get version flag
        # or command, so the version is not currently available.
        return {"Python DPX validator": {"version": UNKN}}
