"""General interface for building a file validator plugin. """
import abc
import subprocess
import os


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
    def check_validity(self):
        pass

    @abc.abstractmethod
    def check_version(self):
        pass

    @abc.abstractmethod
    def check_profile(self):
        pass

    def __init__(self):
        """Init method for BaseValidator class which sets environment
        variables.
        """

        self.exec_cmd = list()
        self.environment = os.environ.copy()
        self.filename = None
        self.fileversion = None
        self.mimetype = None
        self.profile = None

        self.statuscode = None
        self.stdout = ""
        self.stderr = ""

    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None
        """

        filename_in_list = [self.filename]
        self.exec_cmd += filename_in_list
        self.exec_validator()

        errors = []

        error = self.check_validity()
        if error is not None:
            errors.append(error)

        error = self.check_version(self.fileversion)
        if error is not None:
            errors.append(error)

        error = self.check_profile(self.profile)
        if error is not None:
            errors.append(error)

        if self.statuscode != 0:
            return (
                self.statuscode, self.stdout,
                "Validator returned error: %s\n%s" %
                (self.statuscode, self.stderr))

        if len(errors) == 0:
            return (0, self.stdout, '')
        else:
            return (1, self.stdout, '\n'.join(errors))

    def exec_validator(self):
        """Execute validator command given in self.self.exec_cmd.

        :returns: Tuple (statuscode, stdout, stderr)
        """

        proc = subprocess.Popen(self.exec_cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=False,
                                env=self.environment)

        (self.stdout, self.stderr) = proc.communicate()
        self.statuscode = proc.returncode

        return self.statuscode, self.stdout, self.stderr
