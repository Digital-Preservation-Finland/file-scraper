from ipt.validator import BaseValidator


class DummyTextValidator(BaseValidator):

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
        self._techmd['format']['mimetype'] = self.fileinfo['format']['mimetype']
        self._techmd['format']['charset'] = self.fileinfo['format']['charset']
        self.messages("")
        return self.result()
