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
        # file-5.30 does not reliably recognize all DPX files
        # 'image/x-dpx': ['2.0'],
        'image/png': [''],
        'image/jpeg': ['1.00', '1.01', '1.02'],
        'image/jp2': [''],
        'image/tiff': ['6.0'],
        'text/plain': ['']
    }

    def validate(self):
        """
        Check MIME type determined by libmagic
        """
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-type', self.metadata_info['filename']],
                      ld_library_path=FILE_LIBRARY_PATH)
        self.errors(shell.stderr)
        mimetype = shell.stdout.strip()
        if not self.metadata_info['format']['mimetype'] == mimetype:

            # Allow text/plain as mimetype in metadata_info
            # for any text based file.
            if self.metadata_info['format']['mimetype'] == 'text/plain':
                shell = Shell([
                    FILECMD_PATH, '-be', 'soft', '--mime-type',
                    self.metadata_info['filename']],
                              ld_library_path=FILE_LIBRARY_PATH)
                mimetype_soft = shell.stdout.strip()
                if not self.metadata_info['format']['mimetype'] == \
                        mimetype_soft:
                    self.errors("MIME type does not match")
                else:
                    self.messages(
                        "Detected mimetype %s "
                        "instead of reported mimetype %s.\n"
                        "The digital object is a valid text file and will be "
                        "preserved as text/plain." % (
                            mimetype,
                            self.metadata_info['format']['mimetype']))
                    self.validator_info = self.metadata_info

            else:
                self.errors("MIME type does not match")
        else:
            self.messages(shell.stdout)
            self.messages("MIME type is correct")
            self.validator_info = self.metadata_info


class FileEncoding(BaseValidator):
    """
    Character encoding validator for text files
    """

    _supported_mimetypes = {
        'text/csv': [''],
        'text/plain': [''],
        'text/xml': ['1.0'],
        'text/html': ['4.01', '5.0'],
        'application/xhtml+xml': ['1.0', '1.1']
    }

    # We use JHOVE for UTF-8 validation
    _encodings = {
        'ISO-8859-15': ['us-ascii', 'iso-8859-1'],
        'UTF-16': ['utf-16', 'utf-16be', 'utf-16le']
    }

    @classmethod
    def is_supported(cls, metadata_info):
        """
        Check supported mimetypes.
        :metadata_info: metadata_info
        """
        if metadata_info['format']['mimetype'] in cls._supported_mimetypes:
            if metadata_info['format']['charset'] not in \
                    list(cls._encodings.keys()):
                return False
        return super(FileEncoding, cls).is_supported(metadata_info)

    def validate(self):
        """
        Check character encoding
        """
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-encoding',
            self.metadata_info['filename']],
                      ld_library_path=FILE_LIBRARY_PATH)
        self.messages(shell.stdout)
        self.errors(shell.stderr)
        encoding = shell.stdout.strip()
        if encoding in self._encodings[
                self.metadata_info['format']['charset']]:
            self.messages("File encoding match found.")
            self.validator_info = self.metadata_info
        else:
            err = " ".join(
                ["File encoding mismatch:", encoding, "was found, but",
                 self.metadata_info['format']['charset'], "was expected."])
            self.errors(err)
