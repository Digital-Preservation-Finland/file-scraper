"""General interface for building a file validator plugin. """
import abc
import subprocess

from ipt.utils import run_command


class ValidatorError(Exception):
    """Unrecoverable error in validator"""
    pass


class Shell(object):

    """Docstring for ShellTarget. """

    def __init__(self, command, output_file=subprocess.PIPE,
                 ld_library_path=None):
        """Initialize instance.

        :command: Command to execute as list
        """
        self.command = command

        self._stdout = None
        self._stderr = None
        self._returncode = None
        self.ld_library_path = ld_library_path
        self.output_file = output_file

    @property
    def returncode(self):
        """Returncode from the command

        :returns: Returncode

        """
        return self.run()["returncode"]

    @property
    def stderr(self):
        """Standard error output from the command

        :returns: Stdout as string

        """
        return self.run()["stderr"]

    @property
    def stdout(self):
        """Command standard error output.

        :returns: Stderr as string

        """
        return self.run()["stdout"]

    def run(self):
        """Run the command and store results to class attributes for caching.

        :returns: Returncode, stdout, stderr as dictionary

        """
        if self._returncode is None:
            (self._returncode, self._stdout,
             self._stderr) = run_command(
                 cmd=self.command, stdout=self.output_file,
                 ld_library_path=self.ld_library_path)

        return {
            'returncode': self._returncode,
            'stderr': self._stderr,
            'stdout': self._stdout
            }


class BaseValidator(object):

    """This class introduces general interface for file validor plugin which
    every validator has to satisfy. This class is meant to be inherited and to
    use this class at least exec_cmd and filename variables has to be set.
    """

    __metaclass__ = abc.ABCMeta
    _supported_mimetypes = None

    _techmd = None

    def __init__(self, fileinfo):
        """Setup the base validator object"""

        self.fileinfo = fileinfo
        self._messages = []
        self._errors = []
        self._techmd = {'filename': fileinfo['filename'],
                        'format': {}
                       }

    @classmethod
    def is_supported(cls, fileinfo):
        """Return True if this validator class supports digital object with
        given fileinfo record.

        Default implementation checks the mimetype and version. Other
        implementations may override this for other selection criteria"""

        mimetype = fileinfo['format']['mimetype']
        version = fileinfo['format']['version']

        return mimetype in cls._supported_mimetypes and \
            version in cls._supported_mimetypes[mimetype]

    def messages(self, message=None):
        """Return validation diagnostic messages"""
        if message is not None:
            self._messages.append(message)
        return concat(self._messages)

    def errors(self, error=None):
        """Return validation error messages"""
        if error is not None and error != "":
            self._errors.append(error)
        return concat(self._errors, 'ERROR: ')

    @property
    def is_valid(self):
        """Validation result is valid when there are more than one messages and
        no error messages.
        """
        return len(self._messages) > 0 and len(self._errors) == 0

    def result(self):
        """Return the validation result"""

        if len(self._messages) == 0:
            self.validate()

        return {
            'is_valid': self.is_valid,
            'messages': self.messages(),
            'errors': self.errors(),
            'result': self._techmd
        }

    @abc.abstractmethod
    def validate(self):
        """All validator classes must implement the validate() method"""
        pass


def concat(lines, prefix=""):
    """Join given list of strings to single string separated with newlines.

    :lines: List of string to join
    :prefix: Prefix to prepend each line with
    :returns: Joined lines as string

    """
    return "\n".join(["%s%s" % (prefix, line) for line in lines])
