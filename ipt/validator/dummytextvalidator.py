"""Validator for plain text files"""

from ipt.validator.basevalidator import BaseValidator


class DummyTextValidator(BaseValidator):

    """Validator for plain text files"""

    @classmethod
    def is_supported(cls, fileinfo):
        """
        Check suported mimetypes.
        :fileinfo: fileinfo
        """
        if fileinfo['format']['mimetype'] == 'text/plain':
            if fileinfo['format']['charset'] == 'ISO-8859-15':
                return True
        return False

    def validate(self):
        """Return validation results"""

        self._techmd['format']['mimetype'] = \
            self.fileinfo['format']['mimetype']
        self._techmd['format']['charset'] = self.fileinfo['format']['charset']
        self.messages("")
        return self.result()
