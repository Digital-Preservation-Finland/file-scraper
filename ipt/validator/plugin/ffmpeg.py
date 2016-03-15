""" This is a module that integrates ffmpeg-tool with information-package-tools
for file validation purposes. Validation is achieved by doing a conversion.
If conversion is succesful, file is interpred as a valid file."""
from ipt.utils import run_command
from ipt.validator.basevalidator import BaseValidator

class FFMpeg(object):
    """FFMpeg plugin class."""

    def __init__(self, fileinfo):
        """init"""
        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']
        self.stdout = ""
        self.stderr = ""
        self.exitcode = 1
        self.validation_cmd = [
            'ffmpeg', '-v', 'error', '-i', self.filename, '-f', 'null', '-']
        self.version_cmd = [
            'ffprobe', '-show_format', self.filename, '-print_format', 'json']

    def validate(self):
        """validate file."""
        print self.exec_cmd
        (self.exitcode, self.stdout, self.stderr) = run_command(self.exec_cmd)

        if self.stderr:
            self.exitcode = 117
        else:
            self.exitcode = 0
        return (self.exitcode, self.stdout, self.stderr)
