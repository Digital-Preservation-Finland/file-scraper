"""Metadata scraper for AV files"""
from file_scraper.mediainfo_base import Mediainfo
from file_scraper.base import SkipElement


class WavMediainfo(Mediainfo):
    """Scraper for WAV audio
    """
    _supported = {'audio/x-wav': ['2', '']}
    _allow_versions = True  # Allow any version

    def _s_version(self):
        """Returns version
        """
        if self._mediainfo is None:
            return None
        if self._s_stream_type() != 'audio':
            return None
        if self._mediainfo.tracks[0].bext_present is not None \
                and self._mediainfo.tracks[0].bext_present == 'Yes':
            return '2'
        return ''

    def _s_codec_quality(self):
        """Returns codec quality
        """
        if self._s_stream_type() == 'audio':
            return 'lossless'
        return None


class MpegMediainfo(Mediainfo):
    """Scraper for MPEG video and audio
    """
    # Supported mimetypes
    _supported = {'video/mpeg': ['1', '2'], 'video/mp4': [''],
                  'audio/mpeg': ['1', '2'], 'audio/mp4': [''],
                  'video/MP1S': [''], 'video/MP2P': [''],
                  'video/MP2T': ['']}
    _allow_versions = True  # Allow any version
    _containers = ['MPEG-TS', 'MPEG-PS', 'MPEG-4']


    # pylint: disable=no-self-use
    def _s_signal_format(self):
        """Returns signal format
        """
        if self._s_stream_type() not in ['video']:
            return SkipElement
        if self._mediainfo is None:
            return None
        return '(:unap)'

    def _s_codec_quality(self):
        """Returns codec quality
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.compression_mode is not None:
            return self._mediainfo_stream.compression_mode.lower()
        return 'lossy'

    def _s_data_rate_mode(self):
        """Returns data rate mode. Must be resolved
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.bit_rate_mode == 'CBR':
            return 'Fixed'
        return 'Variable'

    def _s_mimetype(self):
        """Returns mimetype for stream
        """
        if self._mediainfo is None:
            return self.mimetype
        mime_dict = {'AAC': 'audio/mp4',
                     'AVC': 'video/mp4',
                     'MPEG-4': 'video/mp4',
                     'MPEG Video': 'video/mpeg',
                     'MPEG Audio': 'audio/mpeg'}
        if self._s_codec_name() in mime_dict:
            return mime_dict[self._s_codec_name()]
        else:
            return self.mimetype

    def _s_version(self):
        """Returns stream version
        """
        if self._mediainfo is None:
            return None
        if self._mediainfo_stream.format_version is not None:
            return self._mediainfo_stream.format_version[-1]
        elif self.well_formed:
            return ''
        else:
            return None
