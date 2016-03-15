""" This is a module that integrates ffmpeg-tool with information-package-tools
for file validation purposes. Validation is achieved by doing a conversion.
If conversion is succesful, file is interpred as a valid file."""
from ipt.utils import run_command


SYSTEM_ERRORS = [
    'Invalid argument',
    'Missing argument for option',
    'No such file or directory']

class FFMpeg(object):
    """FFMpeg plugin class."""

    def __init__(self, fileinfo):
        """init"""
        self.filename = fileinfo['filename']
        self.fileversion = fileinfo['format']['version']
        self.mimetype = fileinfo['format']['mimetype']
        self.validation_cmd = [
            'ffmpeg', '-v', 'error', '-i', self.filename, '-f', 'null', '-']
        self.version_cmd = [
            'ffprobe', '-show_format', self.filename, '-print_format', 'json']
        self.stdout = []
        self.stderr = []
        self.exitcode = []

    def validate(self):
        """validate file."""
        self.check_version()
        self.check_validity()
        if set(self.exitcode).issubset(set([0])):
            validity = 0
        elif not set(self.exitcode).issubset([0, 117]):
            validity = 1
        else:
            validity = 117
        return (validity, '\n'.join(self.stdout), '\n'.join(self.stderr))

    def check_validity(self):
        """Check file validity."""
        (exitcode, stdout, stderr) = run_command(self.validation_cmd)
        if stderr:
            exitcode = 117
        for error in SYSTEM_ERRORS:
            if error in stderr:
                print "SYSTEM_ERRORS"
                exitcode = 1
                break
        self.append_results(exitcode, stdout, stderr)

    def append_results(self, exitcode, stdout, stderr):
        """append intermediate results."""
        self.exitcode.append(exitcode)
        self.stdout.append(stdout)
        self.stderr.append(stderr)
