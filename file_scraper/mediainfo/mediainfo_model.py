"""Metadata scraper for AV files."""
from __future__ import unicode_literals

import re
import six

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.exceptions import SkipElementException
import file_scraper.mediainfo
from file_scraper.utils import iso8601_duration, strip_zeros, metadata


class BaseMediainfoMeta(BaseMeta):
    # pylint: disable=too-many-public-methods
    """Metadata models for streams scraped using MediainfoScraper."""

    def __init__(self, tracks, index):
        """
        Initialize the metadata model.

        :tracks: list of all tracks in the file
        :index: index of the track represented by this metadata model
        """
        self._stream = tracks[index]
        self._tracks = tracks
        self._track_index = index

        # Find out if file is a video container
        if len(self._tracks) > 2 or tracks[0].format != tracks[1].format:
            self._container = tracks[0]
        else:
            self._container = None

    @metadata()
    def mimetype(self):
        """Return mimetype for stream."""
        return file_scraper.mediainfo.track_mimetype(self._stream) or UNAV

    @metadata()
    def version(self):
        """Return version of stream."""
        if self._stream.format_version is not None:
            return self._stream.format_version.replace("Version ", "")
        return UNAV

    @metadata()
    def stream_type(self):
        """Return stream type."""
        if self._container and self._stream == self._container:
            return "videocontainer"

        if self._stream.track_type == "Audio":
            return 'audio'

        if self._stream.track_type == "Video":
            return 'video'

        # For example "General" tracks are not streams, unless they are
        # videocontainers
        return None

    @metadata()
    def index(self):
        """Return stream index."""
        if self._container:
            return self._track_index

        # Since file is not a container, the first track is not a
        # stream. It is just general information that is skipped.
        return self._track_index - 1

    @metadata()
    def color(self):
        """
        Return color information.

        Only values from fixed list are allowed. Must be resolved, if
        returns None.
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

        Must be resolved, if returns None. Only values "lossy" or
        "lossless" are allowed.
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

        Must be resolved, if returns None. The allowed values are
        "Fixed" and "Variable".
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
        """Return creator application."""
        if self.stream_type() not in ["video", "audio", "videocontainer"]:
            raise SkipElementException()
        if self._tracks[0].writing_application is not None:
            return self._tracks[0].writing_application
        return UNAV

    @metadata()
    def codec_creator_app_version(self):
        """Return creator application version."""
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
        """Return codec name."""
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


class ContainerMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for container streams."""

    _supported = {"video/quicktime": [""],
                  "video/MP1S": [""],
                  "video/MP2P": [""],
                  "video/MP2T": [""],
                  "video/avi": [""],
                  "video/x-ms-asf": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        Container streams do not have version, and therefore the result
        is unapplicable (:unap).
        """
        return UNAP


class MkvMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for Matroska AV container."""

    _supported = {"video/x-matroska": ["4"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream."""
        version = super(MkvMediainfoMeta, self).version()
        if isinstance(version, six.text_type):
            version = version.split(".")[0]
        return version


class FfvMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for FF Video Codec 1."""

    _supported = {"video/x-ffv": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def signal_format(self):
        """Return signal format."""
        return UNAP

    @metadata()
    def version(self):
        """Return version of stream."""
        version = super(FfvMediainfoMeta, self).version()
        if isinstance(version, six.text_type):
            version = version.split(".")[0]
        return version


class DvMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for Digital Video."""

    _supported = {"video/dv": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        DV streams do not have version, and therefore the result is
        unapplicable (:unap).
        """
        return UNAP


class LpcmMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for Linear Pulse-Code Modulation audio."""

    _supported = {"audio/L8": [""],
                  "audio/L16": [""],
                  "audio/L20": [""],
                  "audio/L24": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        PCM audio streams (i.e. audio/L*) do not have version, and
        therefore the result is unapplicable (:unap).
        """
        return UNAP

    @metadata()
    def codec_quality(self):
        """Return codec quality."""
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()

        return "lossless"


class AiffMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for AIFF audio."""

    _supported = {"audio/x-aiff": ["", "1.3"]}
    _allow_versions = True  # Allow any version

    def __init__(self, tracks, index):
        """Initialize the metadata model.

        AIFF is a special container format. For AIFF files, no
        distinction between container and soundtrack needs to be made,
        as both are treated as one in the DPS.
        """
        super(AiffMediainfoMeta, self).__init__(tracks, index)
        self._container = None

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return 'audio/x-aiff'

    @metadata()
    def codec_name(self):
        """Return codec name.

        The codec name for AIFF-C files is ready from the codec_id
        key. AIFF files should have PCM in the format key.
        """
        if self._stream.codec_id is not None:
            return self._stream.codec_id.lower()

        if self._stream.format is not None:
            return self._stream.format

        return UNAV

    @metadata()
    def codec_quality(self):
        """Return codec quality.

        AIFF-C can contain lossless or lossy compression. We'll set the
        codec quality based on the codec ID.
        """
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()

        if self._stream.codec_id is not None:
            if self._stream.codec_id not in [
                    "raw", "twos", "swot", "fl32", "fl64", "in24", "in32"]:
                return "lossy"

        return "lossless"


class WmaMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for WMA audio."""

    _supported = {"audio/x-ms-wma": ["9"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return 'audio/x-ms-wma'

    @metadata()
    def version(self):
        """Return version of stream."""
        if any((self._stream.description_of_the_codec is not None and
                self._stream.description_of_the_codec == 'wmav1',
                self._stream.format_version is not None and
                self._stream.format_version == 'Version 1')):
            return "7"
        if any((self._stream.description_of_the_codec is not None and
                self._stream.description_of_the_codec == 'wmav2',
                self._stream.format_version is not None and
                self._stream.format_version == 'Version 2')):
            return "8"
        if any((self._stream.description_of_the_codec is not None and
                self._stream.description_of_the_codec in ['wmav3', 'wmapro'],
                self._stream.format_profile is not None and
                self._stream.format_profile in ['Pro', 'Lossless'])):
            return "9"
        return UNAV

    @metadata()
    def codec_quality(self):
        """Return codec quality.

        Most common WMA codecs are lossy, but some WMA files can use
        the Windows Media Audio Lossless codec.
        """
        if any((self._stream.codec_id_info is not None
                and "Lossless" in self._stream.codec_id_info,
                self._stream.format_profile is not None
                and "Lossless" in self._stream.format_profile)):
            return "lossless"
        return "lossy"

    @metadata()
    def data_rate_mode(self):
        """Return data rate mode.

        WMA supports both fixed and variable bit rates. Variable
        bit rate mode was officially introduced in WMA9.
        """
        mode = super(WmaMediainfoMeta, self).data_rate_mode()
        if mode not in [UNAV, None]:
            return mode

        # Overall data rate mode is reported in the container stream.
        # If can be used if the file contains max. two tracks (General
        # + Audio)
        if len(self._tracks) <= 2:
            if self._tracks[0].overall_bit_rate_mode == "CBR":
                return "Fixed"
            if self._tracks[0].overall_bit_rate_mode is not None:
                return "Variable"
        return UNAV


class WmvMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for WMV video."""

    _supported = {"video/x-ms-wmv": ["9"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return 'video/x-ms-wmv'

    @metadata()
    def version(self):
        """Return version of stream."""
        if self._stream.codec_id is not None and \
                self._stream.codec_id == 'WMV1':
            return "7"
        if self._stream.codec_id is not None and \
                self._stream.codec_id == 'WMV2':
            return "8"
        if self._stream.codec_id is not None and \
                self._stream.codec_id in ['WVC1', 'WMV3', 'WMVA', 'WMVP']:
            return "9"
        return UNAV

    @metadata()
    def codec_quality(self):
        """Return codec quality.

        WMV codecs are lossy codecs.
        """
        return "lossy"

    @metadata()
    def signal_format(self):
        """Return signal format."""
        return UNAP

    @metadata()
    def data_rate_mode(self):
        """Return data rate mode.

        WMV supports both fixed and variable bit rates.
        """
        mode = super(WmvMediainfoMeta, self).data_rate_mode()
        if mode not in [UNAV, None]:
            return mode

        # Overall bit rate mode is reported in the container stream
        # If can be used if the file contains max. two tracks (General
        # + Video)
        if len(self._tracks) <= 2:
            if self._tracks[0].overall_bit_rate_mode == "CBR":
                return "Fixed"
            if self._tracks[0].overall_bit_rate_mode is not None:
                return "Variable"
        return UNAV


class FlacMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for FLAC audio."""

    _supported = {"audio/flac": ["1.2.1"]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        The version number 1.2.1 of FLAC comes from PRONOM registry.
        This is actually the version number of FLAC tools containing
        FLAC format specification. Although the latest FLAC tools
        version is 1.3.3, version 1.2.1 still includes the latest format
        change and was released in 2007. There is no separate version
        numbering in FLAC format itself, and therefore, there is no
        proper way to extract it.
        """
        return "1.2.1"


class WavMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for WAV audio."""

    _supported = {"audio/x-wav": ["2", ""]}
    _allow_versions = True  # Allow any version

    def __init__(self, tracks, index):
        """Initialize the metadata model.

        WAV is a special container format. For WAV files, no
        distinction between container and soundtrack needs to be made,
        as both are treated as one in the DPS.
        """
        super(WavMediainfoMeta, self).__init__(tracks, index)
        self._container = None

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return 'audio/x-wav'

    @metadata()
    def version(self):
        """Return version."""
        if self._tracks[0].bext_present is not None \
                and self._tracks[0].bext_present == "Yes":
            return "2"
        return UNAP

    @metadata()
    def codec_quality(self):
        """Return codec quality."""
        return "lossless"


class MpegMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for MPEG audio."""

    # Supported mimetypes
    _supported = {"audio/mpeg": ["1", "2"],
                  "audio/mp4": [""],
                  "video/mpeg": ["1", "2"],
                  "video/mp4": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def signal_format(self):
        """Return signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.standard is not None:
            return self._stream.standard
        return UNAP

    @metadata()
    def codec_quality(self):
        """Return codec quality."""
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        return "lossy"

    @metadata()
    def data_rate_mode(self):
        """Return data rate mode.

        MP4 is assumed to always have variable bit rate, based on e.g.
        https://slhck.info/video/2017/03/01/rate-control.html claiming
        that MP4 does not support NAL stuffing and thus it cannot be
        forced to have constant bit rate.
        """
        mode = super(MpegMediainfoMeta, self).data_rate_mode()
        if mode not in [UNAV, None]:
            return mode
        if self._stream.bit_rate_mode == "CBR":
            return "Fixed"
        return "Variable"

    @metadata()
    def version(self):
        """Return version of stream.

        MP4 streams do not have version, and and therefore the result is
        unapplicable (:unap).

        MP3 "container" does not know the version, so it has to be
        checked from the first stream.
        """
        if self.mimetype() in ["audio/mp4", "video/mp4"]:
            return UNAP

        if (self.mimetype() == "audio/mpeg" and
                self._stream.track_type == "General" and
                len(self._tracks) >= 2):
            return six.text_type(self._tracks[1].format_version)[-1]

        if self._stream.format_version is not None:
            return six.text_type(self._stream.format_version)[-1]
        return UNAV


class VersionlessFormatMeta(BaseMediainfoMeta):
    """Generic metadata model for stream formats, which do not have a version.
    """

    _supported = {"video/x.fi-dpres.prores": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        Result is always unapplicable (:unap), because these formats do not
        have a version.
        """
        return UNAP


class UnknownStreamFormatMeta(BaseMediainfoMeta):
    """Metadata model for streams that were not detected."""

    _supported = {None: [""]}
    _allow_versions = True  # Allow any version
