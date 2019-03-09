"""
This is an Office file scraper.
"""
import tempfile
import shutil
from dpres_scraper.base import BaseScraper, Shell


class Office(BaseScraper):
    """
    Office file format scraper
    """
    # Supported mimetypes
    _supported = {
        'application/vnd.oasis.opendocument.text': [],
        'application/vnd.oasis.opendocument.spreadsheet': [],
        'application/vnd.oasis.opendocument.presentation': [],
        'application/vnd.oasis.opendocument.graphics': [],
        'application/vnd.oasis.opendocument.formula': [],
        'application/msword': [],
        'application/vnd.ms-excel': [],
        'application/vnd.ms-powerpoint': [],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        'document': [],
        'application/vnd.openxmlformats-officedocument.'
        'spreadsheetml.sheet': [],
        'application/vnd.openxmlformats-officedocument.presentationml.'
        'presentation': []}
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file
        """
        temp_dir = tempfile.mkdtemp()
        try:
            env = {'HOME': temp_dir}
            shell = Shell([
                'soffice', '--convert-to', 'pdf', '--outdir', temp_dir,
                self.filename], env=env)
            self.errors(shell.stderr)
            self.messages(shell.stdout)
        finally:
            shutil.rmtree(temp_dir)
            self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
