"""Validator for plain text files"""

from ipt.validator.basevalidator import BaseValidator


class DummyTextValidator(BaseValidator):

    """Validator for plain text files"""

    @classmethod
    def is_supported(cls, metadata_info):
        """
        Check suported mimetypes.
        :metadata_info: metadata_info
        """
        if metadata_info['format']['mimetype'] == 'text/plain':
            if metadata_info['format']['charset'] == 'ISO-8859-15':
                return True
        return False

    def validate(self):
        """Return validation results"""

        self.validator_info['format']['mimetype'] = \
            self.metadata_info['format']['mimetype']
        self.validator_info['format']['charset'] = self.metadata_info['format']['charset']
        self.messages("")
        return self.result()
