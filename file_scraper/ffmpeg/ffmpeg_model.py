"""Metadata model for FFMpeg scraper."""
from __future__ import unicode_literals

import re
from fractions import Fraction

import six

from file_scraper.base import BaseMeta, SkipElementException
from file_scraper.utils import metadata, strip_zeros


class FFMpegSimpleMeta(BaseMeta):
    """
    A simple metadata class for not scraping any metadata using FFMpeg.

    See FFMpegMeta docstring for reasons to use this metadata model.
    """

    # Supported mimetypes
    _supported = {"video/mpeg": [], "video/mp4": [],
                  "audio/mpeg": [], "audio/mp4": [],
                  "video/MP1S": [], "video/MP2P": [],
                  "video/MP2T": [], "video/x-matroska": [],
                  "video/quicktime": [], "video/dv": []}
    _allow_versions = True   # Allow any version

    @metadata()
    def stream_type(self):
        """
        This metadata model scrapes nothing, return (:unav).
        """
        return "(:unav)"


class FFMpegMeta(BaseMeta):
    """
    Metadata model for a selection of video files.

    This metadata model can be used with mpeg, mp4, MP1s, MP2T, MP2P,
    quicktime, matroska and dv files.

    NB: This metadata model is not currently used. Mediainfo scrapes many of
        the same file types, but can return streams in different order, causing
        problems when the scraper results would be combined. Until this problem
        has been solved, only FFMpegSimpleMeta metadata model should be used.
    """
    # pylint: disable=too-many-public-methods

    # Supported mimetypes
    _supported = {"video/mpeg": [], "video/mp4": [],
                  "audio/mpeg": [], "audio/mp4": [],
                  "video/MP1S": [], "video/MP2P": [],
                  "video/MP2T": [], "video/x-matroska": [],
                  "video/quicktime": [], "video/dv": []}
    _allow_versions = True   # Allow any version
    # Codec names returned by ffmpeg do not always correspond to ones from
    # different scraper tools. This dict is used to unify the results.
    _codec_names = {"MP3 (MPEG audio layer 3)": "MPEG Audio",
                    "MPEG-1 video": "MPEG Video",
                    "MPEG-2 video": "MPEG Video",
                    "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10": "(:unav)",
                    "AAC (Advanced Audio Coding)": "AAC",
                    "FFmpeg video codec #1": "FFV1",
                    "DV (Digital Video)": "DV",
                    "PCM unsigned 8-bit": "PCM"}
    container_stream = None

    def __init__(self, probe_results, index):
        """
        Initialize the metadata model.

        :probe_results: List of streams returned by ffmpeg.probe.
        :index:  Index of the current stream.
        """
        self._probe_results = probe_results
        if index == 0 and self.hascontainer():
            self._ffmpeg_stream = probe_results["format"]
        else:
            self._ffmpeg_stream = probe_results["streams"][index-1]
        if self.hascontainer():
            self.container_stream = self._probe_results["format"]

    def hascontainer(self):
        """Check if file has a video container."""
        return ("codec_type" not in self._probe_results["format"]
                and self._probe_results["format"]["format_name"] not in
                ["mp3", "mpegvideo"])

    @metadata()
    def version(self):
        """Return version of stream."""
        return "(:unav)"

    @metadata()
    def codec_quality(self):
        """
        Return codec quality.

        Must be resolved, if returns None. Only values "lossy" and "lossless"
        are allowed.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        return None

    @metadata()
    def data_rate_mode(self):
        """
        Return data rate mode.

        Must be resolved, if returns None. Only values "Fixed" or "Variable"
        are allowed.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self.container_stream == self._ffmpeg_stream:
            raise SkipElementException()
        return None

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        if "codec_type" not in self._ffmpeg_stream and \
                self.index() > 0:
            return "other"
        if self.hascontainer() and self.index() == 0:
            return "videocontainer"
        if self._ffmpeg_stream["codec_type"] == "data":
            return "other"
        return self._ffmpeg_stream["codec_type"]

    @metadata()
    def index(self):
        """Return stream index."""
        if "index" not in self._ffmpeg_stream:
            return 0
        if self.hascontainer():
            return self._ffmpeg_stream["index"]
        return self._ffmpeg_stream["index"] - 1

    @metadata()
    def color(self):
        """
        Return color information.

        Only values from fixed list are allowed. Must be resolved, if returns
        None.
        """
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "pix_fmt" in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray"]:
                return "Grayscale"
            if self._ffmpeg_stream["pix_fmt"] in ["monob", "monow"]:
                return "B&W"
            return "Color"
        return None

    @metadata()
    def width(self):
        """Return frame width."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "width" in self._ffmpeg_stream:
            return six.text_type(self._ffmpeg_stream["width"])
        return "(:unav)"

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "height" in self._ffmpeg_stream:
            return six.text_type(self._ffmpeg_stream["height"])
        return "(:unav)"

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "sample_aspect_ratio" in self._ffmpeg_stream:
            return strip_zeros("%.3f" % float(Fraction(
                self._ffmpeg_stream["sample_aspect_ratio"].replace(":", "/"))))

        return "(:unav)"

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "display_aspect_ratio" in self._ffmpeg_stream:
            return strip_zeros("%.3f" % float(Fraction(
                self._ffmpeg_stream["display_aspect_ratio"].replace(
                    ":", "/"))))
        return "(:unav)"

    @metadata()
    def data_rate(self):
        """Return data rate (bit rate)."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._ffmpeg_stream == self.container_stream:
            raise SkipElementException()
        if "bit_rate" in self._ffmpeg_stream:
            if self._ffmpeg_stream["codec_type"] == "video":
                return "(:unav)"
            return strip_zeros(six.text_type(float(
                self._ffmpeg_stream["bit_rate"]) / 1000))
        return "(:unav)"

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "r_frame_rate" in self._ffmpeg_stream:
            return self._ffmpeg_stream["r_frame_rate"].split("/")[0]
        return "(:unav)"

    @metadata()
    def sampling(self):
        """Return chroma subsampling method."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        sampling = "(:unav)"
        if "pix_fmt" in self._ffmpeg_stream:
            for sampling_code in ["444", "422", "420", "440", "411", "410"]:
                if sampling_code in self._ffmpeg_stream["pix_fmt"]:
                    sampling = ":".join(sampling_code)
                    break
        return sampling

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
            return "MPEG Audio"  # as other scrapers
        return self._ffmpeg_stream["codec_long_name"].split(" ")[0]

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._ffmpeg_stream == self.container_stream:
            raise SkipElementException()
        if "sample_rate" in self._ffmpeg_stream:
            return strip_zeros(six.text_type(float(
                self._ffmpeg_stream["sample_rate"])/1000))
        return "(:unav)"

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if "channels" in self._ffmpeg_stream:
            return six.text_type(self._ffmpeg_stream["channels"])
        return "(:unav)"

    @metadata()
    def codec_creator_app(self):
        """Returns creator application."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "encoder" in self._probe_results["format"]:
            return self._probe_results["format"]["encoder"]
        return "(:unav)"

    @metadata()
    def codec_creator_app_version(self):
        """Returns creator application version."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "encoder" in self._probe_results["format"]:
            reg = re.search(r"([\d.]+)$",
                            self._probe_results["format"]["encoder"])
            if reg is not None:
                return reg.group(1)
        return "(:unav)"

    @metadata()
    def codec_name(self):
        """Returns codec name."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "codec_long_name" in self._ffmpeg_stream:
            codec = self._ffmpeg_stream["codec_long_name"]
            if codec in self._codec_names:
                return self._codec_names[codec]
            return codec
        return "(:unav)"

    @metadata()
    def bits_per_sample(self):
        """Return bits per sample."""
        if self.stream_type() not in ["audio", "video"]:
            raise SkipElementException()
        if "bits_per_raw_sample" in self._ffmpeg_stream is not None:
            return six.text_type(self._ffmpeg_stream["bits_per_raw_sample"])
        return "(:unav)"
