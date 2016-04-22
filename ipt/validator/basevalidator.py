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

    _supported_mimetypes = []
    _messages = None
    _errors = None
    _is_valid = None

    @abc.abstractmethod
    def validate(self):
        pass

    def __init__(self, fileinfo):
        """Init """

        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']

        self._is_valid = None

    @classmethod
    def is_supported_mimetype(cls, fileinfo):
        mimetype = fileinfo['format']['mimetype']
        version = fileinfo['format']['version']

        if mimetype in cls._supported_mimetypes:
            if version in cls._supported_mimetypes[mimetype]:
                return True
        return False

    def messages(self):
        if self._is_valid is None:
            self.validate()

        for message in self._messages:
            yield message

    def errors(self):
        if self._is_valid is None:
            self.validate()

        for error in self._errors:
            yield error

    def is_valid(self):
        if self._is_valid is None:
            self.validate()

        return self._is_valid

