"""
This is a PDF 1.7 valdiator implemented with ghostscript.
"""

from ipt.validator.basevalidator import BaseValidator, Shell


class GhostScript(BaseValidator):
    """
    Ghostscript pdf validator
    """
    _supported_mimetypes = {
        'application/pdf': ['1.7']
    }

    def validate(self):
        """
        Validate file
        """

        shell = Shell([
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage', self.fileinfo["filename"]])
        if shell.returncode != 0:
            self.errors(shell.stderr)
        else:
            self._check_version()
        self.messages(shell.stdout)

    def _check_version(self):
        """
        Check pdf version
        """
        shell = Shell(['file', self.fileinfo["filename"]])
        if 'PDF document, version %s' % self.fileinfo["format"]["version"] not in shell.stdout:
            found_version = shell.stdout.split(':')[1]
            self.errors("wrong file version. Expected PDF %s, found%s"
                        % (self.fileinfo["format"]["version"], found_version))
            self.messages(shell.stdout)
