"""Metadata scraper for video file formats and streams"""
import re

try:
    from pymediainfo import MediaInfo
except ImportError:
    pass

from dpres_scraper.base import BaseScraper, SkipElement
from dpres_scraper.utils import iso8601_duration, strip_zeros


class Mediainfo(BaseScraper):
    """Scraper class for collecting video metadata
    """

    def __init__(self, filename, mimetype, validation=True):
        """Initialize scraper
        """
        self._mediainfo_stream = None
        self._mediainfo = None
        self._iscontainer = None
        super(Mediainfo, self).__init__(filename, mimetype, validation)

    def scrape_file(self):
        """Scrape data from file
        """
        try:
            self._mediainfo = MediaInfo.parse(self.filename)
        except:
            if self.mimetype == 'application/octet-stream':
                self.messages('Was not an audio/video file, '
                              'skipping scraper...')
            else:
                self.errors('Error in scraping file.')
        else:
            self._iscontainer = False
            for track in self._mediainfo.tracks:
                if track.track_id is not None:
                    self._iscontainer = True
                    break
            for index, track in enumerate(self._mediainfo.tracks):
                if track.track_type == 'General':
                    self._mediainfo.tracks.insert(
                        0, self._mediainfo.tracks.pop(index))
                    break
            self.messages('The file was scraped.')
        finally:
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """Iterate streams
        """
        for stream in self._mediainfo.tracks:
            if stream.track_type.lower() == stream_type or stream_type is None:
                self._mediainfo_stream = stream
                yield stream

    def set_tool_stream(self, index):
        """Set stream
        """
        found = False
        for stream in self._mediainfo.tracks:
            if stream.streamorder == str(index):
                self._mediainfo_stream = stream
                found = True
                break
        if not found:
            self._mediainfo_stream = self._mediainfo.tracks[0]

    def _s_version(self):
        """Return version of stream.
        """
        if self._mediainfo_stream.format_version is not None:
            return str(self._mediainfo_stream.format_version)
        else:
            return ''

    def _s_stream_type(self):
        """Return stream type
        """
        if self._mediainfo_stream.track_type == 'General':
            if self._iscontainer:
                return 'videocontainer'
            else:
                return None
        return self._mediainfo_stream.track_type.lower()

    def _s_index(self):
        """Return stream index
        """
        if self._mediainfo_stream.streamorder is not None:
            return int(self._mediainfo_stream.streamorder) + 1
        elif self._mediainfo_stream.track_type == 'General':
            return 0
        else:
            return 'muxed-' + str(self._mediainfo_stream.track_id)

    def _s_color(self):
        """Returns color information. Only values from fixed list are
        allowed. Must be resolved, if returns None.
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.color_space is not None:
            if self._mediainfo_stream.color_space in ['RGB', 'YUV']:
                return 'Color'
            elif self._mediainfo_stream.color_space in ['Y']:
                return 'Grayscale'
        return None

    # pylint: disable=no-self-use
    def _s_signal_format(self):
        """Returns signal format
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.standard is not None:
            return self._mediainfo_stream.standard
        return '(:unav)'

    def _s_width(self):
        """Returns frame width
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.width is not None:
            return str(self._mediainfo_stream.width)
        return '0'

    def _s_height(self):
        """Returns frame height
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.height is not None:
            return str(self._mediainfo_stream.height)
        return '0'

    def _s_par(self):
        """Returns pixel aspect ratio
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.pixel_aspect_ratio is not None:
            return strip_zeros(str(self._mediainfo_stream.pixel_aspect_ratio))
        return '0'

    def _s_dar(self):
        """Returns display aspect ratio
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.display_aspect_ratio is not None:
            return strip_zeros(str(
                self._mediainfo_stream.display_aspect_ratio))
        return '(:unav)'

    def _s_data_rate(self):
        """Returns data rate (bit rate)
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.bit_rate is not None:
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
        if self._mediainfo_stream.frame_rate is not None:
            return strip_zeros(str(self._mediainfo_stream.frame_rate))
        return '0'

    def _s_sampling(self):
        """Returns chroma subsampling method
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo_stream.chroma_subsampling is not None:
            return self._mediainfo_stream.chroma_subsampling
        return '(:unav)'

    def _s_sound(self):
        """Returns 'Yes' if sound channels are present, otherwise 'No'
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo.tracks[0].count_of_audio_streams is not None \
                and self._mediainfo.tracks[0].count_of_audio_streams > 0:
            return 'Yes'
        return 'No'

    def _s_codec_quality(self):
        """Returns codec quality. Must be resolved, if returns None.
        Only values 'lossy' or 'lossless' are allowed.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.compression_mode is not None:
            return self._mediainfo_stream.compression_mode.lower()
        return None

    def _s_data_rate_mode(self):
        """Returns data rate mode. Must be resolved, if returns None.
        The allowed values are 'Fixed' and 'Variable'.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
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
        if self._mediainfo_stream.format is not None:
            return str(self._mediainfo_stream.format)
        return '(:unav)'

    def _s_sampling_frequency(self):
        """Returns sampling frequency
        """
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._mediainfo_stream.sampling_rate is not None:
            return strip_zeros(str(float(
                self._mediainfo_stream.sampling_rate)/1000))
        return '0'

    def _s_num_channels(self):
        """Returns number of channels
        """
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._mediainfo_stream.channel_s is not None:
            return str(self._mediainfo_stream.channel_s)
        return '(:unav)'

    def _s_codec_creator_app(self):
        """Returns creator application
        """
        if self._s_stream_type() not in [None, 'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo.tracks[0].writing_application is not None:
            return self._mediainfo.tracks[0].writing_application
        return '(:unav)'

    def _s_codec_creator_app_version(self):
        """Returns creator application version
        """
        if self._s_stream_type() not in [None, 'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo.tracks[0].writing_application is not None:
            reg = re.search(r'([\d.]+)$',
                            self._mediainfo.tracks[0].writing_application)
            if reg is not None:
                return reg.group(1)
        return '(:unav)'

    def _s_codec_name(self):
        """Returns codec name
        """
        if self._s_stream_type() not in [None, 'video', 'audio', 'videocontainer']:
            return SkipElement
        if self._mediainfo_stream.format is not None:
            return self._mediainfo_stream.format
        return '(:unav)'

    def _s_duration(self):
        """Returns duration
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.duration is not None:
            return iso8601_duration(float(
                self._mediainfo_stream.duration)/1000)
        return '(:unav)'

    def _s_bits_per_sample(self):
        """Returns bits per sample
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.bit_depth is not None:
            return str(self._mediainfo_stream.bit_depth)
        return '0'
