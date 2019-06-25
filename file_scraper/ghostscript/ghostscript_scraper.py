"""
Metadata scraper for pdf files, based on Ghostscript.

This scraper does not scrape metadata but instead checks well-formedness of pdf
versions 1.7, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u.
"""

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.ghostscript.ghostscript_model import GhostscriptMeta


class GhostscriptScraper(BaseScraper):
    """Ghostscript pdf scraper."""

    # Supported mimetype and versions
    _supported_metadata = [GhostscriptMeta]
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return
        shell = ProcessRunner([
            "gs", "-o", "/dev/null", "-sDEVICE=nullpage",
            self.filename])

        for model in self._supported_metadata:
            self.streams.append(model())

        # Ghostscript will result 0 if it can repair errors.
        # However, in those cases an error is logged to either _errors or
        # _messages. This case should be handled as well-formed failure.
        if shell.stderr:
            self._errors.append(shell.stderr.decode("iso-8859-1").
                                encode("utf8"))
        elif shell.returncode != 0:
            self._errors.append("Ghostscript returned return code: %s"
                                % shell.returncode)
        self._messages.append(shell.stdout.decode("iso-8859-1").encode("utf8"))

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    @property
    def well_formed(self):
        """
        Overwrite the normal well-formedness check to also look at the stdout.

        This is needed as ghostscript can log errors to stdout if it has been
        able to repair the file. In these cases, scraper messages contain
        "**** Error" or "**** Warning" (any capitalization is detected), which
        is interpreted as well-formedness failure.

        :returns: True if the file is well-formed, False if it is not.
        """
        for message in self._messages:
            if ("**** error" in message.lower() or
                    "**** warning" in message.lower()):
                return False
        return super(GhostscriptScraper, self).well_formed
