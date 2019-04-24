"""Metadata scraper for AV files."""

import re

from file_scraper.base import BaseMeta
from file_scraper.base import SkipElementException
from file_scraper.utils import iso8601_duration, strip_zeros, metadata


class BaseMediainfoMeta(BaseMeta):
    """Metadata models for files scraped using MediainfoScraper"""
    # pylint: disable=too-many-public-methods

    _containers = []
    container_stream = None

    def __init__(self, tracks, index, mimetype_guess):
        """
        Initialize the metadata model.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        :mimetype_guess: MIME type of the file. For some file types, the
                         scraper cannot determine the mimetype and this
                         value is used instead.
        """
        self._stream = tracks[index]
        self._index = index
        self._tracks = tracks
        self._mimetype_guess = mimetype_guess
        if self._hascontainer():
            self.container_stream = tracks[0]
        super(BaseMediainfoMeta, self).__init__()

    def _hascontainer(self):
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
        if self.stream_type() in ["videocontainer", "video", "audio"]:
            return ""
        return None

    @metadata()
    def stream_type(self):
        """Return stream type."""
        if self._stream.track_type == "General":
            if not self._hascontainer():
                return None
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
        return None

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
            return str(self._stream.width)
        return "(:unav)"

    @metadata()
    def height(self):
        """Return frame height."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.height is not None:
            return str(self._stream.height)
        return "(:unav)"

    @metadata()
    def par(self):
        """Return pixel aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.pixel_aspect_ratio is not None:
            return strip_zeros(str(self._stream.pixel_aspect_ratio))
        return "(:unav)"

    @metadata()
    def dar(self):
        """Return display aspect ratio."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.display_aspect_ratio is not None:
            return strip_zeros(str(
                self._stream.display_aspect_ratio))
        return "(:unav)"

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
        return "(:unav)"

    @metadata()
    def frame_rate(self):
        """Return frame rate."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        if self._stream.frame_rate is not None:
            return strip_zeros(str(self._stream.frame_rate))
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
        return None

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
        return None

    @metadata()
    def audio_data_encoding(self):
        """Return audio data encoding."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.format is not None:
            return str(self._stream.format)
        return "(:unav)"

    @metadata()
    def sampling_frequency(self):
        """Return sampling frequency."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.sampling_rate is not None:
            return strip_zeros(str(float(
                self._stream.sampling_rate)/1000))
        return "(:unav)"

    @metadata()
    def num_channels(self):
        """Return number of channels."""
        if self.stream_type() not in ["audio"]:
            raise SkipElementException()
        if self._stream.channel_s is not None:
            return str(self._stream.channel_s)
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
            return str(self._stream.bit_depth)
        return "(:unav)"


class MovMediainfoMeta(BaseMediainfoMeta):
    """Scraper for Quicktime Movie AV container and selected streams"""
    _supported = {"video/quicktime": [""], "video/dv": [""]}
    _allow_versions = True  # Allow any version
    _containers = ["QuickTime"]

    def __init__(self, tracks, index, mimetype_guess):
        """
        Initialize the metadata model.

        This subclass has its own initializer in order to allow setting
        the container_stream despite _hascontainer() method returning
        false for dv files.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        :mimetype_guess: MIME type of the file. For some file types, the
                         scraper cannot determine the mimetype and this
                         value is used instead.
        """
        super(MovMediainfoMeta, self).__init__(tracks, index, mimetype_guess)
        # TODO is this enough checking? could there be files where this would
        #      be bad? E.g. only one stream?
        if self.mimetype() == "video/dv":
            self.container_stream = tracks[0]

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        mime_dict = {"QuickTime": "video/quicktime",
                     "PCM": "audio/x-wav",
                     "DV": "video/dv"}
        try:
            return mime_dict[self.codec_name()]
        except (SkipElementException, KeyError):
            pass
        return self._mimetype_guess

    @metadata()
    def version(self):
        """Return version of stream."""
        if self.stream_type() in ["videocontainer", "video", "audio"]:
            return ""
        return None

    # pylint: disable=inconsistent-return-statements
    @metadata()
    def codec_quality(self):
        """Returns codec quality."""
        if self.stream_type() not in ["video", "audio"]:
            raise SkipElementException()
        if self._stream.compression_mode is not None:
            return self._stream.compression_mode.lower()
        if self.stream_type() == "audio":
            return "lossless"


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
                     "FFV1": "video/x-ffv"}
        try:
            return mime_dict[self.codec_name()]
        except (SkipElementException, KeyError):
            pass
        return self._mimetype_guess

    @metadata()
    def version(self):
        """Return version of stream."""
        version = super(MkvMediainfoMeta, self).version()
        if isinstance(version, str):
            return version.split(".")[0]
        return version

    @metadata()
    def signal_format(self):
        """Returns signal format."""
        if self.stream_type() not in ["video"]:
            raise SkipElementException()
        return "(:unap)"

    # pylint: disable=inconsistent-return-statements
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

    def __init__(self, tracks, index, mimetype_guess):
        """
        Initialize the metadata model.

        This subclass has its own initializer in order to allow setting
        the container_stream despite _hascontainer() method returning
        false for wav files.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        :mimetype_guess: MIME type of the file. For some file types, the
                         scraper cannot determine the mimetype and this
                         value is used instead.
        """
        super(WavMediainfoMeta, self).__init__(tracks, index, mimetype_guess)
        self.container_stream = tracks[0]

    @metadata()
    def mimetype(self):
        """Returns mimetype for stream."""
        return self._mimetype_guess  # TODO just the guess??

    @metadata()
    def version(self):
        """Returns version."""
        if self.stream_type() != "audio":
            return None
        if self._tracks[0].bext_present is not None \
                and self._tracks[0].bext_present == "Yes":
            return "2"
        return ""

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

    def __init__(self, tracks, index, mimetype_guess):
        """
        Initialize the metadata model.

        This subclass has its own initializer in order to allow setting
        the container_stream despite _hascontainer() method returning
        false for wav files.

        :tracks: list of tracks containing all tracks in the file
        :index: index of the track represented by this metadata model
        :mimetype_guess: MIME type of the file. For some file types, the
                         scraper cannot determine the mimetype and this
                         value is used instead.
        """
        super(MpegMediainfoMeta, self).__init__(tracks, index, mimetype_guess)
        # TODO ok?
        if self.mimetype() == "video/mpeg" or self.mimetype() == "audio/mpeg":
            self.container_stream = tracks[0]

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
            pass
        return self._mimetype_guess

    @metadata()
    def version(self):
        """Return version of stream.."""
        if self._stream.format_version is not None:
            return str(self._stream.format_version)[-1]
        if self.stream_type() in ["videocontainer", "video", "audio"]:
            return ""
        return None
