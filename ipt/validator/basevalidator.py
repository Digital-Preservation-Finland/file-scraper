"""General interface for building a file validator plugin. """
import abc


class ValidatorError(Exception):

    """Validator error exception which should be thrown when validator is not
    able to continue with given parametres. For example unknown mimetype for
    validator should throw this exception.
    """

    pass


class BaseValidator(object):

    """This class introduces general interface for file validor plugin which
    every validator has to satisfy. This class is meant to be inherited and to
    use this class at least exec_cmd and filename variables has to be set.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self):
        pass

    def __init__(self, fileinfo):
        """Init """

        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']
        self._supported_mimetypes = []
        self._messages = []
        self._errors = []
        self._is_valid = True

    @classmethod
    def is_supported_mimetype(cls, fileinfo):
        mimetype = fileinfo['format']['mimetype']
        version = fileinfo['format']['version']

        if mimetype in cls._supported_mimetypes:
            if version in cls._supported_mimetypes[mimetype]:
                return True
        return False

    def messages(self):
        for message in self._messages:
            yield message

    def errors(self):
        for error in self._errors:
            yield error

    def is_valid(self, validity=None):
        """Return validator validity state (True/False)"""
        if validity is not None:
            self._is_valid = validity
        return self._is_valid

    def not_valid(self):
        """Set validity to invalid"""
        self._is_valid = False
