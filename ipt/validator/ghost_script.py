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
        self.version = fileinfo["format"]["version"]

    def validate(self):
        """
        Validate file
        """

        shell = Shell([
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage', self.filename])
        if shell.returncode != 0:
            self.errors(shell.stderr)
        else:
            self._check_version()
        self.messages(shell.stdout)

    def _check_version(self):
        """
        Check pdf version
        """
        shell = Shell(['file', self.filename])
        if 'PDF document, version %s' % self.version not in shell.stdout:
            found_version = shell.stdout.split(':')[1]
            self.errors("wrong file version. Expected PDF %s, found%s"
                        % (self.version, found_version))
            self.messages(shell.stdout)
