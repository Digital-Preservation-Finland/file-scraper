""" This is a module that integrates ffmpeg-tool with information-package-tools
for file validation purposes. Validation is achieved by doing a conversion.
If conversion is succesful, file is interpred as a valid file."""
from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import run_command

FORMATS = [
    {"format_string": "mpeg1video",
     "format": {
         "version": "1", "mimetype": "video/mpeg"
         }
    },
    {"format_string": "mpeg2video",
     "format": {
         "version": "2", "mimetype": "video/mpeg"
         }
    },
    {"format_string": "h264",
     "format": {
         "version": "", "mimetype": "video/mp4"
         }
    }

]


class FFMpeg(BaseValidator):
    """FFMpeg plugin class."""

    _supported_mimetypes = {
        'video/mpeg': ['1', '2'],
        'video/mp4': ['']
    }

    def validate(self):
        """validate file."""
        self.check_version()
        self.check_validity()

    def check_version(self):
        """parse version from stderr, which is in such format:

            Stream #0:0[0x1e0]: Video: mpeg2video (Main), yuv420p, ...
        """
        shell = Shell(['ffprobe', self.fileinfo['filename']])
        if "Video: " not in shell.stderr:
            self.errors(
                "No version information could be found,"
                "file might not be video: %s" % shell.stderr)
            return

        detected_format = self.resolve_format(shell.stderr)
        if detected_format != self.fileinfo["format"] and detected_format:
            self.errors(
                "Wrong format version, got %s version %s, "
                "expected %s version %s." % (
                    detected_format["mimetype"],
                    detected_format["version"],
                    self.fileinfo["format"]["mimetype"],
                    self.fileinfo["format"]["version"]))

    def resolve_format(self, info):
        """Resolve format name and version."""
        line = info.split("Video: ")[1].split(' ')[0].replace(",", "")
        for format_ in FORMATS:
            if format_["format_string"] == line:
                return format_["format"]
        self.errors("Unknown mimetype or version")

    def check_validity(self):
        """Check file validity."""
        shell = Shell([
            'ffmpeg', '-v', 'error', '-i', self.fileinfo['filename'],
            '-f', 'null', '-'])
        if shell.returncode != 0 or shell.stderr != "":
            self.errors(
                "File %s not valid: %s" % (
                    self.fileinfo['filename'], shell.stderr))
            return
        self.messages("OK")
