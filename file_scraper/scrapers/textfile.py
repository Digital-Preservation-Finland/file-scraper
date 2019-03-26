"""Module for checking if the file is uitable as text file or not."""
from file_scraper.base import BaseScraper, Shell
from file_scraper.utils import metadata, ensure_str

FILECMD_PATH = "/opt/file-5.30/bin/file"
ENV = {'LD_LIBRARY_PATH': "/opt/file-5.30/lib64"}


class CheckTextFile(BaseScraper):
    """
    Text file detection scraper.

    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.
    """

    def _file_mimetype(self):
        """
        Detect mimetype with the soft option that excludes libmagick.

        :returns: file mimetype
        """
        shell = Shell([
            FILECMD_PATH, '-be', 'soft', '--mime-type',
            self.filename], env=ENV)

        self.errors(shell.stderr)
        mimetype = ensure_str(shell.stdout).strip()

        return mimetype

    def scrape_file(self):
        """Check MIME type determined by libmagic."""
        self.messages('Trying text detection...')
        mimetype = self._file_mimetype()
        if mimetype == 'text/plain':
            self.messages('File is a text file.')
        else:
            self.errors("File is not a text file")
        self._collect_elements()

    @metadata()
    def _s_stream_type(self):
        """Return stream type."""
        return None
