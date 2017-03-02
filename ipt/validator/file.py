"""
This is an File (libmagick) validator.
"""


from ipt.validator.basevalidator import BaseValidator, Shell


FILECMD_PATH = "/opt/file-5.30/bin/file"
FILE_LIBRARY_PATH = "/opt/file-5.30/lib64"


class File(BaseValidator):
    """
    File (libmagick) validator checks MIME-type
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
        'presentation': ['12.0', '14.0', '15.0'],
        'image/x-dpx': ['2.0'],
        'image/png': [''],
        'image/jpeg': ['1.00', '1.01', '1.02'],
        'image/jp2': [''],
        'image/tiff': ['6.0'],
    }


    def validate(self):
        """
        Check MIME type determined by libmagic
        """
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-type', self.fileinfo['filename']],
                      ld_library_path=FILE_LIBRARY_PATH)
        self.messages(shell.stdout)
        self.errors(shell.stderr)
        mimetype = shell.stdout.strip()
        if not self.fileinfo['format']['mimetype'] == mimetype:
            self.errors("MIME type does not match")
        else:
            self.messages("MIME type is correct")
