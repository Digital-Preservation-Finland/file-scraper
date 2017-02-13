"""
This is an Office validator.
"""

from ipt.validator.basevalidator import BaseValidator, Shell

FILECMD_PATH = "/usr/local/file/bin/file"

class Office(BaseValidator):
    """
    Office valiator
    """
    _supported_mimetypes = {\
            'application/vnd.oasis.opendocument.text': [''],
            'application/vnd.oasis.opendocument.spreadsheet': [''],
            'application/vnd.oasis.opendocument.presentation': [''],
            'application/vnd.oasis.opendocument.graphics': [''],
            'application/vnd.oasis.opendocument.formula': [''],
            'application/msword': [''],
            'application/vnd.ms-excel': [''],
            'application/vnd.ms-powerpoint': [''],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.\
                    document': [''],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.\
                    sheet': [''],
            'application/vnd.openxmlformats-officedocument.presentationml.\
                    presentation': [''],
            # TODO: openxmlformats-officedocument or openxmlformatsofficedocument?
            'application/vnd.openxmlformatsofficedocument.wordprocessingml.\
                    document': [''],
            'application/vnd.openxmlformatsofficedocument.spreadsheetml.\
                    sheet': [''],
            'application/vnd.openxmlformatsofficedocument.presentationml.\
                    presentation': [''],\
            }

    def validate(self):
        """
        Validate file
        """
        shell = Shell([
            'soffice', '--convert-to', 'pdf', self.fileinfo['filename']])
        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._check_filetype()

    def _check_filetype(self):
        """
        Check MIME type determined by libmagic
        """
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-type', self.fileinfo['filename']])
        mimetype = shell.stdout.strip()
        if not self.fileinfo['format']['mimetype'] == mimetype:
            self.errors("MIME type does not match")
