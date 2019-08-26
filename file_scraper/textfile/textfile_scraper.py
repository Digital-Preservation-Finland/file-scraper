"""Module for checking if the file is uitable as text file or not."""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.config import FILECMD_PATH, LD_LIBRARY_PATH
from file_scraper.textfile.textfile_model import TextFileMeta
from file_scraper.utils import encode_path, ensure_text

ENV = {"LD_LIBRARY_PATH": LD_LIBRARY_PATH}


class TextfileScraper(BaseScraper):
    """
    Text file detection scraper.

    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.
    """

    _supported_metadata = [TextFileMeta]

    def _file_mimetype(self):
        """
        Detect mimetype with the soft option that excludes libmagick.

        :returns: file mimetype
        """
        shell = ProcessRunner([
            FILECMD_PATH, "-be", "soft", "--mime-type",
            encode_path(self.filename)], env=ENV)
        if shell.stderr:
            self._errors.append(ensure_text(shell.stderr))

        return ensure_text(shell.stdout).strip()

    def scrape_file(self):
        """Check MIME type determined by libmagic."""
        self._messages.append("Trying text detection...")

        mimetype = self._file_mimetype()
        if mimetype == "text/plain":
            self._messages.append("File is a text file.")
            for md_class in self._supported_metadata:
                self.streams.append(md_class())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
        else:
            self._errors.append("File is not a text file")
