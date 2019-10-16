"""Metadata model for FFMpeg scraper."""
from __future__ import unicode_literals

import re
import six
from fractions import Fraction

from file_scraper.base import BaseMeta
from file_scraper.exceptions import SkipElementException
from file_scraper.utils import metadata
from file_scraper.utils import strip_zeros, iso8601_duration


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
                  "video/quicktime": [], "video/dv": [],
                  "application/mxf": []}
    _allow_versions = True   # Allow any version

    def __init__(self, probe_results, index, mimetype=None, version=None):
        """Do nothing special: this is a very simple metadata model."""
        # pylint: disable=unused-argument
        # The extra arguments are included to keep this metadata model
        # compatible with FFMpegMeta
        super(FFMpegSimpleMeta, self).__init__(mimetype, version)

    @metadata()
    def stream_type(self):
        """
        This metadata model scrapes nothing, return (:unav).
        """
        # pylint: disable=no-self-use
        return "(:unav)"


class FFMpegMeta(BaseMeta):
    """
    Metadata model for video/avi.

    This metadata model is used only for a limited selection of video formats,
    as the order of the reported streams from FFMpeg and MediaInfo do not
    necessarily correspond, so scraping the metadata with both is not
    practical due to difficulties in matching the metadata dicts representing
    the same streams.

    These file types are scraped using FFMpeg instead of MediaInfo due to
    determining the color/grayscale status of JPEG2000 video streams from
    MediaInfo output is difficult.
    """
    # pylint: disable=too-many-public-methods

    # Supported mimetypes
    _supported = {"video/avi": []}
    _allow_versions = True   # Allow any version

    # Codec names returned by ffmpeg do not always correspond to ones from
    # different scraper tools. This dict is used to unify the results.
    _codec_names = {
        "AVI (Audio Video Interleaved)": "AVI",
        }

    # MIME types need to be decided based on format name
    _mimetype_dict = {
        "AVI (Audio Video Interleaved)": "video/avi",
        "JPEG 2000": "video/jpeg2000",
        }

    container_stream = None

    def __init__(self, probe_results, index, mimetype=None, version=None):
        """
        Initialize the metadata model.

        :probe_results: List of streams returned by ffmpeg.probe.
        :index:  Index of the current stream.
        """
        self._probe_results = probe_results
        self._index = index
        if self.hascontainer():
            self.container_stream = self._probe_results["format"]
            if index == 0:
                self._ffmpeg_stream = probe_results["format"]
            else:
                self._ffmpeg_stream = probe_results["streams"][index-1]
        else:
            self._ffmpeg_stream = probe_results["streams"][index]

        super(FFMpegMeta, self).__init__(mimetype=mimetype, version=version)

    def hascontainer(self):
        """Check if file has a video container."""
        return ("codec_type" not in self._probe_results["format"]
                and self._probe_results["format"]["format_name"] not in
                ["mp3", "mpegvideo"])

    @metadata()
    def mimetype(self):
        """Return MIME type based on format name."""
        if self._given_mimetype:
            if self._index == 0:
                return self._given_mimetype
        mime = "(:unav)"
        if "format_long_name" in self._ffmpeg_stream:
            mime = self._ffmpeg_stream["format_long_name"]
        elif "codec_long_name" in self._ffmpeg_stream:
            mime = self._ffmpeg_stream["codec_long_name"]
        if mime in self._mimetype_dict:
            mime = self._mimetype_dict[mime]
        return mime

    @metadata()
    def version(self):
        """Return (:unap) as supported types do not have different versions."""
        return "(:unap)"

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
        if self.mimetype() in ["video/avi", "video/jpeg2000"]:
            return "Variable"
        return "(:unav)"

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self.mimetype() in ["video/jpeg2000"]:
            # signal format not relevant for JPEG2000 streams
            return "(:unap)"
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
        # TODO: Do we want to skip the container? Mediainfo didn't
#        if self._ffmpeg_stream == self.container_stream:
#            raise SkipElementException()
        if "bit_rate" in self._ffmpeg_stream:
            # TODO why this?
#            if self._ffmpeg_stream["codec_type"] == "video":
#                return "(:unav)"
            # TODO this is different from what we get from mediainfo
            return strip_zeros(six.text_type(float(
                self._ffmpeg_stream["bit_rate"]) / 10**6))
        return "(:unav)"

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
        if "encoder" in self._probe_results["format"]["tags"]:
            return self._probe_results["format"]["tags"]["encoder"]
        return "(:unav)"

    @metadata()
    def codec_creator_app_version(self):
        """Returns creator application version."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()
        if "encoder" in self._probe_results["format"]["tags"]:
            reg = re.search(r"([\d.]+)$",
                            self._probe_results["format"]["tags"]["encoder"])
            if reg is not None:
                return reg.group()  # TODO this used to be reg.group(1), why?
        return "(:unav)"

    @metadata()
    def codec_name(self):
        """Returns codec name."""
        if self.stream_type() not in ["audio", "video", "videocontainer"]:
            raise SkipElementException()

        codec = "(:unav)"
        if "codec_long_name" in self._ffmpeg_stream:
            codec = self._ffmpeg_stream["codec_long_name"]
        if "format_long_name" in self._ffmpeg_stream:
            codec = self._ffmpeg_stream["format_long_name"]

        if codec in self._codec_names:
            return self._codec_names[codec]
        return codec

    @metadata()
    def bits_per_sample(self):
        """Return bits per sample."""
        if self.stream_type() not in ["audio", "video"]:
            raise SkipElementException()
        if "bits_per_raw_sample" in self._ffmpeg_stream is not None:
            return six.text_type(self._ffmpeg_stream["bits_per_raw_sample"])
        return "(:unav)"
