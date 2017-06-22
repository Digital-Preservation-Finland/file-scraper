import gzip
import tempfile

from ipt.validator.basevalidator import BaseValidator, Shell


class WarctoolsWARC(BaseValidator):

    """Implements WARC file format validator using Internet Archives warctools
    validator.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_mimetypes = {
        'application/warc': ['0.17', '0.18', '1.0']
    }

    def validate(self):

        shell = Shell(['warcvalid', self.fileinfo['filename']])

        if shell.returncode != 0:
            self.errors("Validation failed: returncode %s" % shell.returncode)
            self.errors(shell.stderr)

        self.messages(shell.stdout)

        self._check_warc_version()

    def _check_warc_version(self):
        warc_fd = gzip.open(self.fileinfo['filename'])
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with open(self.fileinfo['filename'], 'r') as warc_fd:
                line = warc_fd.readline()
        except Exception as exception:
            # Compressed but corrupted gzip file
            self.errors(str(exception))
            return

        if "WARC/%s" % self.fileinfo['format']['version'] in line:
            self.messages("OK: WARC version good")
        else:
            self.errors(
                "File version check error, version %s "
                "not found from warc file header." % (self.fileinfo['format']['version']))


class WarctoolsARC(BaseValidator):

    _supported_mimetypes = {
        'application/x-internet-archive': ['1.0', '1.1']
    }

    def validate(self):
        """Validate ARC file by converting to WARC using Warctools' arc2warc
        converter."""

        with tempfile.NamedTemporaryFile(prefix="ipt-warctools.") as warcfile:
            shell = Shell(command=['arc2warc', self.fileinfo['filename']],
                          output_file=warcfile)

            if shell.returncode != 0:
                self.errors("Validation failed: returncode %s" %
                            shell.returncode)
                self.errors(shell.stderr)

            self.messages(shell.stdout)
