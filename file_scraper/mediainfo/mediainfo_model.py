"""Metadata extractor for AV files."""

import re

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.exceptions import SkipElementException
import file_scraper.mediainfo
from file_scraper.utils import iso8601_duration, strip_zeros
from file_scraper.metadata import metadata


class BaseMediainfoMeta(BaseMeta):
    # pylint: disable=too-many-public-methods
    """Metadata models for streams scraped using MediainfoExtractor."""

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

        if self._stream.track_type == "Image":
            return 'image'

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
            return str(self._stream.width)
        return UNAV

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.height is not None:
            return str(self._stream.height)
        return UNAV

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.pixel_aspect_ratio is not None:
            return strip_zeros(str(self._stream.pixel_aspect_ratio))
        return UNAV

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.display_aspect_ratio is not None:
            return strip_zeros(str(
                self._stream.display_aspect_ratio))
        return UNAV

    @metadata()
    def data_rate(self):
        """Return data rate (bit rate)."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.bit_rate is not None:
            if self._stream.track_type == "Video":
                return strip_zeros(str(float(
                    self._stream.bit_rate) / 1000000))
            return strip_zeros(str(float(
                self._stream.bit_rate)/1000))
        return UNAV

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.frame_rate is not None:
            return strip_zeros(str(self._stream.frame_rate))
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
            return str(self._stream.format)
        return UNAV

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.sampling_rate is not None:
            return strip_zeros(str(float(
                self._stream.sampling_rate)/1000))
        return UNAV

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.channel_s is not None:
            return str(self._stream.channel_s)
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
            return str(self._stream.bit_depth)
        return UNAV


class ContainerMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for container streams."""

    _supported = {"audio/mp4": [""],
                  "video/avi": [""],
                  "video/mp1s": [""],
                  "video/mp2p": [""],
                  "video/mp2t": [""],
                  "video/mp4": [""],
                  "video/quicktime": [""],
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
        version = super().version()
        if isinstance(version, str):
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
        version = super().version()
        if isinstance(version, str):
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

    _supported = {"audio/l8": [""],
                  "audio/l16": [""],
                  "audio/l20": [""],
                  "audio/l24": [""]}
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
        super().__init__(tracks, index)
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
        mode = super().data_rate_mode()
        if mode not in [UNAV, None]:
            return mode

        # Overall data rate mode is reported in the container stream.
        # It can be used if the file contains max. two tracks (General
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
        mode = super().data_rate_mode()
        if mode not in [UNAV, None]:
            return mode

        # Overall bit rate mode is reported in the container stream
        # It can be used if the file contains max. two tracks (General
        # + Video)
        if len(self._tracks) <= 2:
            if self._tracks[0].overall_bit_rate_mode == "CBR":
                return "Fixed"
            if self._tracks[0].overall_bit_rate_mode is not None:
                return "Variable"
        return UNAV

    @metadata()
    def color(self):
        """Return color information.

        WMV files are by default based on the YUV 4:2:0 color
        sampling.

        NOTE: FFMpeg can detect the color in the "pix_fmt" metadata.
        However, combining MediaInfo and FFMpeg is difficult and since
        WMV files are by default in color, we can just use it as a
        default value if no other value is found.
        """
        mode = super().color()
        if mode not in [UNAV, None]:
            return mode

        return "Color"


class FlacMediainfoMeta(BaseMediainfoMeta):
    """Metadata model for FLAC audio."""

    _supported = {"audio/flac": [""]}
    _allow_versions = True  # Allow any version

    def __init__(self, tracks, index):
        """Initialize the metadata model.

        FLAC is a special container format. If the file is a FLAC audio
        file, no distinction between container and soundtrack needs to
        be made, as both are treated as one in the DPS. However, FLAC
        audio can also exist as a stream in a separate video container
        file and must be treated as a separate audio stream in these
        cases.
        """
        super().__init__(tracks, index)
        if self._tracks[0].format == 'FLAC':
            self._container = None

    @metadata()
    def version(self):
        """Return version of stream.

        The PRONOM registry reports the version number of FLAC as 1.2.1.
        This is actually the version number of FLAC tools containing the
        FLAC format specification. Although the latest FLAC tools
        version is 1.3.3, version 1.2.1 still includes the latest format
        change and was released in 2007.

        FLAC is standardized in RFC 9639 without a file format version
        information, so the version will be mapped to (:unap).
        """
        return UNAP


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
        super().__init__(tracks, index)
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
    """Metadata model for MPEG data streams."""

    # Supported mimetypes
    _supported = {"audio/mpeg": ["1", "2"],
                  "audio/aac": [""],
                  "video/mpeg": ["1", "2"],
                  "video/h264": [""],
                  "video/h265": [""]}
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

        MPEG-4 and MPEG-H video (i.e. AVC and HEVC) are assumed to always have
        variable bit rate, based on e.g.
        https://slhck.info/video/2017/03/01/rate-control.html claiming
        that they do not support NAL stuffing and thus they cannot be
        forced to have constant bit rate.
        """
        mode = super().data_rate_mode()
        if mode not in [UNAV, None]:
            return mode
        if self._stream.bit_rate_mode == "CBR":
            return "Fixed"
        return "Variable"

    @metadata()
    def version(self):
        """Return version of stream.

        MPEG-4 (i.e. AVC and AAC) and MPEG-H (i.e. HEVC) streams do not have
        version, and therefore the result is unapplicable (:unap).

        MP3 "container" does not know the version, so it has to be
        checked from the first stream.
        """
        if self.mimetype() in ["audio/aac", "video/h264", "video/h265"]:
            return UNAP

        if (self.mimetype() == "audio/mpeg" and
                self._stream.track_type == "General" and
                len(self._tracks) >= 2):
            return str(self._tracks[1].format_version)[-1]

        if self._stream.format_version is not None:
            return str(self._stream.format_version)[-1]
        return UNAV


class VersionlessFormatMeta(BaseMediainfoMeta):
    """Generic metadata model for stream formats, which do not have a version.
    """

    _supported = {"video/x.fi-dpres.prores": [""],
                  "audio/ac3": [""]}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version of stream.

        Result is always unapplicable (:unap), because these formats do not
        have a version.
        """
        return UNAP


class ImageMediaInfoMeta(BaseMediainfoMeta):
    """
    Very simple metadata model for images, Mediainfo extractor needs to know
    images that exist in containers, but more precise metadata can be gathered
    with other extractors
    """
    _supported = {"image/jpeg": [""], "image/png": [""]}
    _allow_versions = True


class UnknownStreamFormatMeta(BaseMediainfoMeta):
    """Metadata model for streams that were not detected."""

    _supported = {None: [""]}
    _allow_versions = True  # Allow any version
