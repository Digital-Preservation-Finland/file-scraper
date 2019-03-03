"""There is a need for a separate softer check, if the file is suitable as
text file or not.
"""
from dpres_scraper.base import BaseScraper, Shell

FILECMD_PATH = "/opt/file-5.30/bin/file"
ENV = {'LD_LIBRARY_PATH': "/opt/file-5.30/lib64"}


class TextPlainFile(BaseScraper):
    """
    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.
    """

    def _file_mimetype(self):
        """Detect mimetype with the soft option that
        excludes libmagick.

        :returns: file mimetype
        """
        shell = Shell([
            FILECMD_PATH, '-be', 'soft', '--mime-type',
            self.filename], env=ENV)

        self.errors(shell.stderr)
        mimetype = shell.stdout.strip()

        return mimetype

    def scrape_file(self):
        """
        Check MIME type determined by libmagic
        """
        self.messages('Trying text detection...')
        mimetype = self._file_mimetype()
        if mimetype == 'text/plain':
            self.messages('File is a text file.')
        else:
            self.errors("File is not a text file")
        self._collect_elements()

    def _s_stream_type(self):
        """Return stream type
        """
        return None
