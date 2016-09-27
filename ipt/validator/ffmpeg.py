""" This is a module that integrates ffmpeg and ffprobe tools with
information-package-tools for file validation purposes. Validation is
achieved by doing a conversion. If conversion is succesful, file is
interpred as a valid file. Container type is also validated with ffprobe.
"""

import json

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import compare_lists_of_dicts

MPEG1 = {"version": "1", "mimetype": "video/MP1S"}
MPEG2_TS = {"version": "2", "mimetype": "video/MP2T"}
MPEG2_PS = {"version": "2", "mimetype": "video/MP2P"}
MP3 = {"version": "", "mimetype": "audio/mpeg"}
MP4 = {"version": "", "mimetype": "video/mp4"}
RAW_AAC = {"version": "", "mimetype": "audio/mp4"}
RAW_MPEG = {"version": "1", "mimetype": "video/mpeg"}

MPEG1_STRINGS = ["MPEG-1 video"]
RAW_MPEG_STRINGS = ["raw MPEG video"]
MPEG2_TS_STRINGS = ["MPEG-2 transport stream format"]
MPEG2_PS_STRINGS = ["MPEG-PS format", "MPEG-2 PS (DVD VOB)"]
MP3_STRINGS = [
    "MPEG audio layer 2/3",
    "MP3 (MPEG audio layer 3)",
    "ADU (Application Data Unit) MP3 (MPEG audio layer 3)",
    "MP3onMP4",
    "libmp3lame MP3 (MPEG audio layer 3)",
    "libshine MP3 (MPEG audio layer 3)"]
MPEG4_STRINGS = ["M4A", "QuickTime/MPEG-4/Motion JPEG 2000 format"]
RAW_AAC_STRINGS = ["raw ADTS AAC"]

CONTAINER_MIMETYPES = [
    {"data": MPEG1, "strings": MPEG1_STRINGS},
    {"data": MPEG2_TS, "strings": MPEG2_TS_STRINGS},
    {"data": MPEG2_PS, "strings": MPEG2_PS_STRINGS},
    {"data": MP3, "strings": MP3_STRINGS},
    {"data": MP4, "strings": MPEG4_STRINGS},
    {"data": RAW_AAC, "strings": RAW_AAC_STRINGS},
    {"data": RAW_MPEG, "strings": RAW_MPEG_STRINGS}
]

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


class FFMpeg(BaseValidator):
    """FFMpeg validator class."""

    _supported_mimetypes = {
        'video/mpeg': ['1', '2'],
        'video/mp4': [''],
        'audio/mpeg': ['1', '2'],
        'audio/mp4': [''],
        'video/MP2T': ['2'],
        'video/MP2P': ['2']
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
                "No format data could be read. "
                "FFprobe output: %s " % shell.stdout)
            return

        detected_format = None
        for mimetype in CONTAINER_MIMETYPES:
            if format_data.get("format_long_name") in mimetype["strings"]:
                detected_format = mimetype["data"]

        if not detected_format:
            self.errors(
                "No matching version information could be found,"
                "file might not be MPEG1/2 or MP4. "
                "FFprobe output: %s" % shell.stdout)
            return

        if detected_format != self.fileinfo["format"]:
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

        stream_data = json.loads(shell.stdout)

        for stream in stream_data.get("streams", []):
            new_stream = STREAM_PARSERS[stream_type](stream, stream_type)
            if new_stream:
                found_streams[stream_type].append(new_stream)

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


def parse_video_streams(stream, stream_type):
    """
    Parse video streams from ffprobe output.
    :stream: raw dict of video stream data.
    :stream_type: audio or video
    :returns: parsed dict of video stream data.
    """
    if stream_type != stream.get("codec_type"):
        return
    new_stream = {}
    if stream["codec_name"] in STREAM_STRINGS:
        new_stream["codec_name"] = STREAM_STRINGS[stream["codec_name"]]
    else:
        new_stream["codec_name"] = stream.get("codec_name")
    new_stream["duration"] = stream.get("duration")
    new_stream["level"] = str(stream.get("level"))
    new_stream["avg_frame_rate"] = stream.get("avg_frame_rate")
    new_stream["width"] = str(stream.get("width"))
    new_stream["height"] = str(stream.get("height"))
    new_stream["display_aspect_ratio"] = stream.get(
        "display_aspect_ratio")
    new_stream["sample_aspect_ratio"] = stream.get(
        "sample_aspect_ratio")
    return new_stream


def parse_audio_streams(stream, stream_type):
    """
    Parse audio streams from ffprobe output.
    :stream: raw dict of audio stream data.
    :stream_type: audio or video
    :returns: parsed dict of audio stream data.
    """
    if stream_type != stream.get("codec_type"):
        return
    new_stream = {}
    if stream["codec_name"] in STREAM_STRINGS:
        new_stream["codec_name"] = STREAM_STRINGS[stream["codec_name"]]
    else:
        new_stream["codec_name"] = stream.get("codec_name")
    new_stream["duration"] = stream.get("duration")
    new_stream["sample_rate"] = str(stream.get("sample_rate"))
    new_stream["channels"] = str(stream.get("channels"))
    return new_stream

STREAM_PARSERS = {
    "video": parse_video_streams,
    "audio": parse_audio_streams
}
