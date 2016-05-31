"""Module for validating files with warc-tools warc validator"""
import gzip
import tempfile

from ipt.utils import run_command
from ipt.validator.basevalidator import BaseValidator, ValidatorError, Shell


class WarcTools(BaseValidator):

    """ Implements filevalidation or warc/arc files. use by calling
    validate.
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
            fileinfo["object_id"]["type"]
            fileinfo["object_id"]["value"]
        """

        super(WarcTools, self).__init__(fileinfo)
        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']
        self.failures = ['zero length field name in format',
            'Error -3 while decompressing: invalid distance code',
            'Not a gzipped file',
            'CRC check failed',
            'incorrect newline in header']

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

        if "WARC/%s" % self.fileversion not in line:
            self.errors("File version check error, version %s "
                         "not found from warc: %s" % (self.fileversion, line))
        else:
            self.messages("OK")

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
            self._validate_arc()

        elif self.mimetype == "application/warc":
            self._validate_warc()
        messages = "\n".join(message for message in self.messages())
        errors = "\n".join(error for error in self.errors())
        return (self.is_valid(), messages, errors)

    def _validate_warc(self):
        """
        Validate warc with WarcTools.
        :returns: (statuscode, messages, errors)"""
        shell = Shell(['warcvalid', self.filename])
        self._check_for_errors(shell.returncode, shell.stdout, shell.stderr)
        if shell.returncode == 0:
            self._check_warc_version()

    def _validate_arc(self):
        """
        Valdiate arc by transforming it to warc first. WarcTools does not
        support direct validation of arc.
        :returns: (statuscode, messages, errors)
        """
        # create covnersion from arc to warc
        temp_file = tempfile.NamedTemporaryFile(prefix="temp-warc.")
        warc_path = temp_file.name
        shell = Shell(command=['arc2warc', self.filename], output_file=temp_file)
        self._check_for_errors(shell.returncode, shell.stdout, shell.stderr)

        # Successful conversion from arc to warc, validation can
        # now be made.
        if shell.returncode == 0:
            shell = Shell(['warcvalid', warc_path])
            self._check_for_errors(shell.returncode, shell.stderr, shell.stdout)
            if shell.returncode == 0:
                self.messages("OK")

    def _check_for_errors(self, validity, messages, errors):
        """Check if outcome was failure or success.
        :validity: validity
        :messages: messages
        :errors: errors
        """
        if validity != 0:
            self.errors(errors)

            for failure in self.failures:
                if failure in errors:
                    return
            raise ValidatorError(self.errors())
