import gzip
import tempfile
import unicodedata
import string

from ipt.validator.basevalidator import BaseValidator, Shell


def sanitaze_string(dirty_string):
    """Strip non-printable control characters from unicode string"""
    sanitazed_string = "".join(
        char for char in dirty_string if unicodedata.category(char)[0] != "C"
        or char in string.printable)
    return sanitazed_string

class WarctoolsWARC(BaseValidator):

    """Implements WARC file format validator using Internet Archives warctools
    validator.

    .. seealso:: https://github.com/internetarchive/warctools
    """

    _supported_mimetypes = {
        'application/warc': ['0.17', '0.18', '1.0']
    }

    def validate(self):

        shell = Shell(['warcvalid', self.metadata_info['filename']])

        if shell.returncode != 0:
            self.errors("Validation failed: returncode %s" % shell.returncode)
            # Filter some trash printed by warcvalid.
            filtered_errors = \
                "\n".join([line for line in shell.stderr.split('\n') \
                if not 'ignored line' in line])
            self.errors(filtered_errors)

        self.messages(shell.stdout)

        self._check_warc_version()

    def _check_warc_version(self):
        warc_fd = gzip.open(self.metadata_info['filename'])
        try:
            # First assume archive is compressed
            line = warc_fd.readline()
        except IOError:
            # Not compressed archive
            warc_fd.close()
            with open(self.metadata_info['filename'], 'r') as warc_fd:
                line = warc_fd.readline()
        except Exception as exception:
            # Compressed but corrupted gzip file
            self.errors(str(exception))
            return

        if "WARC/%s" % self.metadata_info['format']['version'] in line:
            self.messages("OK: WARC version good")
        else:
            self.errors(
                "File version check error, version %s not found from header "
                "of warc file: %s"
                % (self.metadata_info['format']['version'],
                   self.metadata_info['filename'])
                )


class WarctoolsARC(BaseValidator):

    _supported_mimetypes = {
        'application/x-internet-archive': ['1.0', '1.1']
    }

    def validate(self):
        """Validate ARC file by converting to WARC using Warctools' arc2warc
        converter."""

        with tempfile.NamedTemporaryFile(prefix="ipt-warctools.") as warcfile:
            shell = Shell(command=['arc2warc', self.metadata_info['filename']],
                          output_file=warcfile)

            if shell.returncode != 0:
                self.errors("Validation failed: returncode %s" %
                            shell.returncode)
                # replace non-utf8 characters
                utf8string = shell.stderr.decode('utf8', errors='replace')
                # remove non-printable characters
                sanitazed_string = sanitaze_string(utf8string)
                # encode string to utf8 before adding to errors
                self.errors(sanitazed_string.encode('utf-8'))

            self.messages(shell.stdout)
