"""
This is a PDF 1.7 valdiator implemented with ghostscript.
"""

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import run_command, UnknownException


class GhostScript(BaseValidator):
    """
    Ghostscript pdf validator
    """
    _supported_mimetypes = {
        'application/pdf': ['1.7']
    }

    def __init__(self, fileinfo):
        """
        init
        :fileinfo: a dictionary with format

            fileinfo["filename"]
            fileinfo["format"]["version"]
            fileinfo["format"]["mimetype"]
        """
        super(GhostScript, self).__init__(fileinfo)
        self.filename = fileinfo["filename"]
        self.cmd_exec = [
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage', '%s' % self.filename]
        self.file_cmd_exec = 'file'

    def validate(self):
        """
        Validate file
        :returns: tuple(validity, messages, errors)
        """

        shell = Shell(self.cmd_exec)
        if 'error' in shell.stderr or 'Error' in shell.stdout or \
            shell.returncode != 0 or 'Processing page' not in shell.stdout:
            self.errors(shell.stderr)
            self.messages(shell.stdout)

        if 'Error: /undefined in' not in shell.stdout and shell.returncode != 0:
            raise UnknownException(
                "stderr:%s stdout:%s" % (shell.stderr, shell.stdout))

        self._check_version()
        self.messages('OK')


    def _check_version(self):
        """
        Check pdf version
        """
        shell = Shell([self.file_cmd_exec, self.filename])
        if shell.returncode != 0:
            self.errors("ERROR:%s" % stderr)
            self.messages(stdout)
            raise UnknownException(
                "stderr:%s stdout:%s" % (shell.errors(), shell.messages()))

        if 'PDF document, version 1.7' not in shell.stdout:
            version = shell.stdout.split(':')[1]
            self.errors(
                "ERROR: wrong file version. Expected PDF 1.7, found%s"
                % version)
            self.messages(shell.stdout)
