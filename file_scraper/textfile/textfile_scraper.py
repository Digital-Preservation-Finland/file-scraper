"""Module for checking if the file is uitable as text file or not."""
from file_scraper.base import BaseScraper, Shell
from file_scraper.textfile.textfile_model import TextFileMeta
from file_scraper.utils import ensure_str

FILECMD_PATH = "/opt/file-5.30/bin/file"
ENV = {"LD_LIBRARY_PATH": "/opt/file-5.30/lib64"}


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
        shell = Shell([
            FILECMD_PATH, "-be", "soft", "--mime-type",
            self.filename], env=ENV)
        if shell.stderr:
            self._errors.append(shell.stderr)

        return ensure_str(shell.stdout).strip()

    def scrape_file(self):
        """Check MIME type determined by libmagic."""
        self._messages.append("Trying text detection...")

        mimetype = self._file_mimetype()
        if mimetype == "text/plain":
            self._messages.append("File is a text file.")
            for md_class in self._supported_metadata:
                self.streams.append(md_class())
        else:
            self._errors.append("File is not a text file")
