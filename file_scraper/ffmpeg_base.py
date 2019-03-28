"""Metadata scraper for video file formats and streams."""
import re
from fractions import Fraction

try:
    import ffmpeg
except ImportError:
    pass

from file_scraper.base import BaseScraper, SkipElement
from file_scraper.utils import iso8601_duration, strip_zeros


class FFMpeg(BaseScraper):
    """Scraper class for collecting video and audio metadata."""

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._ffmpeg_stream = None  # Current ffprobe stream
        self._ffmpeg = None         # All ffprobe streams
        super(FFMpeg, self).__init__(filename, mimetype, check_wellformed,
                                     params)

    def scrape_file(self):
        """Scrape data from file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        try:
            self._ffmpeg = ffmpeg.probe(self.filename)
            for stream in [self._ffmpeg['format']] + self._ffmpeg['streams']:
                if 'index' not in stream:
                    stream['index'] = 0
                else:
                    stream['index'] = stream['index'] + 1
            self.set_tool_stream(0)
        except self._ffmpeg.Error as err:
            self.errors('Error in analyzing file.')
            self.errors(err.stderr)
        else:
            self.messages('The file was analyzed successfully.')
        finally:
            self._check_supported()
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """
        Iterate streams of give stream type.

        :stream_type: Stream type, e.g. 'audio', 'video', 'videocontainer'
        """
        if self._ffmpeg is None:
            yield {}
        else:
            if stream_type == 'videocontainer':
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
        """
        Set stream of given index.

        :index: Stream index
        """
        if self._ffmpeg is not None:
            if index == 0:
                self._ffmpeg_stream = self._ffmpeg['format']
                return
            for stream in self._ffmpeg['streams']:
                if stream['index'] == index:
                    self._ffmpeg_stream = stream
                    return

    def _hascontainer(self):
        """Check if file has a video container."""
        if self._ffmpeg is None:
            return False
        if 'codec_type' not in self._ffmpeg['format']:
            return True
        return False

    def _s_version(self):
        """Return version of stream."""
        return None

    def _s_codec_quality(self):
        """
        Returns codec quality.

        Must be resolved, if returns None. Only values 'lossy' and 'lossless'
        are allowed.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        return None

    def _s_data_rate_mode(self):
        """
        Return data rate mode.

        Must be resolved, if returns None. Only values 'Fixed' or 'Variable'
        are allowed.
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        return None

    def _s_signal_format(self):
        """Return signal format."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        return '(:unav)'

    def _s_stream_type(self):
        """Return stream type."""
        if self._ffmpeg is None:
            return None
        if 'codec_type' not in self._ffmpeg_stream and \
                self._s_index() > 0:
            return 'other'
        if self._hascontainer() and self._s_index() == 0:
            return 'videocontainer'
        return self._ffmpeg_stream['codec_type']

    def _s_index(self):
        """Return stream index."""
        if self._ffmpeg is None:
            return 0
        if 'index' not in self._ffmpeg_stream:
            return 0
        return self._ffmpeg_stream['index']

    def _s_color(self):
        """
        Return color information.

        Only values from fixed list are allowed. Must be resolved, if returns
        None.
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'pix_fmt' in self._ffmpeg_stream:
            if self._ffmpeg_stream["pix_fmt"] in ["gray"]:
                return "Grayscale"
            if self._ffmpeg_stream["pix_fmt"] in ["monob", "monow"]:
                return "B&W"
            return 'Color'
        return None

    def _s_width(self):
        """Return frame width."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'width' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['width'])
        return '(:unav)'

    def _s_height(self):
        """Return frame height."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'height' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['height'])
        return '(:unav)'

    def _s_par(self):
        """Return pixel aspect ratio."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'sample_aspect_ratio' in self._ffmpeg_stream:
            return strip_zeros("%.2f" % float(Fraction(
                self._ffmpeg_stream['sample_aspect_ratio'].replace(':', '/'))))

        return '(:unav)'

    def _s_dar(self):
        """Return display aspect ratio."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'display_aspect_ratio' in self._ffmpeg_stream:
            return strip_zeros("%.2f" % float(Fraction(
                self._ffmpeg_stream['display_aspect_ratio'].replace(
                    ':', '/'))))
        return '(:unav)'

    def _s_data_rate(self):
        """Return data rate (bit rate)."""
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'bit_rate' in self._ffmpeg_stream:
            if self._ffmpeg_stream['codec_type'] == 'video':
                return strip_zeros(str(float(
                    self._ffmpeg_stream['bit_rate'])/1000000))
            else:
                return strip_zeros(str(float(
                    self._ffmpeg_stream['bit_rate'])/1000))
        return '(:unav)'

    def _s_frame_rate(self):
        """Return frame rate."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'r_frame_rate' in self._ffmpeg_stream:
            return self._ffmpeg_stream['r_frame_rate'].split('/')[0]
        return '(:unav)'

    def _s_sampling(self):
        """Return chroma subsampling method."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        sampling = "(:unav)"
        if 'pix_fmt' in self._ffmpeg_stream:
            for sampling_code in ["444", "422", "420", "440", "411", "410"]:
                if sampling_code in self._ffmpeg_stream["pix_fmt"]:
                    sampling = ":".join(sampling_code)
                    break
        return sampling

    def _s_sound(self):
        """Return 'Yes' if sound channels are present, otherwise 'No'."""
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        for stream in self._ffmpeg["streams"]:
            if stream['codec_type'] == 'audio':
                return 'Yes'
        return 'No'

    def _s_audio_data_encoding(self):
        """Return audio data encoding."""
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'codec_long_name' in self._ffmpeg_stream:
            return self._ffmpeg_stream['codec_long_name'].split(' ')[0]
        return '(:unav)'

    def _s_sampling_frequency(self):
        """Return sampling frequency."""
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'sample_rate' in self._ffmpeg_stream:
            return strip_zeros(str(float(
                self._ffmpeg_stream['sample_rate'])/1000))
        return '(:unav)'

    def _s_num_channels(self):
        """Return number of channels."""
        if self._s_stream_type() not in ['audio']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'channels' in self._ffmpeg_stream:
            return str(self._ffmpeg_stream['channels'])
        return '(:unav)'

    def _s_codec_creator_app(self):
        """Return creator application."""
        if self._s_stream_type() not in [
                'audio', 'video', 'videocontainer']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'encoder' in self._ffmpeg['format']:
            return self._ffmpeg['format']['encoder']
        return '(:unav)'

    def _s_codec_creator_app_version(self):
        """Return creator application version."""
        if self._s_stream_type() not in [
                'audio', 'video', 'videocontainer']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'encoder' in self._ffmpeg['format']:
            reg = re.search(r'([\d.]+)$',
                            self._ffmpeg['format']['encoder'])
            if reg is not None:
                return reg.group(1)
        return '(:unav)'

    def _s_codec_name(self):
        """Return codec name."""
        if self._s_stream_type() not in [
                'audio', 'video', 'videocontainer']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'codec_long_name' in self._ffmpeg_stream:
            return self._ffmpeg_stream['codec_long_name']
        return '(:unav)'

    def _s_duration(self):
        """Return duration."""
        if self._s_stream_type() not in ['audio', 'video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'duration' in self._ffmpeg_stream:
            return iso8601_duration(float(self._ffmpeg_stream['duration']))
        return '(:unav)'

    def _s_bits_per_sample(self):
        """Return bits per sample."""
        if self._s_stream_type() not in ['audio', 'video']:
            return SkipElement
        if self._ffmpeg is None:
            return None
        if 'bits_per_raw_sample' in self._ffmpeg_stream is not None:
            return str(self._ffmpeg_stream['bits_per_raw_sample'])
        return '(:unav)'
