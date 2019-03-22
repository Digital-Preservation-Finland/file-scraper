"""Metadata scraper for video file formats and streams
Please note that you can not use Mediainfo with FFMpeg.
The streams are in different order, and there is no way
to fix that.
"""
import re

try:
    from pymediainfo import MediaInfo
except ImportError:
    pass

from file_scraper.base import BaseScraper, SkipElement
from file_scraper.utils import iso8601_duration, strip_zeros


class Mediainfo(BaseScraper):
    """Scraper class for collecting video and audio metadata.
    """

    _containers = []  # Container codec names

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize scraper.
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._mediainfo_index = None   # Current mediainfo stream index
        self._mediainfo_stream = None  # Current mediainfo stream
        self._mediainfo = None         # All mediainfo streams
        super(Mediainfo, self).__init__(filename, mimetype, validation,
                                        params)

    def scrape_file(self):
        """Scrape the file.
        """
        try:
            self._mediainfo = MediaInfo.parse(self.filename)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self.errors('Error in scraping file.')
            self.errors(str(e))
            self.set_tool_stream(0)
            self._check_supported()
            self._collect_elements()
            return

        for index, track in enumerate(self._mediainfo.tracks):
            if track.track_type == 'General':
                self._mediainfo.tracks.insert(
                    0, self._mediainfo.tracks.pop(index))
                break

        streamnr = 1
        for index, track in enumerate(self._mediainfo.tracks[1:]):
            if track.track_type in ['Audio', 'Video']:
                self._mediainfo.tracks.insert(
                    streamnr, self._mediainfo.tracks.pop(index + 1))
                streamnr = streamnr + 1

        truncated = False
        track_found = False
        for track in self._mediainfo.tracks:
            if track.istruncated == 'Yes':
                truncated = True
                self.errors('The file is truncated.')
            if track.track_type.lower() in ['audio', 'video']:
                track_found = True
        if not track_found:
            self.errors('No audio or video tracks found.')
        elif not truncated:
            self.messages('The file was scraped successfully.')

        self.set_tool_stream(0)
        self._check_supported()
        self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """Iterate streams of given stream type
        :stream_type: Stream type, e.g. 'audio', 'video', 'videocontainer'
        """
        if self._mediainfo is None:
            yield {}
        else:
            if self._hascontainer():
                index = 0
            else:
                index = 1
            if len(self._mediainfo.tracks) <= index:
                yield {}
            for stream in self._mediainfo.tracks[index:]:
                if stream.track_type.lower() == stream_type or \
                        stream_type is None:
                    self._mediainfo_stream = stream
                    self._mediainfo_index = index
                    yield stream
                index = index + 1

    def set_tool_stream(self, index):
        """Set stream with given index
        :index: Index of the stream
        """
        if self._mediainfo is not None:
            self._mediainfo_stream = self._mediainfo.tracks[index]
            self._mediainfo_index = index

    def _hascontainer(self):
        """Find out if file is a video container"""
        if self._mediainfo is None:
            return False
        if self._mediainfo.tracks[0].format in self._containers:
            return True
        if len(self._mediainfo.tracks) < 3:
            return False

        return True

    def _s_version(self):
        """Return version of stream.
        """
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.format_version is not None:
            return str(self._mediainfo_stream.format_version)
        elif self._s_stream_type() in ['videocontainer', 'video', 'audio']:
            return ''
        else:
            return None

    def _s_stream_type(self):
        """Return stream type
        """
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.track_type == 'General':
            if not self._hascontainer():
                return None
            return 'videocontainer'
        return self._mediainfo_stream.track_type.lower()

    def _s_index(self):
        """Return stream index
        """
        if self._mediainfo is None:
            return 0
        if self._hascontainer() or len(self._mediainfo.tracks) <= 1:
            return self._mediainfo_index

        return self._mediainfo_index - 1

    def _s_color(self):
        """Returns color information. Only values from fixed list are
        allowed. Must be resolved, if returns None.
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.color_space is not None:
            if self._mediainfo_stream.color_space in ['RGB', 'YUV']:
                return 'Color'
            elif self._mediainfo_stream.color_space in ['Y']:
                return 'Grayscale'
        return None

    def _s_signal_format(self):
        """Returns signal format
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.standard is not None:
            return self._mediainfo_stream.standard
        return '(:unav)'

    def _s_width(self):
        """Returns frame width
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.width is not None:
            return str(self._mediainfo_stream.width)
        return '0'

    def _s_height(self):
        """Returns frame height
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.height is not None:
            return str(self._mediainfo_stream.height)
        return '0'

    def _s_par(self):
        """Returns pixel aspect ratio
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.pixel_aspect_ratio is not None:
            return strip_zeros(str(self._mediainfo_stream.pixel_aspect_ratio))
        return '0'

    def _s_dar(self):
        """Returns display aspect ratio
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.display_aspect_ratio is not None:
            return strip_zeros(str(
                self._mediainfo_stream.display_aspect_ratio))
        return '(:unav)'

    def _s_data_rate(self):
        """Returns data rate (bit rate)
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.bit_rate is not None:
            # pylint: disable=no-else-return
            if self._mediainfo_stream.track_type == 'Video':
                return strip_zeros(str(float(
                    self._mediainfo_stream.bit_rate)/1000000))
            else:
                return strip_zeros(str(float(
                    self._mediainfo_stream.bit_rate)/1000))
        return '0'

    def _s_frame_rate(self):
        """Returns frame rate
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.frame_rate is not None:
            return strip_zeros(str(self._mediainfo_stream.frame_rate))
        return '0'

    def _s_sampling(self):
        """Returns chroma subsampling method
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.chroma_subsampling is not None:
            return self._mediainfo_stream.chroma_subsampling
        return '(:unav)'

    def _s_sound(self):
        """Returns 'Yes' if sound channels are present, otherwise 'No'
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo.tracks[0].count_of_audio_streams is not None \
                and int(self._mediainfo.tracks[0].count_of_audio_streams) > 0:
            return 'Yes'
        if self._mediainfo.tracks[0].audio_count is not None \
                and int(self._mediainfo.tracks[0].audio_count) > 0:
            return 'Yes'
        return 'No'

    def _s_codec_quality(self):
        """Returns codec quality. Must be resolved, if returns None.
        Only values 'lossy' or 'lossless' are allowed.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.compression_mode is not None:
            return self._mediainfo_stream.compression_mode.lower()
        return None

    def _s_data_rate_mode(self):
        """Returns data rate mode. Must be resolved, if returns None.
        The allowed values are 'Fixed' and 'Variable'.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.bit_rate_mode == 'CBR':
            return 'Fixed'
        if self._mediainfo_stream.bit_rate_mode is not None:
            return 'Variable'
        return None

    def _s_audio_data_encoding(self):
        """Returns audio data encoding
        """
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.format is not None:
            return str(self._mediainfo_stream.format)
        return '(:unav)'

    def _s_sampling_frequency(self):
        """Returns sampling frequency
        """
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.sampling_rate is not None:
            return strip_zeros(str(float(
                self._mediainfo_stream.sampling_rate)/1000))
        return '0'

    def _s_num_channels(self):
        """Returns number of channels
        """
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.channel_s is not None:
            return str(self._mediainfo_stream.channel_s)
        return '(:unav)'

    def _s_codec_creator_app(self):
        """Returns creator application
        """
        if self._s_stream_type() not in [
                'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo.tracks[0].writing_application is not None:
            return self._mediainfo.tracks[0].writing_application
        return '(:unav)'

    def _s_codec_creator_app_version(self):
        """Returns creator application version
        """
        if self._s_stream_type() not in [
                'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo.tracks[0].writing_application is not None:
            reg = re.search(r'([\d.]+)$',
                            self._mediainfo.tracks[0].writing_application)
            if reg is not None:
                return reg.group(1)
        return '(:unav)'

    def _s_codec_name(self):
        """Returns codec name
        """
        if self._s_stream_type() not in [
                'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.format is not None:
            return self._mediainfo_stream.format
        return '(:unav)'

    def _s_duration(self):
        """Returns duration
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.duration is not None:
            return iso8601_duration(float(
                self._mediainfo_stream.duration)/1000)
        return '(:unav)'

    def _s_bits_per_sample(self):
        """Returns bits per sample
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.bit_depth is not None:
            return str(self._mediainfo_stream.bit_depth)
        return '0'
