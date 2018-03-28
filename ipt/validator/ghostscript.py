"""
This is a PDF 1.7 valdiator implemented with ghostscript.
"""

from ipt.validator.basevalidator import BaseValidator, Shell


class GhostScript(BaseValidator):
    """
    Ghostscript pdf validator
    """
    _supported_mimetypes = {
        'application/pdf': ['1.7', 'A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a',
                            'A-3b', 'A-3u']
    }

    def validate(self):
        """
        Validate file
        """

        shell = Shell([
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage', self.metadata_info["filename"]])
        # Ghostscript will result 0 if it can repair errors. However, stderr is not then empty.
        if shell.stderr:
            self.errors(shell.stderr)
        else:
            self._check_version()
        self.messages(shell.stdout)

    def _check_version(self):
        """
        Check pdf version
        """
        # VeraPDF will check PDF/A profile conformance
        if self.metadata_info["format"]["version"] in [
            'A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a', 'A-3b', 'A-3u']:
               return

        shell = Shell(['file', self.metadata_info["filename"]])
        if 'PDF document, version %s' % self.metadata_info["format"]["version"] not in shell.stdout:
            found_version = shell.stdout.split(':')[1]
            self.errors("wrong file version. Expected PDF %s, found%s"
                        % (self.metadata_info["format"]["version"], found_version))
            self.messages(shell.stdout)
