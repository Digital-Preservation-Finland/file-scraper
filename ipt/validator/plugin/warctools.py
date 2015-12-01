"""Module for validating files with warc-tools warc validator"""
import gzip
import subprocess
import tempfile
import os

from ipt.utils import run_command

class WarcError(Exception):
    """Warc validation error."""
    pass

class WarcTools(object):

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
        self.profile = None
        self.statuscode = None
        self.stdout = ""
        self.stderr = ""

    def check_version(self, version, filename):
        """ Check the file version of given file. In WARC format version string
            is stored at the first line of file so this methdos read the first
            line and check that it matches.
        """
        warc_fd = gzip.open(filename)
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with open(filename, 'r') as warc_fd:
                line = warc_fd.readline()

        if "WARC/%s" % version in line:
            return (117, "File version check error")
        return (0, "")



    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, 117 failure, anything else failure
            report -- generated report
            errors -- errors if encountered, else None
        """

        if self.mimetype == "application/x-internet-archive":
            (statuscode, stdout, stderr) = self.validate_arc()

        elif self.mimetype == "application/warc":
            exec_cmd1 = ['warcvalid', self.filename]
            (statuscode, stdout, stderr) = run_command(cmd=exec_cmd1)
        else:
            raise WarcError("Unknown mimetype: %s" % self.mimetype)

        return (statuscode, stdout, stderr)

    def validate_arc(self):
        """Valdiate arc by transforming it to warc first. WarcTools does not
        support direct validation of arc.

        """
        # create covnersion from arc tp warc
        stdout = []
        stderr = []
        statuscode_validation = 1

        (temp_file, warc_path) = tempfile.mkstemp()
        exec_cmd1 = ['arc2warc', self.filename]
        (statuscode_conversion,
            stdout_conversion,
            stderr_conversion) = run_command(
            cmd=exec_cmd1, stdout=temp_file)
        stdout.append(str(stdout_conversion))
        stderr.append(str(stderr_conversion))

        # Successful conversion from arc to warc, valdiation can
        # now be made.
        if statuscode_conversion == 0:
            exec_cmd2 = ['warcvalid', warc_path]
            (statuscode_validation,
                stdout_validation,
                stderr_validation) = run_command(exec_cmd2)

            stdout.append(stdout_validation)
            stderr.append(stderr_validation)

        # Check that version is correct
        (statuscode_version, messages) = self.check_version(
            self.fileversion, warc_path)
        if statuscode_version != 0:
            stderr.append(messages)

        return (statuscode_validation, ''.join(stdout), ''.join(stderr))
