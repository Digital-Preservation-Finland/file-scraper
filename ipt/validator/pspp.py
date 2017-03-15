"""
This is an PSPP validator.
"""


import os
import shutil
import tempfile
from ipt.validator.basevalidator import BaseValidator, Shell


FORMAT_STRINGS = {
    "application/x-spss-por": "adsf",
}

PSPP_PATH = '/opt/pspp-0.8.5/bin/pspp-convert'


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
