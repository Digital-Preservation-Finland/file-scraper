""" This is a module that integrates ffmpeg and ffprobe tools with
information-package-tools for file validation purposes. Validation is
achieved by doing a conversion. If conversion is succesful, file is
interpred as a valid file. Container type is also validated with ffprobe.
"""

import json

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import compare_lists_of_dicts, handle_div, find_max_complete

MPEG1 = {"version": None, "mimetype": "video/MP1S"}
MPEG2_TS = {"version": None, "mimetype": "video/MP2T"}
MPEG2_PS = {"version": None, "mimetype": "video/MP2P"}
MP3 = {"version": None, "mimetype": "audio/mpeg"}
MP4 = {"version": None, "mimetype": "video/mp4"}
RAW_AAC = {"version": None, "mimetype": "audio/mp4"}
RAW_MPEG = {"version": None, "mimetype": "video/mpeg"}

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

STREAM_MIMETYPES = {
    "mpegvideo": "video/mpeg",
    "mpeg1video": "video/mpeg",
    "mpeg2video": "video/mpeg",
    "h264": "video/mp4",
    "libmp3lame": "audio/mpeg",
    "libshine": "audio/mpeg",
    "mp3": "audio/mpeg",
    "mp3adu": "audio/mpeg",
    "mp3adufloat": "audio/mpeg",
    "mp3float": "audio/mpeg",
    "mp3on4": "audio/mpeg",
    "mp3on4float": "audio/mpeg",
    "aac": "audio/mp4"
    }


class FFMpeg(BaseValidator):
    """FFMpeg validator class."""

    # TODO: Accepting MP4 containers may accept various other containers too
    _supported_mimetypes = {
        'video/mpeg': ['1', '2'],
        'audio/mpeg': ['1', '2'],
        'video/MP2T': [''],
        'video/MP2P': [''],
        'audio/mp4': [''],
#       'video/mp4': [''],
    }

    def validate(self):
        """validate file."""
        self.check_container_mimetype()
        if not set(self.metadata_info.keys()).intersection(
            set(['audio', 'video', 'audio_streams', 'video_streams'])):
                self.errors('Stream metadata was not found.')
                return
        if 'audio' in self.metadata_info:
            self.check_streams('audio')
        if 'video' in self.metadata_info:
            self.check_streams('video')
        if 'audio_streams' in self.metadata_info:
            self.check_streams('audio_streams')
        if 'video_streams' in self.metadata_info:
            self.check_streams('video_streams')
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
             'debug', '-print_format', 'json', self.metadata_info['filename']])
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
                "No matching mimetype information could be found,"
                "this might not be MPEG file."
                "FFprobe output: %s" % shell.stdout)
            return

        if 'audio_streams' in self.metadata_info or 'video_streams' in self.metadata_info:
            if self.metadata_info['format']['mimetype'] in \
                ['audio/mpeg', 'video/mpeg', 'audio/mp4']:
                    self.errors("Stream file format %s can not include streams,"
                                " as decribed in metadata."% (
                        self.metadata_info["format"]["mimetype"]))
            elif 'audio' in self.metadata_info or 'video' in self.metadata_info:
                self.errors("AudioMD or VideoMD metadata included for container %s."
                            " This must be directed to the including streams." % (
                    self.metadata_info["format"]["mimetype"]))

    def check_validity(self):
        """Check file validity. The validation logic is check that ffmpeg returncode
        is 0 and nothing is found in stderr. FFmpeg lists faulty parts of mpeg
        to stderr."""
        shell = Shell([
            'ffmpeg', '-v', 'error', '-i', self.metadata_info['filename'],
            '-f', 'null', '-'])
        if shell.returncode != 0 or shell.stderr != "":
            self.errors(
                "File %s not valid: %s" % (
                    self.metadata_info['filename'], shell.stderr))
            return
        self.messages("%s is valid." % self.metadata_info['filename'])

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

        :stream_type: "audio" or "video"
        """

        if stream_type in self.metadata_info:
            if stream_type == 'audio_streams':
                metadata = self.metadata_info[stream_type]
                stream_type = 'audio'
            elif stream_type == 'video_streams':
                metadata = self.metadata_info[stream_type]
                stream_type = 'video'
            else:
                metadata = [self.metadata_info]
        else:
            metadata = [self.metadata_info]

        found_streams = []
        shell = Shell(
            ['ffprobe', '-show_streams', '-show_format', '-print_format',
             'json', self.metadata_info['filename']])

        stream_data = json.loads(shell.stdout)

        for stream in stream_data.get("streams", []):
            new_stream = STREAM_PARSERS[stream_type](stream, stream_type)
            if not new_stream:
                continue
            found_streams.append(new_stream)

        (list1, list2) = find_max_complete(
            metadata, found_streams, ['format', 'mimetype', 'version'])

        match = compare_lists_of_dicts(list1, list2)

        if match is False:
            self.errors("Streams in %s are not what is "
                        "described in metadata. Found %s, expected %s" % (
                            self.metadata_info["filename"],
                            found_streams,
                            metadata))

        if stream_type not in metadata:
            return
        self.messages("Streams %s are according to metadata description" %
                      metadata_list)


def get_version(mimetype, stream_data):
    """
    Solve version of file format.
    """
    if mimetype == 'audio/mpeg':
        if stream_data in ['32', '44.1', '48']:
            return '1'
        elif stream_data in ['16', '22.05', '24']:
            return '2'
    if mimetype == 'video/mpeg':
        if stream_data in ['mpegvideo', 'mpeg1video']:
            return '1'
        elif stream_data in ['mpeg2video']:
            return '2'
    return None


def parse_video_streams(stream, stream_type):
    """
    Parse video streams from ffprobe output.
    :stream: raw dict of video stream data.
    :stream_type: audio or video
    :returns: parsed dict of video stream data.
    """
    if stream_type != stream.get("codec_type"):
        return
    new_stream = {"format": {}, "video": {}}
    if stream["codec_name"] in STREAM_MIMETYPES:
        new_stream["format"]["mimetype"] = STREAM_MIMETYPES[stream["codec_name"]]
    else:
        new_stream["format"]["mimetype"] = stream.get("codec_name")
    new_stream["format"]["version"] = \
        get_version(new_stream["format"]["mimetype"], stream['codec_name'])

    if "bit_rate" in stream:
        new_stream["video"]["bit_rate"] = \
            handle_div(stream.get("bit_rate")+"/1000000")
    if "avg_frame_rate" in stream:
        new_stream["video"]["avg_frame_rate"] = \
            handle_div(stream.get("avg_frame_rate"))
    if "display_aspect_ratio" in stream:
        new_stream["display_aspect_ratio"] = \
            handle_div(stream.get("display_aspect_ratio").replace(':', '/'))
    new_stream["video"]["width"] = str(stream.get("width"))
    new_stream["video"]["height"] = str(stream.get("height"))

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
    new_stream = {"format": {}, "audio": {}}
    if stream["codec_name"] in STREAM_MIMETYPES:
        new_stream["format"]["mimetype"] = STREAM_MIMETYPES[stream["codec_name"]]
    else:
        new_stream["format"]["mimetype"] = stream.get("codec_name")

    new_stream["audio"]["bits_per_sample"] = stream.get("bits_per_sample")
    if "bit_rate" in stream:
        new_stream["audio"]["bit_rate"] = \
            handle_div(stream.get("bit_rate")+"/1000")
    if "sample_rate" in stream:
        new_stream["audio"]["sample_rate"] = \
            handle_div(stream.get("sample_rate")+"/1000")
    new_stream["audio"]["channels"] = str(stream.get("channels"))

    new_stream["format"]["version"] = \
        get_version(new_stream["format"]["mimetype"],
                    new_stream["audio"]["sample_rate"])

    return new_stream


STREAM_PARSERS = {
    "video": parse_video_streams,
    "audio": parse_audio_streams
}
