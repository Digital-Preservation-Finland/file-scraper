""" This is a module that integrates ffmpeg and ffprobe tools with
information-package-tools for file validation purposes. Validation is
achieved by doing a conversion. If conversion is succesful, file is
interpred as a valid file. Container type is also validated with ffprobe.
"""

import json

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import compare_lists_of_dicts

MPEG1_STRINGS = ["MPEG-1 video", "raw MPEG video"]
MPEG2_STRINGS = ["MPEG-2 transport stream format",
                 "MPEG-PS format",
                 "MPEG-2 PS (DVD VOB)"]
MP3_STRINGS = ["MPEG audio layer 2/3", "mp3"]
STREAM_STRINGS = {
    "mpegvideo": "MPEG 1",
    "mpeg1video": "MPEG 1",
    "mpeg2video": "MPEG 2",
    "h264": "AVC",
    "libmp3lame": "MP3",
    "libshine": "MP3",
    "mp3": "MP3",
    "mp3adu": "MP3",
    "mp3adufloat": "MP3",
    "mp3float": "MP3",
    "mp3on4": "MP3",
    "mp3on4float": "MP3",
    "aac": "AAC"
    }
MPEG4_STRINGS = ["M4A", "QuickTime/MPEG-4/Motion JPEG 2000 format", "isom"]

class FFMpeg(BaseValidator):
    """FFMpeg validator class."""

    _supported_mimetypes = {
        'video/mpeg': ['1', '2'],
        'video/mp4': ['']
    }

    def validate(self):
        """validate file."""
        self.check_version()
        self.check_streams("audiomd")
        self.check_streams("videomd")
        self.check_validity()

    def check_version(self):
        """parse version from ffprobes stderr, which is in following format:
            .
            .
            .
            [FORMAT]
            filename=example.aac
            nb_streams=1
            format_name=mov,mp4,m4a,3gp,3g2,mj2
            format_long_name=QuickTime/MPEG-4/Motion JPEG 2000 format
            start_time=0.000000
            duration=35.526531
            size=1304925
            bit_rate=293847
            TAG:major_brand=M4A
            TAG:minor_version=0
            TAG:compatible_brands=M4A mp42isom
            TAG:creation_time=2014-11-20 12:31:15
            TAG:title=forAAC
            TAG:gapless_playback=0
            TAG:encoder=iTunes 12.0.1.26
            [/FORMAT]
        """
        shell = Shell(
            ['ffprobe', '-show_format', '-v',
             'debug', self.fileinfo['filename']])
        detected_format = None
        if "raw MPEG video" in shell.stderr:
            detected_format = {"version": "1", "mimetype": "video/mpeg"}

        if "MPEG-2 transport stream format" in shell.stderr or \
                "MPEG-PS" in shell.stderr:
            detected_format = {"version": "2", "mimetype": "video/mpeg"}

        if "MPEG-4" in shell.stderr and \
                "TAG:major_brand=isom" in shell.stderr:
            detected_format = {"version": "", "mimetype": "video/mp4"}

        if "MPEG audio layer 2/3" in shell.stderr and \
                "format_name=mp3" in shell.stderr:
            detected_format = {"version": "", "mimetype": "audio/mpeg"}

        if "TAG:major_brand=M4A " in shell.stderr:
            detected_format = {"version": "", "mimetype": "audio/mp4"}

        if not detected_format:
            self.errors(
                "No matching version information could be found,"
                "file might not be MPEG1/2 or MP4. "
                "FFprobe output: %s" % shell.stderr)
            return

        if detected_format != self.fileinfo["format"] and detected_format:
            self.errors(
                "Wrong format version, got '%s' version '%s', "
                "expected '%s' version '%s'." % (
                    detected_format["mimetype"],
                    detected_format["version"],
                    self.fileinfo["format"]["mimetype"],
                    self.fileinfo["format"]["version"]))

    def check_validity(self):
        """Check file validity. The validation logic is check that ffmpeg returncode
        is 0 and nothing is found in stderr. FFmpeg lists faulty parts of mpeg
        to stderr."""
        shell = Shell([
            'ffmpeg', '-v', 'error', '-i', self.fileinfo['filename'],
            '-f', 'null', '-'])
        if shell.returncode != 0 or shell.stderr != "":
            self.errors(
                "File %s not valid: %s" % (
                    self.fileinfo['filename'], shell.stderr))
            return
        self.messages("%s is valid." % self.fileinfo['filename'])

    def check_streams(self, stream_type):
        """Check that streams inside container are what they are described in
        audioMD and videoMD.
        :stream_type: "audiomd" or "videomd"
        """
        if stream_type not in self.fileinfo:
            return
        streams = {stream_type: []}
        shell = Shell(
            ['ffprobe', '-show_streams', '-show_format', '-print_format',
             'json', self.fileinfo['filename']])

        stream_raw_data = json.loads(shell.stdout)

        for stream in stream_raw_data["streams"]:
            if stream["codec_type"] == stream_type:
                streams[stream_type].append({"codec": stream["codec_name"]})
        (missing, extra) = compare_lists_of_dicts(
            self.fileinfo[stream_type], streams[stream_type])
        if missing or extra:
            self.errors("Streams in container %s are not what is "
                        "described in metadata. Found %s, expected %s" % (
                            self.fileinfo["filename"],
                            streams[stream_type],
                            self.fileinfo[stream_type]))
        self.messages("Streams %s are according to metadata description" %
                      self.fileinfo[stream_type])
