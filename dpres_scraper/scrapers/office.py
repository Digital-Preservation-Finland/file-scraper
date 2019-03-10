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
    # Supported mimetypes and versions
    _supported = {
        'application/vnd.oasis.opendocument.text': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.spreadsheet': [
            '1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.presentation': [
            '1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.graphics': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.formula': ['1.0', '1.2'],
        'application/msword': ['8.0', '8.5', '9.0', '10.0', '11.0'],
        'application/vnd.ms-excel': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.ms-powerpoint': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        'document': ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.'
        'spreadsheetml.sheet': ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.presentationml.'
        'presentation': ['12.0', '14.0', '15.0']}
    _allow_versions = True  # Allow any version
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
            self._check_supported()
            self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
