"""Module for validating files with warc-tools warc validator"""
import gzip
import tempfile
import contextlib

from ipt.utils import run_command, UnknownException


class WarcError(Exception):
    """Warc validation error."""
    pass


class WarcTools(object):

    """ Implements filevalidation or warc/arc files. use by calling
    validate.
        validate() for file validation.


    .. seealso:: https://github.com/internetarchive/warctools
    """

    def __init__(self, fileinfo):
        """init."""

        #FIXME: Inherit Basevalidator and remove these
        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']

        if self.mimetype != "application/warc" and \
                self.mimetype != "application/x-internet-archive":
            raise WarcError("Unknown mimetype: %s" % self.mimetype)

    def _check_warc_version(self):
        """ Check the file version of given file. In WARC format version string
            is stored at the first line of file so this methdos read the first
            line and check that it matches.
        """
        warc_fd = gzip.open(self.filename)
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with open(self.filename, 'r') as warc_fd:
                line = warc_fd.readline()
        print "CHECKING FOR", self.fileversion, "IN", line
        if "WARC/%s" % self.fileversion not in line:
            print "VERSION CHECK FAILED"
            self._append_results(117, "", "File version check error, version %s "
                         "not found from warc: %s" % (self.fileversion, line))
        self._append_results(0, "", "")

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
            (self.statuscode,
                self.stdout,
                self.stderr) = self._validate_arc()

        elif self.mimetype == "application/warc":
            (self.statuscode,
                self.stdout,
                self.stderr) = self._validate_warc()

        return (self.statuscode, self.stdout, self.stderr)


    def _validate_warc(self):
        """Validate warc with WarcTools.
        :returns: (statuscode, stdout, stderr)"""
        stdout = []
        stderr = []
        statuscode_version = 1

        # Validate warc
        exec_cmd1 = ['warcvalid', self.filename]
        (statuscode,
            stdout_validation,
            stderr_validation) = run_command(cmd=exec_cmd1)
        print (statuscode,
            stdout_validation,
            stderr_validation)
        stdout.append(stdout_validation)
        stderr.append(stderr_validation)

        (exitcode, stdout, stderr) = run_command(['warcvalid', self.filename])
        if exitcode == 0:
            self._check_warc_version()

    def _validate_arc(self):
        """Valdiate arc by transforming it to warc first. WarcTools does not
        support direct validation of arc.
        :returns: (statuscode, stdout, stderr)

        """
        # create covnersion from arc tp warc
        stdout = []
        stderr = []
        statuscode_validation = 1
        statuscode_conversion = 1

        temp_file = tempfile.NamedTemporaryFile(prefix="temp-warc.")
        warc_path = temp_file.name
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

        return (statuscode_validation, ''.join(stdout), ''.join(stderr))

    def _check_for_errors(self, exitcode, stdout, stderr):
        """Check if outcome was failure or success."""
        if exitcode == 0:
            self._append_results(0, stdout, stderr)
            return
        for message in self.failures:
            if message in stderr:
                self._append_results(117, "", stderr)
        for error in self.system_errors:
            if error in stderr:
                self._append_results(1, "", stderr)

    def _append_results(self, exitcode, stdout, stderr):
        """append intermediate results."""
        self.exitcode.append(exitcode)
        self.stdout.append(stdout)
        self.stderr.append(stderr)
