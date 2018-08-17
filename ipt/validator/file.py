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
        'image/tiff': ['6.0']
    }

    def validate(self):
        """
        Check MIME type determined by libmagic
        """
        shell = Shell([
            FILECMD_PATH, '-b', '--mime-type', self.metadata_info['filename']],
                      ld_library_path=FILE_LIBRARY_PATH)
        self.messages(shell.stdout)
        self.errors(shell.stderr)
        mimetype = shell.stdout.strip()
        if not self.metadata_info['format']['mimetype'] == mimetype:
            self.errors("MIME type does not match")
        else:
            self.messages("MIME type is correct")
            self.validator_info = self.metadata_info


class FileTextPlain(BaseValidator):
    """
    file (libmagick) validator checks mime-type and if it is a text
    file with the soft option that excludes libmagick.

    All text files are accepted as text/plain.
    """
    _supported_mimetypes = {
        'text/plain': ['']
    }

    def file_mimetype(self, soft=False):
        """Detect mimetype using file (libmagick) or with
        the soft option that excludes libmagick.

        :soft: use file with soft option if true

        :returns: file mimetype
        """
        if soft:
            shell = Shell([
                FILECMD_PATH, '-be', 'soft', '--mime-type',
                self.metadata_info['filename']],
                          ld_library_path=FILE_LIBRARY_PATH)
        else:
            shell = Shell([
                FILECMD_PATH, '-b', '--mime-type',
                self.metadata_info['filename']],
                          ld_library_path=FILE_LIBRARY_PATH)

        self.errors(shell.stderr)
        mimetype = shell.stdout.strip()

        return mimetype

    def validate(self):
        """
        Check MIME type determined by libmagic
        """

        mimetype = self.file_mimetype()
        self.messages('Detected mimetype: %s' % mimetype)

        if self.metadata_info['format']['mimetype'] == mimetype:
            self.messages("MIME type is correct")
            self.validator_info = self.metadata_info
            return

        self.messages('METS mimetype is text/plain, trying text detection')

        mimetype = self.file_mimetype(soft=True)

        self.messages('Detected alternative mimetype: %s' % mimetype)

        if self.metadata_info['format']['mimetype'] == mimetype:
            self.messages("MIME type is correct. The "
                          "digital object will be preserved as text/plain.")
            self.validator_info = self.metadata_info
            return

        self.errors("MIME type does not match")


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
