"""
This is an Office validator.
"""


from ipt.validator.basevalidator import BaseValidator, Shell
import tempfile
import shutil


FILECMD_PATH = "/usr/local/file/bin/file"


class Office(BaseValidator):
    """
    Office valiator
    """
    _supported_mimetypes = {
        'application/vnd.oasis.opendocument.text': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.spreadsheet':
            ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.presentation':
            ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.graphics': ['1.0', '1.1', '1.2'],
        'application/vnd.oasis.opendocument.formula': ['1.0', '1.1', '1.2'],
        'application/msword': ['8.0', '8.5', '9.0', '10.0', '11.0'],
        'application/vnd.ms-excel': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.ms-powerpoint': ['8.0', '9.0', '10.0', '11.0'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        'document': ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            ['12.0', '14.0', '15.0'],
        'application/vnd.openxmlformats-officedocument.presentationml.'
        'presentation': ['12.0', '14.0', '15.0']
    }


    def validate(self):
        """
        Validate file
        """
        temp_dir = tempfile.mkdtemp()
        try:
            shell = Shell([
                'soffice', '--convert-to', 'pdf', '--outdir', temp_dir,
                self.fileinfo['filename']])
        finally:
            shutil.rmtree(temp_dir)

        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._check_filetype()
        self._check_version()


    def _check_filetype(self):
        """
        Check MIME type determined by libmagic
        """
        tempfile.mkdtemp
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-type', self.fileinfo['filename']])
        mimetype = shell.stdout.strip()
        if not self.fileinfo['format']['mimetype'] == mimetype:
            self.errors("MIME type does not match")


    def _check_version(self):
        """
        Check that version is supported
        """
        if not self.is_supported(self.fileinfo):
            self.errors("Version not supported")
