"""Metadata scraper for AV files."""
from file_scraper.mediainfo_base import Mediainfo
from file_scraper.base import SkipElementException
from file_scraper.utils import metadata


class WavMediainfo(Mediainfo):
    """Scraper for WAV audio."""

    _supported = {'audio/x-wav': ['2', '']}
    _allow_versions = True  # Allow any version

    @metadata()
    def _s_version(self):
        """Return version."""
        if self._mediainfo is None:
            return None
        if self._s_stream_type() != 'audio':
            return None
        if self._mediainfo.tracks[0].bext_present is not None \
                and self._mediainfo.tracks[0].bext_present == 'Yes':
            return '2'
        return ''

    @metadata()
    def _s_codec_quality(self):
        """Return codec quality."""
        if self._s_stream_type() == 'audio':
            return 'lossless'
        raise SkipElementException()


class MpegMediainfo(Mediainfo):
    """Scraper for MPEG video and audio."""

    # Supported mimetypes
    _supported = {'video/mpeg': ['1', '2'], 'video/mp4': [''],
                  'audio/mpeg': ['1', '2'], 'audio/mp4': [''],
                  'video/MP1S': [''], 'video/MP2P': [''],
                  'video/MP2T': ['']}
    _allow_versions = True  # Allow any version
    _containers = ['MPEG-TS', 'MPEG-PS', 'MPEG-4']

    @metadata()
    def _s_signal_format(self):
        """Return signal format."""
        if self._s_stream_type() not in ['video']:
            raise SkipElementException()
        if self._mediainfo is None:
            return None
        return '(:unap)'

    @metadata()
    def _s_codec_quality(self):
        """Return codec quality."""
        if self._s_stream_type() not in ['video', 'audio']:
            raise SkipElementException()
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.compression_mode is not None:
            return self._mediainfo_stream.compression_mode.lower()
        return 'lossy'

    @metadata()
    def _s_data_rate_mode(self):
        """Return data rate mode. Must be resolved."""
        if self._s_stream_type() not in ['video', 'audio']:
            raise SkipElementException()
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.bit_rate_mode == 'CBR':
            return 'Fixed'
        return 'Variable'

    @metadata()
    def _s_mimetype(self):
        """Return mimetype for stream."""
        if self._mediainfo is None:
            return self.mimetype
        mime_dict = {'AAC': 'audio/mp4',
                     'AVC': 'video/mp4',
                     'MPEG-4': 'video/mp4',
                     'MPEG Video': 'video/mpeg',
                     'MPEG Audio': 'audio/mpeg'}

        try:
            return mime_dict[self._s_codec_name()]
        except (SkipElementException, KeyError):
            pass
        return self.mimetype

    @metadata()
    def _s_version(self):
        """Return version of stream."""
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.format_version is not None:
            return str(self._mediainfo_stream.format_version)[-1]
        if self._s_stream_type() in ['videocontainer', 'video', 'audio']:
            return ''
        return None
