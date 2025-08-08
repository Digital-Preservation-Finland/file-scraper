"""Metadata model for FFMpeg extractor."""

import re
from fractions import Fraction

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.exceptions import SkipElementException
from file_scraper.utils import metadata, strip_zeros, iso8601_duration


class FFMpegSimpleMeta(BaseMeta):
    """
    A simple metadata class for not scraping any metadata using FFMpeg.

    See FFMpegMeta docstring for reasons to use this metadata model.
    """

    # Supported mimetypes
    _supported = {
        "audio/aac": [],
        "audio/flac": [],
        "audio/l8": [],
        "audio/l16": [],
        "audio/l24": [],
        "audio/mp4": [],
        "audio/mpeg": [],
        "audio/x-aiff": [],
        "audio/x-ms-wma": [],
        "audio/x-wav": [],
        "video/avi": [],
        "video/dv": [],
        "video/h264": [],
        "video/h265": [],
        "video/mp1s": [],
        "video/mp2p": [],
        "video/mp2t": [],
        "video/mp4": [],
        "video/mpeg": [],
        "video/quicktime": [],
        "video/x-ffv": [],
        "video/x-matroska": [],
        "video/x-ms-asf": [],
        "video/x-ms-wmv": [],
    }
    _allow_versions = True   # Allow any version

    _supported_formats = {
        "Audio IFF": [
            # Audio
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
        ],
        "ASF (Advanced / Active Streaming Format)": [
            # Audio
            "Windows Media Audio 9 Professional",
            "Windows Media Audio Lossless",
            # Video
            "SMPTE VC-1",
            "Windows Media Video 9"
        ],
        "AVI (Audio Video Interleaved)": [
            # Audio
            "MP3 (MPEG audio layer 3)",
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
            # Video
            "DV (Digital Video)",
            "MPEG-1 video",
            "MPEG-2 video"
        ],
        "DV (Digital Video)": [
            # Audio
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
            # Video
            "DV (Digital Video)"
        ],
        "Matroska / WebM": [
            # Audio
            "FLAC (Free Lossless Audio Codec)",
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
            "raw FLAC",
            # Video
            "FFmpeg video codec #1",
            "H.265 / HEVC (High Efficiency Video Coding)"
        ],
        "MP2/3 (MPEG audio layer 2/3)": [
            # Audio
            "MP3 (MPEG audio layer 3)"
        ],
        "MPEG-PS (MPEG-2 Program Stream)": [
            # Audio
            "MP3 (MPEG audio layer 3)",
            # Video
            "MPEG-1 video",
            "MPEG-2 video"
        ],
        "MPEG-TS (MPEG-2 Transport Stream)": [
            # Audio
            "AAC (Advanced Audio Coding)",
            "MP3 (MPEG audio layer 3)",
            # Video
            "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "H.265 / HEVC (High Efficiency Video Coding)",
            "MPEG-1 video",
            "MPEG-2 video",
            "raw H.264 video"
        ],
        "MXF (Material eXchange Format)": [
            # Audio
            "AAC (Advanced Audio Coding)",
            "MP3 (MPEG audio layer 3)",
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
            # Video
            "DV (Digital Video)",
            "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "JPEG 2000",
            "MPEG-1 video",
            "MPEG-2 video",
            "raw H.264 video"
        ],
        # video/quicktime and video/mp4
        "QuickTime / MOV": [
            # Audio
            "AAC (Advanced Audio Coding)",
            "MP3 (MPEG audio layer 3)",
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
            # Video
            "DV (Digital Video)",
            "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "H.265 / HEVC (High Efficiency Video Coding)",
            "JPEG 2000",
            "MPEG-1 video",
            "MPEG-2 video",
            "raw H.264 video"
        ],
        "raw MPEG video": [
            # Video
            "MPEG-1 video",
            "MPEG-2 video"
        ],
        "WAV / WAVE (Waveform Audio)": [
            # Audio
            "PCM signed 8-bit",
            "PCM signed 16-bit big-endian",
            "PCM signed 16-bit little-endian",
            "PCM signed 24-bit big-endian",
            "PCM signed 24-bit little-endian",
            "PCM unsigned 8-bit",
            "PCM unsigned 16-bit big-endian",
            "PCM unsigned 16-bit little-endian",
            "PCM unsigned 24-bit big-endian",
            "PCM unsigned 24-bit little-endian",
        ],
        "raw FLAC": [
            "FLAC (Free Lossless Audio Codec)",
            "raw FLAC"
        ]
    }

    def __init__(self, probe_results, index):
        """
        Initialize the metadata model.

        :probe_results: List of streams returned by ffmpeg.probe.
        :index:  Index of the current stream.
        """
        self._probe_results = probe_results
        self._index = index
        self._ffmpeg_stream = self._current_stream()

    def av_format_supported(self):
        """Return value whether the audio/video format is supported or not.

        The stream type may be a video container, video, audio or other kind
        of stream, such as timetracker data for syncronizing audio/video
        streams or subtitles. Here we check if the file has any audio or
        video stream (or a video container) which is not listed in the model.
        The other stream types (i.e. subtitles or timetrackers) result None.

        None - Stream type is not a video container, video nor audio format
        False - Stream type is video container, video or audio, but the
                format is not supported
        True - Supported
        """
        supported = False
        if self.hascontainer() and self.index() == 0:
            supported = self.streams_in_container_supported()
            return supported

        if self.index() > 0:
            if "codec_type" not in self._ffmpeg_stream:
                return None
            if self._ffmpeg_stream["codec_type"] not in ["video", "audio"]:
                return None

        if "format_long_name" in self._ffmpeg_stream:
            if (self._ffmpeg_stream["format_long_name"] not in
                    self._supported_formats):
                return False

        if "codec_long_name" in self._ffmpeg_stream:
            supported = any(self._ffmpeg_stream["codec_long_name"] in
                            val for val in self._supported_formats.values())

        return supported

    def streams_in_container_supported(self):
        """Check if the streams inside a container are supported.

        :returns: True if all of the streams are supported, False
                  otherwise.
        """
        container = self._ffmpeg_stream["format_long_name"]
        if container not in self._supported_formats:
            return False
        av_streams = []
        for stream in self._probe_results["streams"]:
            if stream["codec_type"] in ["video", "audio"]:
                av_streams.append(stream["codec_long_name"])
        for stream in av_streams:
            if stream not in self._supported_formats[container]:
                return False
        return True

    def hascontainer(self):
        """Check if file has a video container.

        We have to check a little bit more than just the container name.
        For example, DV or FLAC might be either a container or just a
        raw stream.
        """
        format_name = self._probe_results["format"]["format_long_name"]

        is_container = "codec_type" not in self._probe_results["format"]

        if is_container and format_name == "DV (Digital Video)":
            is_container = len(self._probe_results["streams"]) > 1

        if is_container and format_name == "raw FLAC":
            is_container = len(self._probe_results["streams"]) > 1

        return is_container

    @metadata()
    def index(self):
        """Return stream index."""
        if "index" not in self._ffmpeg_stream:
            return 0
        if self.hascontainer():
            return self._ffmpeg_stream["index"]
        return self._ffmpeg_stream["index"] - 1

    @property
    def _container_stream(self):
        """
        Return the container stream from the ffprobe results.

        The stream is returned as a dict, in the format used by ffprobe.
        If the file is not a container type, None is returned instead.
        """
        if self.hascontainer():
            return self._probe_results["format"]
        return None

    def _current_stream(self):
        """
        Return the stream dict handled by this instance.

        The constructor is given the full ffprobe output dict, but one
        metadata model instance only handles a single stream. This
        method extracts the relevant part of the dictionary and returns
        it. For non-container formats the n'th stream is simply the n'th
        dict in the stream list, but for containers the first stream is
        the format stream and then the following streams are found at
        the (n-1)'th indices of the stream list.
        """
        if self.hascontainer():
            if self._index == 0:
                return self._probe_results["format"]
            return self._probe_results["streams"][self._index-1]
        return self._probe_results["streams"][self._index]


class FFMpegMeta(FFMpegSimpleMeta):
    """
    Metadata model for application/mxf.

    This metadata model is used only for a limited selection of video
    formats, as the order of the reported streams from FFMpeg and
    MediaInfo do not necessarily correspond, so scraping the metadata
    with both is not practical due to difficulties in matching the
    metadata dicts representing the same streams.

    These file types are scraped using FFMpeg instead of MediaInfo due
    to determining the color/grayscale status of JPEG2000 video streams
    from MediaInfo output is difficult.
    """

    # pylint: disable=too-many-public-methods

    # Supported mimetypes
    _supported = {
        "application/mxf": [],
        "video/jpeg2000": []
        }
    _allow_versions = True   # Allow any version

    # Some MIME types need to be decided based on codec name
    _codec_mimetype_dict = {
        "MXF (Material eXchange Format)": "application/mxf",
        "JPEG 2000": "video/jpeg2000",
        }

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        mime = UNAV
        if "format_long_name" in self._ffmpeg_stream:
            return self._codec_mimetype_dict.get(
                self._ffmpeg_stream["format_long_name"], UNAV)
        if mime not in [UNAV, None]:
            return mime

        if "codec_long_name" in self._ffmpeg_stream:
            mime = self._ffmpeg_stream["codec_long_name"]
        if mime in self._codec_mimetype_dict:
            mime = self._codec_mimetype_dict[mime]
        return mime

    @metadata()
    def version(self):
        """Return supported format versions.

        Return (:unap) as supported types do not have different
        versions.
        """
        return UNAP if self.mimetype() != UNAV else UNAV

    @metadata()
    def codec_quality(self):
        """
        Return codec quality.

        This is based solely on the wavelet transform of JPEG2000
        images.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self.mimetype() == "video/jpeg2000":
            # The key is only present when using the patched version of
            # ffmpeg-python. See README.rst for more information.
            if self._ffmpeg_stream["lossless_wavelet_transform"]:
                return "lossless"
            return "lossy"
        return UNAV

    @metadata()
    def data_rate_mode(self):
        """
        Return data rate mode.

        Must be resolved, if returns None. Only values "Fixed" or
        "Variable" are allowed.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self.mimetype() in ["video/jpeg2000"]:
            return "Variable"
        return UNAV

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self.mimetype() in ["video/jpeg2000"]:
            # signal format not relevant for JPEG2000 streams
            return UNAP
        return UNAV

    @metadata()
    def stream_type(self):
        """Return stream type."""
        if "codec_type" not in self._ffmpeg_stream and \
                self.index() > 0:
            return UNAV
        if self.hascontainer() and self.index() == 0:
            return "videocontainer"
        if self._ffmpeg_stream["codec_type"] == "data":
            return UNAV
        return self._ffmpeg_stream["codec_type"]

    @metadata()
    def color(self):
        """
        Return color information.

        Only values from fixed list are allowed. Must be resolved, if
        returns None.
        """
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "pix_fmt" in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray"]:
                return "Grayscale"
            if self._ffmpeg_stream["pix_fmt"] in ["monob", "monow"]:
                return "B&W"
            return "Color"
        return UNAV

    @metadata()
    def width(self):
        """Return frame width."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "width" in self._ffmpeg_stream:
            return str(self._ffmpeg_stream["width"])
        return UNAV

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "height" in self._ffmpeg_stream:
            return str(self._ffmpeg_stream["height"])
        return UNAV

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        # ffmpeg-python in EL7 may return 0:1 for sar, which is an invalid
        # value. In that case, return UNAV.
        sar = self._ffmpeg_stream.get("sample_aspect_ratio")
        if sar and sar[0] != "0":
            value = float(Fraction(
                self._ffmpeg_stream['sample_aspect_ratio'].replace(':', '/')))
            return strip_zeros(
                f"{value :.3f}")

        return UNAV

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        # ffmpeg-python in EL7 may return 0:1 for dar, which is an invalid
        # value. In that case, return UNAV.
        dar = self._ffmpeg_stream.get("display_aspect_ratio")
        if dar and dar[0] != "0":
            value = float(Fraction(
                self._ffmpeg_stream['display_aspect_ratio'].replace(':', '/')))
            return strip_zeros(
                f"{value :.3f}")
        return UNAV

    @metadata()
    def data_rate(self):
        """
        Return data rate (bit rate) in mbps.

        VideoMD specification defines dataRate as "data rate of the
        audio". This is a copy-paste error in the specification, and it
        should be "data rate of the video".
        """
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._ffmpeg_stream == self._container_stream:
            raise SkipElementException()
        if "bit_rate" in self._ffmpeg_stream:
            return strip_zeros(str(float(
                self._ffmpeg_stream["bit_rate"]) / 10**6))

        if "bit_rate" in self._probe_results["format"]:
            return strip_zeros(str(float(
                self._probe_results["format"]["bit_rate"]) / 10**6))

        return UNAV

    @metadata()
    def duration(self):
        """Return duration."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        return iso8601_duration(float(self._ffmpeg_stream["duration"]))

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "r_frame_rate" in self._ffmpeg_stream:
            value = float(Fraction(self._ffmpeg_stream['r_frame_rate']))
            return strip_zeros(
                f"{value :.2f}")
        return UNAV

    @metadata()
    def sampling(self):
        """Return chroma subsampling method."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "pix_fmt" in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray", "monob", "monow"]:
                return UNAP
            for sampling_code in ["444", "422", "420", "440", "411", "410"]:
                if sampling_code in self._ffmpeg_stream["pix_fmt"]:
                    return ":".join(sampling_code)
            # If pix_fmt is defined but none of the checks above apply,
            # then chroma subsampling is not possible for this format.
            return UNAP

        return UNAV

    @metadata()
    def sound(self):
        """Return "Yes" if sound channels are present, otherwise "No"."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        for stream in self._probe_results["streams"]:
            if stream["codec_type"] == "audio":
                return "Yes"
        return "No"

    @metadata()
    def audio_data_encoding(self):
        """Return audio data encoding."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if "codec_long_name" not in self._ffmpeg_stream:
            raise SkipElementException()
        if "MP3" in self._ffmpeg_stream["codec_long_name"]:
            return "MPEG Audio"  # as other extractors
        return self._ffmpeg_stream["codec_long_name"].split(" ")[0]

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if "sample_rate" in self._ffmpeg_stream:
            return strip_zeros(str(float(
                self._ffmpeg_stream["sample_rate"])/1000))
        return UNAV

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if "channels" in self._ffmpeg_stream:
            return str(self._ffmpeg_stream["channels"])
        return UNAV

    @metadata()
    def codec_creator_app(self):
        """Return creator application."""
        format_info = self._probe_results["format"]["tags"]
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "encoder" in format_info:
            return format_info["encoder"]
        if ("product_name" in format_info or
                "company_name" in format_info):
            parts = []
            parts.append(format_info.get("company_name", None))
            parts.append(format_info.get("product_name", None))
            return " ".join(filter(None, parts))
        return UNAV

    @metadata()
    def codec_creator_app_version(self):
        """Return creator application version."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "encoder" in self._probe_results["format"]["tags"]:
            reg = re.search(r"([\d.]+)$",
                            self._probe_results["format"]["tags"]["encoder"])
            if reg is not None:
                return reg.group()
        if "product_version" in self._probe_results["format"]["tags"]:
            return self._probe_results["format"]["tags"]["product_version"]
        return UNAV

    @metadata()
    def codec_name(self):
        """Return codec name."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()

        codec = UNAV
        if "codec_long_name" in self._ffmpeg_stream:
            codec = self._ffmpeg_stream["codec_long_name"]
        if "format_long_name" in self._ffmpeg_stream:
            codec = self._ffmpeg_stream["format_long_name"]

        return codec

    @metadata()
    def bits_per_sample(self):
        """Return bits per sample."""
        if self.stream_type() not in ["audio", "video"]:
            raise SkipElementException()
        if ("bits_per_raw_sample" in self._ffmpeg_stream and
                self._ffmpeg_stream["bits_per_raw_sample"] is not None):
            return str(self._ffmpeg_stream["bits_per_raw_sample"])
        return UNAV
