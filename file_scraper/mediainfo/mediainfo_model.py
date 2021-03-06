"""Metadata scraper for AV files."""
from __future__ import unicode_literals

import re
import six

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.exceptions import SkipElementException
from file_scraper.utils import iso8601_duration, strip_zeros, metadata


def pcm_mimetype(codec_name, bits_per_sample):
    """
    Check if stream is PCM and return it's mimetype.

    :codec_name: Codec name from Mediainfo
    :bits_per_sample: Bits per sample from Mediainfo
    :returns: PCM mimetype or (:unav)
    """
    if codec_name == "PCM" and bits_per_sample is not None:
        mime = "audio/L%s" % bits_per_sample
        # Allow only certain bit depths
        if mime in ["audio/L8", "audio/L16", "audio/L20",
                    "audio/L24"]:
            return mime

    raise ValueError("Not a PCM stream.")


class BaseMediainfoMeta(BaseMeta):
    """Metadata models for files scraped using MediainfoScraper"""
    # pylint: disable=too-many-public-methods

    container_stream = None
    _containers = []
    _mime_dict = {}

    def __init__(self, tracks, index):
        """
        Initialize the metadata model.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        """
        # pylint: disable=too-many-arguments
        self._stream = tracks[index]
        self._tracks = tracks
        if self.hascontainer():
            self._index = index
            self.container_stream = tracks[0]
        else:
            self._index = index - 1

    def hascontainer(self):
        """Find out if file is a video container."""
        if self._tracks[0].format in self._containers:
            return True
        if len(self._tracks) < 3:
            return False

        return True

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        try:
            return self._mime_dict[self.codec_name()]
        except (KeyError, SkipElementException):
            pass

        return UNAV

    @metadata()
    def version(self):
        """Return version of stream."""
        if self._stream.format_version is not None:
            return self._stream.format_version.replace("Version ", "")
        return UNAV

    @metadata()
    def stream_type(self):
        """Return stream type."""
        if self._stream.track_type == "General":
            if self.hascontainer():
                return "videocontainer"
        return self._stream.track_type.lower()

    @metadata()
    def index(self):
        """Return stream index."""
        return self._index

    @metadata()
    def color(self):
        """
        Return color information.

        Only values from fixed list are allowed. Must be resolved, if returns
        None.
        """
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.color_space is not None:
            if self._stream.color_space in ["RGB", "YUV"]:
                return "Color"
            if self._stream.color_space in ["Y"]:
                return "Grayscale"
        if self._stream.chroma_subsampling is not None:
            return "Color"
        return UNAV

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.standard is not None:
            return self._stream.standard
        return UNAV

    @metadata()
    def width(self):
        """Return frame width."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.width is not None:
            return six.text_type(self._stream.width)
        return UNAV

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.height is not None:
            return six.text_type(self._stream.height)
        return UNAV

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.pixel_aspect_ratio is not None:
            return strip_zeros(six.text_type(self._stream.pixel_aspect_ratio))
        return UNAV

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.display_aspect_ratio is not None:
            return strip_zeros(six.text_type(
                self._stream.display_aspect_ratio))
        return UNAV

    @metadata()
    def data_rate(self):
        """Return data rate (bit rate)."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_rate is not None:
            if self._stream.track_type == "Video":
                return strip_zeros(six.text_type(float(
                    self._stream.bit_rate) / 1000000))
            return strip_zeros(six.text_type(float(
                self._stream.bit_rate)/1000))
        return UNAV

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.frame_rate is not None:
            return strip_zeros(six.text_type(self._stream.frame_rate))
        return UNAV

    @metadata()
    def sampling(self):
        """Return chroma subsampling method."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.chroma_subsampling is not None:
            return self._stream.chroma_subsampling
        return UNAV

    @metadata()
    def sound(self):
        """Return "Yes" if sound channels are present, otherwise "No"."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if (self._tracks[0].count_of_audio_streams is not None and
                int(self._tracks[0].count_of_audio_streams) > 0):
            return "Yes"
        if (self._tracks[0].audio_count is not None and
                int(self._tracks[0].audio_count) > 0):
            return "Yes"
        return "No"

    @metadata()
    def codec_quality(self):
        """
        Return codec quality.

        Must be resolved, if returns None. Only values "lossy" or "lossless"
        are allowed.
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        return UNAV

    @metadata()
    def data_rate_mode(self):
        """
        Return data rate mode.

        Must be resolved, if returns None. The allowed values are "Fixed" and
        "Variable".
        """
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_rate_mode == "CBR":
            return "Fixed"
        if self._stream.bit_rate_mode is not None:
            return "Variable"
        return UNAV

    @metadata()
    def audio_data_encoding(self):
        """Return audio data encoding."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.format is not None:
            return six.text_type(self._stream.format)
        return UNAV

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.sampling_rate is not None:
            return strip_zeros(six.text_type(float(
                self._stream.sampling_rate)/1000))
        return UNAV

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.channel_s is not None:
            return six.text_type(self._stream.channel_s)
        return UNAV

    @metadata()
    def codec_creator_app(self):
        """Returns creator application."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._tracks[0].writing_application is not None:
            return self._tracks[0].writing_application
        return UNAV

    @metadata()
    def codec_creator_app_version(self):
        """Returns creator application version."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._tracks[0].writing_application is not None:
            reg = re.search(r"([\d.]+)$",
                            self._tracks[0].writing_application)
            if reg is not None:
                return reg.group(1)
        return UNAV

    @metadata()
    def codec_name(self):
        """Returns codec name."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._stream.format is not None:
            return self._stream.format
        return UNAV

    @metadata()
    def duration(self):
        """Return duration."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.duration is not None:
            return iso8601_duration(float(
                self._stream.duration) / 1000)
        return UNAV

    @metadata()
    def bits_per_sample(self):
        """Return bits per sample."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_depth is not None:
            return six.text_type(self._stream.bit_depth)
        return UNAV


class MovMediainfoMeta(BaseMediainfoMeta):
    """Scraper for Quicktime Movie AV container and selected streams"""
    _supported = {"video/quicktime": [""], "video/dv": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["QuickTime"]
    _mime_dict = {"QuickTime": "video/quicktime",
                  "DV": "video/dv",
                  "AVC": "video/mp4",
                  "AAC": "audio/mp4"}

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        try:
            return pcm_mimetype(self.codec_name(), self.bits_per_sample())
        except (ValueError, SkipElementException):
            try:
                return self._mime_dict[self._stream.format_profile]
            except KeyError:
                pass

        return super(MovMediainfoMeta, self).mimetype()

    @metadata()
    def version(self):
        """
        Return version.

        Quicktime, DV, MP4, and PCM streams (audio/L*) do not have version,
        and and therefore the result is unapplicable (:unap).
        """
        if self.mimetype() in [
                "audio/L8", "audio/L16", "audio/L20", "audio/24",
                "video/quicktime", "video/dv", "video/mp4", "audio/mp4"]:
            return UNAP
        return super(MovMediainfoMeta, self).version()

    @metadata()
    def codec_quality(self):
        """Returns codec quality."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        if self.stream_type() == "audio":
            return "lossless"
        if self.mimetype() == "video/mp4":
            return "lossy"
        return UNAV

    @metadata()
    def signal_format(self):
        """Returns signal format (usually PAL of NTSC)."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.standard is not None:
            return self._stream.standard
        return super(MovMediainfoMeta, self).signal_format()

    @metadata()
    def data_rate_mode(self):
        """
        Return data rate mode if available.

        MP4 is assumed to always have variable bit rate, based on e.g.
        https://slhck.info/video/2017/03/01/rate-control.html claiming that MP4
        does not support NAL stuffing and thus it cannot be forced to have
        constant bit rate.
        """
        mode = super(MovMediainfoMeta, self).data_rate_mode()
        if mode not in [UNAV, None]:
            return mode
        if self.mimetype() == "video/mp4":
            return "Variable"
        return UNAV


class MkvMediainfoMeta(BaseMediainfoMeta):
    """Scraper for Matroska AV container with selected streams."""

    _supported = {"video/x-matroska": ["4"]}
    _allow_versions = True  # Allow any version
    _containers = ["Matroska"]
    _mime_dict = {"Matroska": "video/x-matroska",
                  "FLAC": "audio/flac",
                  "FFV1": "video/x-ffv"}

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        try:
            return pcm_mimetype(self.codec_name(), self.bits_per_sample())
        except (ValueError, SkipElementException):
            pass

        return super(MkvMediainfoMeta, self).mimetype()

    @metadata()
    def version(self):
        """
        Return version of stream.

        The version number 1.2.1 of FLAC comes from PRONOM registry. This is
        actually the version number of FLAC tools containing FLAC format
        specification. Although the latest FLAC tools version is 1.3.3,
        version 1.2.1 still includes the latest format change and was released
        in 2007. There is no separate version numbering in FLAC format itself,
        and therefore, there is no proper way to extract it.

        PCM audio streams (i.e. audio/L*) do not have version, and therefore
        the result is unapplicable (:unap).
        """
        if self.mimetype() == "audio/flac":
            return "1.2.1"
        if self.mimetype() in ["audio/L8", "audio/L16", "audio/L20",
                               "audio/24"]:
            return UNAP

        version = super(MkvMediainfoMeta, self).version()
        if isinstance(version, six.text_type):
            version = version.split(".")[0]
        return version

    @metadata()
    def signal_format(self):
        """Returns signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return UNAP

    @metadata()
    def codec_quality(self):
        """Returns codec quality."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        if self.stream_type() == "audio":
            return "lossless"


class WavMediainfoMeta(BaseMediainfoMeta):
    """Scraper for WAV audio."""

    _supported = {"audio/x-wav": ["2", ""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        if self._tracks[0].format == "Wave":
            return "audio/x-wav"
        return UNAV

    @metadata()
    def version(self):
        """Returns version."""
        if self._tracks[0].bext_present is not None \
                and self._tracks[0].bext_present == "Yes":
            return "2"
        return UNAP

    @metadata()
    def codec_quality(self):
        """Returns codec quality."""
        if self.stream_type() == "audio":
            return "lossless"
        raise SkipElementException()


class MpegMediainfoMeta(BaseMediainfoMeta):
    """Scraper for MPEG video and audio."""

    # Supported mimetypes
    _supported = {"video/mpeg": ["1", "2"], "video/mp4": [""],
                  "audio/mpeg": ["1", "2"], "audio/mp4": [""],
                  "video/MP2T": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["MPEG-TS", "MPEG-4"]
    _mime_dict = {"AAC": "audio/mp4",
                  "AVC": "video/mp4",
                  "MPEG-4": "video/mp4",
                  "MPEG Video": "video/mpeg",
                  "MPEG Audio": "audio/mpeg"}

    @metadata()
    def signal_format(self):
        """Returns signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return UNAP

    @metadata()
    def codec_quality(self):
        """Returns codec quality."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        return "lossy"

    @metadata()
    def data_rate_mode(self):
        """Returns data rate mode. Must be resolved."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_rate_mode == "CBR":
            return "Fixed"
        return "Variable"

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        try:
            return self._mime_dict[self.codec_name()]
        except SkipElementException:
            pass
        except KeyError:
            for track in self._tracks:
                try:
                    if track.track_type == "Video":
                        if self.codec_name() == "MPEG-TS":
                            if track.format_version == "Version 2":
                                return "video/MP2T"
                except SkipElementException:
                    pass

        return UNAV

    @metadata()
    def version(self):
        """Return version of stream."""
        if self.mimetype() in ["video/MP2T", "video/mp4", "audio/mp4"]:
            return UNAP
        # mp3 "container" does not know the version, so it has to be checked
        # from the first stream
        if (self.mimetype() == "audio/mpeg" and
                self._stream.track_type == "General" and
                len(self._tracks) >= 2):
            return six.text_type(self._tracks[1].format_version)[-1]

        if self._stream.format_version is not None:
            return six.text_type(self._stream.format_version)[-1]
        return UNAV


class MpegPSMediainfoMeta(MpegMediainfoMeta):
    """Scraper for MPEG Program Stream video and audio."""

    # Supported mimetypes
    _supported = {"video/mpeg": ["1", "2"], "audio/mpeg": ["1", "2"],
                  "video/MP1S": [""], "video/MP2P": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["MPEG-PS"]
    _mime_dict = {"MPEG Video": "video/mpeg",
                  "MPEG Audio": "audio/mpeg"}

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        try:
            return self._mime_dict[self.codec_name()]
        except SkipElementException:
            pass
        except KeyError:
            for track in self._tracks:
                try:
                    if track.track_type == "Video":
                        if self.codec_name() == "MPEG-PS":
                            if track.format_version == "Version 2":
                                return "video/MP2P"
                            if track.format_version == "Version 1":
                                return "video/MP1S"
                except SkipElementException:
                    pass

        return UNAV

    @metadata()
    def version(self):
        """Return version of stream."""
        if self.mimetype() in ["video/MP2P", "video/MP1S"]:
            return UNAP

        return super(MpegPSMediainfoMeta, self).version()
