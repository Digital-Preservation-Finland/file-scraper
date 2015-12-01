"""Module for validating files with warc-tools warc validator"""
import gzip
import subprocess
import tempfile
import os
from ipt.validator.basevalidator import BaseValidator


class WarcTools(BaseValidator):

    """ Initializes warctools validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


    .. seealso:: http://code.hanzoarchives.com/warc-tools
    """

    def __init__(self, mimetype, fileversion, filename):
        super(WarcTools, self).__init__()

        if mimetype != "application/warc" and mimetype != "application/x-internet-archive":
            raise Exception("Unknown mimetype: %s" % mimetype)
        self.filename = str(filename)
        self.fileversion = fileversion
        self.mimetype = mimetype


    def check_validity(self):
        return None

    def check_version(self, version, filename):
        """ Check the file version of given file. In WARC format version string
            is stored at the first line of file so this methdos read the first
            line and check that it matches.
        """
        warc_fd = gzip.open(self.filename)
        try:
            line = warc_fd.readline()
        except IOError:
            warc_fd.close()
            warc_fd = open(self.filename)
            line = warc_fd.readline()

        if line.find("WARC/%s" % version) != -1:
            return None
        return "File version check error"

    def check_profile(self, profile):
        """ WARC file format does not have profiles """
        return None

    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None
        """
        warc_path = None
        if self.mimetype == "application/x-internet-archive":
            (temp_file, warc_path) = tempfile.mkstemp()
            exec_cmd1 = [
                'arc2warc', self.filename, '>', warc_path]
            self.exec_validator(exec_cmd1, temp_file)

            exec_cmd2 = ['warcvalid', warc_path]
            self.exec_validator(exec_cmd2)

        if self.mimetype == "application/warc":
            warc_path = self.filename
            exec_cmd1 = ['warcvalid', warc_path]
            self.exec_validator(exec_cmd1)

        if self.statuscode != 0:
            return (
                self.statuscode, self.stdout,
                "Validator returned error: %s\n%s" %
                (self.statuscode, self.stderr))

        errors = []

        error = self.check_validity()
        if error is not None:
            errors.append(error)

        error = self.check_version(self.fileversion, warc_path)
        if error is not None:
            errors.append(error)

        error = self.check_profile(self.profile)
        if error is not None:
            errors.append(error)

        if len(errors) == 0:
            return (0, self.stdout, '')
        else:
            return (1, self.stdout, '\n'.join(errors))

    def exec_validator(self, exec_, tempfile=subprocess.PIPE):
        """Execute validator command given in self.self.exec_cmd.

        :returns: Tuple (statuscode, stdout, stderr)
        """

        proc = subprocess.Popen(exec_,
                                stdout=tempfile,
                                stderr=subprocess.PIPE,
                                shell=False,
                                env=self.environment)

        (self.stdout, self.stderr) = proc.communicate()
        self.statuscode = proc.returncode

        return self.statuscode, self.stdout, self.stderr
