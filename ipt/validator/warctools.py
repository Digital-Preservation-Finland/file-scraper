"""
Module for validating arc and warc files with warc-tools warc validator.
"""
import gzip
import tempfile

from ipt.validator.basevalidator import BaseValidator, ValidatorError, Shell


class WarcTools(BaseValidator):

    """ Implements filevalidation or warc/arc files. use by calling
    validate() for file validation.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_mimetypes = {
        'application/warc': ['0.17', '0.18', '1.0'],
        'application/x-internet-archive': ['1.0', '1.1']
    }

    def __init__(self, fileinfo):
        """init.
        :fileinfo: a dictionary with format

            fileinfo["filename"]
            fileinfo["algorithm"]
            fileinfo["digest"]
            fileinfo["format"]["version"]
            fileinfo["format"]["mimetype"]
            fileinfo["format"]["format_registry_key"]
        """

        super(WarcTools, self).__init__(fileinfo)
        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']
        self.failures = [
            'zero length field name in format',
            'Error -3 while decompressing: invalid distance code',
            'Not a gzipped file',
            'CRC check failed',
            'incorrect newline in header']

    def validate(self):
        """
        Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.
        """

        if self.mimetype == "application/x-internet-archive":
            self._validate_arc()
            self._check_warc_version()

        elif self.mimetype == "application/warc":
            self._validate_arc()

    def _validate_warc(self, path=None):
        """
        Validate warc with WarcTools.
        """
        if path is None:
            path = self.filename
        shell = Shell(['warcvalid', path])
        self._check_shell_output(
            "WARC validation", shell.returncode, shell.stderr)

    def _validate_arc(self):
        """
        Valdiate arc by transforming it to warc first. WarcTools does not
        support direct validation of arc.
        """

        with tempfile.NamedTemporaryFile(prefix="temp-warc.") as outfile:
            shell = Shell(
                command=['arc2warc', self.filename], output_file=outfile.name)
            self._check_shell_output(
                'ARC->WARC conversion', shell.returncode, shell.stderr)
            self._validate_warc(outfile.name)

    def _check_shell_output(self, reason, returncode, stderr):
        """
        Check if outcome was failure or success.
        :reason: Description of the shell command
        :messages: messages
        :errors: errors
        """

        if returncode == 0:
            self.messages("OK: %s successful!" % reason)
        else:
            self.errors("ERROR: %s failed!" % reason)
            self.errors(stderr)
            for failure in self.failures:
                if failure in stderr:
                    return
            raise ValidatorError(self.errors())

    def _check_warc_version(self):
        """
        Check the file version of given file. In WARC format version string
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

        if "WARC/%s" % self.fileversion in line:
            self.messages("OK: WARC version good")
        else:
            self.errors(
                "File version check error, version %s "
                "not found from warc: %s" % (self.fileversion, line))
