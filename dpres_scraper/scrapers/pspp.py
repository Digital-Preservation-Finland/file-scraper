"""
This is an PSPP scraper.
"""

import os
import shutil
import tempfile
from dpres_scraper.base import BaseScraper, Shell


PSPP_PATH = '/usr/bin/pspp-convert'
SPSS_PORTABLE_HEADER = "SPSS PORT FILE"


class Pspp(BaseScraper):
    """
    PSPP scraper
    """
    _supported = {'application/x-spss-por': ['']}  # Supported mimetype
    _only_wellformed = True                        # Only well-formed check
    _allow_versions = True                         # Allow any version

    def scrape_file(self):
        """Scrape file
        """
        # Check file header
        with open(self.filename) as input_file:
            first_line = input_file.readline()
        if SPSS_PORTABLE_HEADER not in first_line:
            self.errors("File is not SPSS Portable format.")

        # Try to conver file with pspp-convert. If conversion is succesful
        # (converted.por file is produced), the original file is valid.
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'converted.por')

        try:
            shell = Shell([
                PSPP_PATH,
                self.filename,
                temp_file,
                ])
            self.errors(shell.stderr)
            self.messages(shell.stdout)
            if os.path.isfile(temp_file):
                self.messages('File conversion was succesful.')
            else:
                self.errors('File conversion failed.')
        finally:
            shutil.rmtree(temp_dir)
            self._check_supported()
            self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
