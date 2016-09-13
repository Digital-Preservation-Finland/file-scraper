""" This is a module that integrates ffmpeg and ffprobe tools with
information-package-tools for file validation purposes. Validation is
achieved by doing a conversion. If conversion is succesful, file is
interpred as a valid file. Container type is also validated with ffprobe.
"""

import json

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import compare_lists_of_dicts

MPEG1 = {"version": "1", "mimetype": "video/mpeg"}
MPEG2 = {"version": "2", "mimetype": "video/mpeg"}
MP3 = {"version": "", "mimetype": "audio/mpeg"}
AUDIOMP4 = {"version": "", "mimetype": "audio/mp4"}
VIDEOMP4 = {"version": "", "mimetype": "video/mp4"}

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
        self.check_container_mimetype()
        self.check_streams("audio")
        self.check_streams("video")
        self.check_validity()

    def check_container_mimetype(self):
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
             'debug', '-print_format', 'json', self.fileinfo['filename']])
        data = json.loads(str(shell.stdout))
        format_data = data.get("format")
        if format_data is None:
            self.errors(
                "No format data could be read. FFprobe output: %s " % shell.stdout)
            return
        detected_format = None

        # Detect MPEG1, MPEG2 and MP3
        if format_data.get("format_long_name") in MPEG1_STRINGS:
            detected_format = MPEG1

        if format_data.get("format_long_name") in MPEG2_STRINGS:
            detected_format = MPEG2

        if format_data.get("format_long_name") in MP3_STRINGS and \
                format_data.get("format_name") in MP3_STRINGS:
            detected_format = MP3

        # Detect MPEG4
        tags = format_data.get("tags")
        if tags:
            if tags.get("major_brand") in MPEG4_STRINGS:
                detected_format = AUDIOMP4
            if format_data["format_long_name"] in MPEG4_STRINGS and \
                    tags.get("major_brand") in MPEG4_STRINGS:
                detected_format = VIDEOMP4

        if not detected_format:
            self.errors(
                "No matching version information could be found,"
                "file might not be MPEG1/2 or MP4. "
                "FFprobe output: %s" % shell.stdout)
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

        found_streams = {stream_type: []}
        shell = Shell(
            ['ffprobe', '-show_streams', '-show_format', '-print_format',
             'json', self.fileinfo['filename']])

        stream_raw_data = json.loads(shell.stdout)

        for stream in stream_raw_data.get("streams", []):
            if stream["codec_type"] == stream_type:
                if stream["codec_name"] in STREAM_STRINGS:
                    new_stream = STREAM_STRINGS[stream["codec_name"]]
                else:
                    new_stream = stream["codec_name"]
                found_streams[stream_type].append({"codec": new_stream})
        (missing, extra) = compare_lists_of_dicts(
            self.fileinfo.get(stream_type), found_streams[stream_type])
        if missing or extra:
            self.errors("Streams in container %s are not what is "
                        "described in metadata. Found %s, expected %s" % (
                            self.fileinfo["filename"],
                            found_streams[stream_type],
                            self.fileinfo.get(stream_type)))
        if stream_type not in self.fileinfo:
            return
        self.messages("Streams %s are according to metadata description" %
                      self.fileinfo[stream_type])
