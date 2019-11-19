"""Metadata model for FFMpeg scraper."""
from __future__ import unicode_literals

import re
from fractions import Fraction
import six

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
    _supported = {
        "video/mpeg": [],
        "video/mp4": [],
        "audio/mpeg": [],
        "audio/mp4": [],
        "video/MP1S": [],
        "video/MP2P": [],
        "video/MP2T": [],
        "video/x-matroska": [],
        "video/quicktime": [],
        "video/dv": [],
        }
    _allow_versions = True   # Allow any version

    # MIME types need to be decided based on format name
    _mimetype_dict = {
        "DV (Digital Video)": "video/dv",
        "Matroska / WebM": "video/x-matroska",
        "raw MPEG video": "video/mpeg",
        "MPEG-TS (MPEG-2 Transport Stream)": "video/MP2T",
        "MXF (Material eXchange Format)": "application/mxf",
        "AVI (Audio Video Interleaved)": "video/avi",
        "JPEG 2000": "video/jpeg2000",
        # These two do not always neatly correspond to one MIME type, so they
        # should be left for other scrapers such as Mediainfo.
        "QuickTime / MOV": "(:unav)",
        "MP2/3 (MPEG audio layer 2/3)": "(:unav)",
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

        super(FFMpegSimpleMeta, self).__init__(mimetype=mimetype,
                                               version=version)

    @metadata()
    def mimetype(self):
        """Return MIME type based on format name."""
        if self._given_mimetype:
            if self._index == 0:
                return self._given_mimetype

        mime = "(:unav)"
        if "format_long_name" in self._ffmpeg_stream:
            mime = self._ffmpeg_stream["format_long_name"]
        if mime in self._mimetype_dict:
            mime = self._mimetype_dict[mime]

        return mime

    @metadata()
    def stream_type(self):
        """
        This metadata model scrapes nothing, return (:unav).
        """
        # pylint: disable=no-self-use
        return "(:unav)"

    def hascontainer(self):
        """Check if file has a video container."""
        return ("codec_type" not in self._probe_results["format"]
                and self._probe_results["format"]["format_name"] not in
                ["mp3", "mpegvideo"])


class FFMpegMeta(FFMpegSimpleMeta):
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
    _supported = {
        "video/avi": [],
        "application/mxf": [],
        }
    _allow_versions = True   # Allow any version

    # Codec names returned by ffmpeg do not always correspond to ones from
    # different scraper tools. This dict is used to unify the results.
    _codec_names = {
        "AVI (Audio Video Interleaved)": "AVI",
        "MXF (Material eXchange Format)": "MXF",
        }

    # Some MIME types need to be decided based on codec name
    _codec_mimetype_dict = {
        "AVI (Audio Video Interleaved)": "video/avi",
        "MXF (Material eXchange Format)": "application/mxf",
        "JPEG 2000": "video/jpeg2000",
        }

    @metadata()
    def mimetype(self):
        """
        Return MIME type.

        If the MIME type can be determined based on format name as is done in
        the superclass, that result is returned. Otherwise, determining the
        MIME type based on codec name is attempted. This is relevant for
        JPEG2000 streams.
        """
        mime = super(FFMpegMeta, self).mimetype()
        if mime not in ["(:unav)", None]:
            return mime

        if "codec_long_name" in self._ffmpeg_stream:
            mime = self._ffmpeg_stream["codec_long_name"]
        if mime in self._codec_mimetype_dict:
            mime = self._codec_mimetype_dict[mime]
        return mime

    @metadata()
    def version(self):
        """Return (:unap) as supported types do not have different versions."""
        return "(:unap)"

    @metadata()
    def codec_quality(self):
        """
        Return codec quality.

        This is based solely on the wavelet transform of JPEG2000 images.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self.mimetype() == "video/jpeg2000":
            # The key is only present when using the patched version of
            # ffmpeg-python. See README.rst for more information.
            if self._ffmpeg_stream["lossless_wavelet_transform"]:
                return "lossless"
            return "lossy"
        return "(:unav)"

    @metadata()
    def data_rate_mode(self):
        """
        Return data rate mode.

        Must be resolved, if returns None. Only values "Fixed" or "Variable"
        are allowed.
        """
        if self.stream_type() not in ["video", "audio"]:
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
        """
        Return data rate (bit rate).

        If data rate information is not available, 0 is returned as per
        "A value 0 can be  allowed as an unknown value if the information can
        not be easily found out." in specifications
        """
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

        # TODO for MXT/JPEG2000 ffmpeg only reports bit rate in format? usable?
        # usable only for single-stream files?
        if "bit_rate" in self._probe_results["format"]:
            return strip_zeros(six.text_type(float(
                self._probe_results["format"]["bit_rate"]) / 10**6))

        return "0"

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
#            return self._ffmpeg_stream["r_frame_rate"].split("/")[0]
            # TODO is this ok? The old one above does not work for e.g.
            # 30000/1001
            return strip_zeros("%.2f" % float(Fraction(
                self._ffmpeg_stream["r_frame_rate"])))
        return "(:unav)"

    @metadata()
    def sampling(self):
        """Return chroma subsampling method."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if "pix_fmt" in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray", "monob", "monow"]:
                return "(:unap)"  # TODO makes sense, right?
            for sampling_code in ["444", "422", "420", "440", "411", "410"]:
                if sampling_code in self._ffmpeg_stream["pix_fmt"]:
                    return ":".join(sampling_code)
            # If pix_fmt is defined but none of the checks above apply, then
            # chroma subsampling is not possible for this format.
            return "(:unap)"

        return "(:unav)"

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
            return " ".join(filter(None, parts))  # TODO is this ok? Mediainfo
                                                  #      also had version here
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
        if "product_version" in self._probe_results["format"]["tags"]:
            return self._probe_results["format"]["tags"]["product_version"]
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
