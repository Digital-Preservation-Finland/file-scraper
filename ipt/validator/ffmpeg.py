""" This is a module that integrates ffmpeg and ffprobe tools with
information-package-tools for file validation purposes. Validation is
achieved by doing a conversion. If conversion is succesful, file is
interpred as a valid file. Container type is also validated with ffprobe.
"""

import json

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import compare_lists_of_dicts, filter_list_of_dicts

MPEG1 = {"version": "1", "mimetype": "video/MP1S"}
MPEG2_TS = {"version": "2", "mimetype": "video/MP2T"}
MPEG2_PS = {"version": "2", "mimetype": "video/MP2P"}
MP3 = {"version": "", "mimetype": "audio/mpeg"}
MP4 = {"version": "", "mimetype": "video/mp4"}
RAW_AAC = {"version": "", "mimetype": "audio/mp4"}
RAW_MPEG = {"version": "1", "mimetype": "video/mpeg"}

MPEG1_STRINGS = ["MPEG-1 video"]
RAW_MPEG_STRINGS = ["raw MPEG video"]
MPEG2_TS_STRINGS = ["MPEG-2 transport stream format",
                    "MPEG-TS (MPEG-2 Transport Stream)"]
MPEG2_PS_STRINGS = ["MPEG-PS format", "MPEG-2 PS (DVD VOB)",
                    "MPEG-PS (MPEG-2 Program Stream)"]
MP3_STRINGS = [
    "MPEG audio layer 2/3",
    "MP3 (MPEG audio layer 3)",
    "MP2/3 (MPEG audio layer 2/3)",
    "ADU (Application Data Unit) MP3 (MPEG audio layer 3)",
    "MP3onMP4",
    "libmp3lame MP3 (MPEG audio layer 3)",
    "libshine MP3 (MPEG audio layer 3)"]
MPEG4_STRINGS = ["M4A", "QuickTime/MPEG-4/Motion JPEG 2000 format",
                 "QuickTime / MOV"]
RAW_AAC_STRINGS = ["raw ADTS AAC",
                   "raw ADTS AAC (Advanced Audio Coding)"]

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

            "format": {
                "filename": "tests/data/02_filevalidation_data/mpg/mpg1.mpg",
                "nb_streams": 1,
                "format_name": "mpegvideo",
                "format_long_name": "raw MPEG video",
                "duration": "19.025400",
                "size": "761016",
                "bit_rate": "320000"
            }
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
        audioMD and videoMD. Ffprobe command gives a json output in the
        following format:

            "streams": [
            {
                "index": 0,
                "codec_name": "mpeg1video",
                "codec_long_name": "MPEG-1 video",
                "codec_type": "video",
                "codec_time_base": "1001/30000",
                "codec_tag_string": "[0][0][0][0]",
                "codec_tag": "0x0000",
                "width": 320,
                "height": 240,
                "has_b_frames": 1,
                "sample_aspect_ratio": "1:1",
                "display_aspect_ratio": "4:3",
                "pix_fmt": "yuv420p",
                "level": -99,
                "timecode": "00:00:00:00",
                "r_frame_rate": "30000/1001",
                "avg_frame_rate": "30000/1001",
                "time_base": "1/1200000",
                "duration": "19.025400"
            }

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

        # Remove the duration key from both lists of dicts, because the
        # duration varies depending on the ffmpeg version used.
        # TODO: figure out a way to approximate if the duration is almost the
        # same.
        filter_list_of_dicts(self.fileinfo.get(stream_type), "duration")
        filter_list_of_dicts(found_streams.get(stream_type), "duration")

        match = compare_lists_of_dicts(
            self.fileinfo.get(stream_type), found_streams[stream_type])
        if match is False:
            self.errors("Streams in %s are not what is "
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
