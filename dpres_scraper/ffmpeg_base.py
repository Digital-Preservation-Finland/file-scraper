"""Metadata scraper for video file formats and streams"""
import re
from fractions import Fraction

try:
    import ffmpeg
except ImportError:
    pass

from dpres_scraper.base import BaseScraper
from dpres_scraper.utils import iso8601_duration, strip_zeros


class FFMpeg(BaseScraper):
    """Scraper class for collecting video metadata
    """

    _only_wellformed = True

    def __init__(self, mimetype, filename, validation):
        """Initialize scraper
        """
        self._ffmpeg_stream = None
        self._ffmpeg = None
        super(FFMpeg, self).__init__(mimetype, filename, validation)

    def scrape_file(self):
        """Scrape data from file
        """
        try:
            self._ffmpeg = ffmpeg.probe(self.filename)
            for stream in [self._ffmpeg['format']] + self._ffmpeg['streams']:
                if not 'index' in stream:
                    stream['index'] = 0
                else:
                    stream['index'] = stream['index'] + 1
            self.set_tool_stream(0)
        except self._ffmpeg.Error as err:
            if self.mimetype == 'application/octet-stream':
                self.messages('Was not an audio/video file, '
                              'skipping scraper...')
            else:
                self.errors('Error in scraping file.')
                self.errors(err.stderr)
        else:
            self.messages('The file was scraped.')
        finally:
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """Iterate streams
        """
        if stream_type == 'container':
            self.set_tool_stream(0)
            yield self._ffmpeg['format']
        for stream in [self._ffmpeg['format']] + self._ffmpeg['streams']:
            if stream_type is None:
                self.set_tool_stream(stream['index'])
                yield stream
            else:
                if 'codec_type' in stream and \
                        stream['codec_type'] == stream_type:
                    self.set_tool_stream(stream['index'])
                    yield stream

    def set_tool_stream(self, index):
        """Set stream with given index
        """
        if index == 0:
            self._ffmpeg_stream = self._ffmpeg['format']
            return
        for stream in self._ffmpeg['streams']:
            if stream['index'] == index:
                self._ffmpeg_stream = stream
                return

    # pylint: disable=no-self-use
    def _s_version(self):
        """Returns version of stream
        """
        return None

    # pylint: disable=no-self-use
    def _s_codec_quality(self):
        """Returns codec quality. Must be resolved, if returns None.
        Only values 'lossy' or 'lossless' are allowed.
        """
        return None

    # pylint: disable=no-self-use
    def _s_data_rate_mode(self):
        """Returns data rate mode. Must be resolved if returns None.
        Only values 'Fixed' or 'Variable' are allowed.
        """
        return None

    # pylint: disable=no-self-use
    def _s_signal_format(self):
        """Returns signal format
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        return '(:unav)'

    def _s_stream_type(self):
        """Return stream type
        """
        if not 'codec_type' in self._ffmpeg_stream:
            if self._s_index() == 0:
                return 'container'
            else:
                return 'other'
        return self._ffmpeg_stream['codec_type']

    def _s_index(self):
        """Return stream index
        """
        if not 'index' in self._ffmpeg_stream:
            return 0
        return self._ffmpeg_stream['index']

    def _s_color(self):
        """Returns color information. Only values from fixed list are
        allowed. Must be resolved, if returns None.
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'pix_fmt' in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray"]:
                return "Grayscale"
            elif self._ffmpeg_stream["pix_fmt"] in ["monob", "monow"]:
                return "B&W"
            else:
                return 'Color'
        return None

    def _s_width(self):
        """Returns frame width
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'width' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['width'])
        return '0'

    def _s_height(self):
        """Returns frame height
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'height' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['height'])
        return '0'

    def _s_par(self):
        """Returns pixel aspect ratio
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'sample_aspect_ratio' in self._ffmpeg_stream:
            return strip_zeros("%.2f" % float(Fraction(
                self._ffmpeg_stream['sample_aspect_ratio'].replace(':', '/'))))

        return '0'

    def _s_dar(self):
        """Returns display aspect ratio
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'display_aspect_ratio' in self._ffmpeg_stream:
            return strip_zeros("%.2f" % float(Fraction(
                self._ffmpeg_stream['display_aspect_ratio'].replace(
                    ':', '/'))))
        return '(:unav)'

    def _s_data_rate(self):
        """Returns data rate (bit rate)
        """
        if self._s_stream_type() not in [None, 'video', 'audio']:
            return None
        if 'bit_rate' in self._ffmpeg_stream:
            if self._ffmpeg_stream['codec_type'] == 'video':
                return strip_zeros(str(float(
                    self._ffmpeg_stream['bit_rate'])/1000000))
            else:
                return strip_zeros(str(float(
                    self._ffmpeg_stream['bit_rate'])/1000))
        return '0'

    def _s_frame_rate(self):
        """Returns frame rate
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        if 'r_frame_rate' in self._ffmpeg_stream:
            return self._ffmpeg_stream['r_frame_rate'].split('/')[0]
        return '0'

    def _s_sampling(self):
        """Returns chroma subsampling method
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        sampling = "(:unav)"
        if 'pix_fmt' in self._ffmpeg_stream:
            for sampling_code in ["444", "422", "420", "440", "411", "410"]:
                if sampling_code in self._ffmpeg_stream["pix_fmt"]:
                    sampling = ":".join(sampling_code)
                    break
        return sampling

    def _s_sound(self):
        """Returns 'Yes' if sound channels are present, otherwise 'No'
        """
        if self._s_stream_type() not in [None, 'video']:
            return None
        for stream in self._ffmpeg["streams"]:
            if stream['codec_type'] == 'audio':
                return 'Yes'
        return 'No'

    def _s_audio_data_encoding(self):
        """Returns audio data encoding
        """
        if self._s_stream_type() not in [None, 'audio']:
            return None
        if 'codec_long_name' in self._ffmpeg_stream:
            return self._ffmpeg_stream['codec_long_name'].split(' ')[0]
        return '(:unav)'

    def _s_sampling_frequency(self):
        """Returns sampling frequency
        """
        if self._s_stream_type() not in [None, 'audio']:
            return None
        if 'sample_rate' in self._ffmpeg_stream:
            return strip_zeros(str(float(
                self._ffmpeg_stream['sample_rate'])/1000))
        return '0'

    def _s_num_channels(self):
        """Returns number of channels
        """
        if self._s_stream_type() not in [None, 'audio']:
            return None
        if 'channels' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['channels'])
        return '(:unav)'

    def _s_codec_creator_app(self):
        """Returns creator application
        """
        if self._s_stream_type() not in [None, 'audio', 'video', 'container']:
            return None
        if 'encoder' in self._ffmpeg['format']:
            return self._ffmpeg['format']['encoder']
        return '(:unav)'

    def _s_codec_creator_app_version(self):
        """Returns creator application version
        """
        if self._s_stream_type() not in [None, 'audio', 'video', 'container']:
            return None
        if 'encoder' in self._ffmpeg['format']:
            reg = re.search(r'([\d.]+)$',
                            self._ffmpeg['format']['encoder'])
            if reg is not None:
                return reg.group(1)
        return '(:unav)'

    def _s_codec_name(self):
        """Returns codec name
        """
        if self._s_stream_type() not in [None, 'audio', 'video', 'container']:
            return None
        if 'codec_long_name' in self._ffmpeg_stream:
            return self._ffmpeg_stream['codec_long_name']
        return '(:unav)'

    def _s_duration(self):
        """Returns duration
        """
        if self._s_stream_type() not in [None, 'audio', 'video']:
            return None
        if 'duration' in self._ffmpeg_stream:
            return iso8601_duration(float(self._ffmpeg_stream['duration']))
        return '(:unav)'

    def _s_bits_per_sample(self):
        """Returns bits per sample
        """
        if self._s_stream_type() not in [None, 'audio', 'video']:
            return None
        if 'bits_per_raw_sample' in self._ffmpeg_stream is not None:
            return str(self._ffmpeg_stream['bits_per_raw_sample'])
        return '0'
