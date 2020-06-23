"""Metadata scraper for AV files."""
from __future__ import unicode_literals

import re
import six

from file_scraper.base import BaseMeta
from file_scraper.exceptions import SkipElementException
from file_scraper.utils import iso8601_duration, strip_zeros, metadata


class BaseMediainfoMeta(BaseMeta):
    """Metadata models for files scraped using MediainfoScraper"""
    # pylint: disable=too-many-public-methods

    _containers = []
    container_stream = None

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
    def version(self):
        """Return version of stream."""
        if self._stream.format_version is not None:
            return self._stream.format_version.replace("Version ", "")
        return "(:unav)"

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
        return "(:unav)"

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.standard is not None:
            return self._stream.standard
        return "(:unav)"

    @metadata()
    def width(self):
        """Return frame width."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.width is not None:
            return six.text_type(self._stream.width)
        return "(:unav)"

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.height is not None:
            return six.text_type(self._stream.height)
        return "(:unav)"

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.pixel_aspect_ratio is not None:
            return strip_zeros(six.text_type(self._stream.pixel_aspect_ratio))
        return "(:unav)"

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.display_aspect_ratio is not None:
            return strip_zeros(six.text_type(
                self._stream.display_aspect_ratio))
        return "(:unav)"

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
        return "(:unav)"

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.frame_rate is not None:
            return strip_zeros(six.text_type(self._stream.frame_rate))
        return "(:unav)"

    @metadata()
    def sampling(self):
        """Return chroma subsampling method."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.chroma_subsampling is not None:
            return self._stream.chroma_subsampling
        return "(:unav)"

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
        return "(:unav)"

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
        return "(:unav)"

    @metadata()
    def audio_data_encoding(self):
        """Return audio data encoding."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.format is not None:
            return six.text_type(self._stream.format)
        return "(:unav)"

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.sampling_rate is not None:
            return strip_zeros(six.text_type(float(
                self._stream.sampling_rate)/1000))
        return "(:unav)"

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.channel_s is not None:
            return six.text_type(self._stream.channel_s)
        return "(:unav)"

    @metadata()
    def codec_creator_app(self):
        """Returns creator application."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._tracks[0].writing_application is not None:
            return self._tracks[0].writing_application
        return "(:unav)"

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
        return "(:unav)"

    @metadata()
    def codec_name(self):
        """Returns codec name."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._stream.format is not None:
            return self._stream.format
        return "(:unav)"

    @metadata()
    def duration(self):
        """Return duration."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.duration is not None:
            return iso8601_duration(float(
                self._stream.duration) / 1000)
        return "(:unav)"

    @metadata()
    def bits_per_sample(self):
        """Return bits per sample."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_depth is not None:
            return six.text_type(self._stream.bit_depth)
        return "(:unav)"


class MovMediainfoMeta(BaseMediainfoMeta):
    """Scraper for Quicktime Movie AV container and selected streams"""
    _supported = {"video/quicktime": [""], "video/dv": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["QuickTime"]

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        mime_dict = {"QuickTime": "video/quicktime",
                     "PCM": "audio/x-wav",
                     "DV": "video/dv",
                     "AVC": "video/mp4",
                     "AAC": "audio/mp4"}

        try:
            return mime_dict[self.codec_name()]
        except SkipElementException:
            pass
        except KeyError:
            try:
                return mime_dict[self._stream.format_profile]
            except KeyError:
                pass
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version."""
        # Quicktime container does not have different versions.
        if self.mimetype() in ["video/quicktime", "video/dv", "video/mp4",
                               "audio/mp4"]:
            return "(:unap)"
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
        return "(:unav)"

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
        if mode not in ["(:unav)", None]:
            return mode
        if self.mimetype() == "video/mp4":
            return "Variable"
        return "(:unav)"


class MkvMediainfoMeta(BaseMediainfoMeta):
    """Scraper for Matroska AV container with selected streams."""

    _supported = {"video/x-matroska": ["4"]}
    _allow_versions = True  # Allow any version
    _containers = ["Matroska"]

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        mime_dict = {"Matroska": "video/x-matroska",
                     "PCM": "audio/x-wav",
                     "FLAC": "audio/flac",
                     "FFV1": "video/x-ffv"}
        try:
            return mime_dict[self.codec_name()]
        except (SkipElementException, KeyError):
            pass
        return "(:unav)"

    @metadata()
    def version(self):
        """
        Return version of stream.

        The version number 1.2.1 of FLAC comes from PRONOM registry. This is
        actually the version number of FLAC tools containing FLAC format
        specification. This includes the latest format change and was released
        in 2007. There is no separate version numbering in FLAC format itself,
        and therefore, there is no proper way to extract it.
        """
        if self.mimetype() == "audio/flac":
            return "1.2.1"
        version = super(MkvMediainfoMeta, self).version()
        if isinstance(version, six.text_type):
            version = version.split(".")[0]
        return version

    @metadata()
    def signal_format(self):
        """Returns signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return "(:unap)"

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
        else:
            return "(:unav)"

    @metadata()
    def version(self):
        """Returns version."""
        if self._tracks[0].bext_present is not None \
                and self._tracks[0].bext_present == "Yes":
            return "2"
        return "(:unap)"

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
                  "video/MP1S": [""], "video/MP2P": [""],
                  "video/MP2T": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["MPEG-TS", "MPEG-PS", "MPEG-4"]

    @metadata()
    def signal_format(self):
        """Returns signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return "(:unap)"

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
        mime_dict = {"AAC": "audio/mp4",
                     "AVC": "video/mp4",
                     "MPEG-4": "video/mp4",
                     "MPEG Video": "video/mpeg",
                     "MPEG Audio": "audio/mpeg"}

        try:
            return mime_dict[self.codec_name()]
        except (SkipElementException, KeyError):
            for track in self._tracks:
                try:
                    if track.track_type == "Video":
                        if self.codec_name() == "MPEG-TS":
                            if track.format_version == "Version 2":
                                return "video/MP2T"
                        if self.codec_name() == "MPEG-PS":
                            if track.format_version == "Version 2":
                                return "video/MP2P"
                            if track.format_version == "Version 1":
                                return "video/MP1S"
                except SkipElementException:
                    pass
        return "(:unav)"

    @metadata()
    def version(self):
        """Return version of stream."""
        if self.mimetype() in ["video/MP2T", "video/MP2P", "video/MP1S",
                               "video/mp4", "audio/mp4"]:
            return "(:unap)"
        # mp3 "container" does not know the version, so it has to be checked
        # from the first stream
        if (self.mimetype() == "audio/mpeg" and
                self._stream.track_type == "General" and
                len(self._tracks) >= 2):
            return six.text_type(self._tracks[1].format_version)[-1]

        if self._stream.format_version is not None:
            return six.text_type(self._stream.format_version)[-1]
        return "(:unav)"


class SimpleMediainfoMeta(BaseMeta):
    """
    Metadata model for checking well-formedness without metadata scraping.

    This class is used for file types for which the metadata collection is done
    using FFMpeg. Both tools cannot currently be used simultaneously, as we do
    not have a reliable way of sorting the streams so that outputs from both
    tools could be reliably combined.
    """
    _supported = {"video/avi": []}
    _allow_versions = True  # Allow any version
    _containers = ["video/avi"]

    def __init__(self, tracks, index):
        """
        Initialize the metadata model. No extra functionality over BaseMeta.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        """
        pass

    def hascontainer(self):
        """
        No metadata is scraped, so container data is irrelevant: returns False.
        """
        # pylint: disable=no-self-use
        return False
