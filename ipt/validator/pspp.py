"""
This is an PSPP validator.
"""


import os
import shutil
import tempfile
from ipt.validator.basevalidator import BaseValidator, Shell


PSPP_PATH = '/opt/pspp-0.8.5/bin/pspp-convert'
SPSS_PORTABLE_HEADER = "SPSS PORT FILE"


class PSPP(BaseValidator):
    """
    PSPP validator
    """
    _supported_mimetypes = {
        "application/x-spss-por": [""],
    }

    def validate(self):
        """
        Validate file
        """
        # Check file header
        self._check_header()

        # Try to conver file with pspp-convert
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'converted.por')

        try:
            shell = Shell([
                PSPP_PATH,
                self.fileinfo['filename'],
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

    def _check_header(self):
        """
        Check that file header contains SPSS_PORTABLE_HEADER-string
        """
        with open(self.fileinfo['filename']) as input_file:
            first_line = input_file.readline()
        if not SPSS_PORTABLE_HEADER in first_line:
            self.errors("File is not SPSS Portable format.")
