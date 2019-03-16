"""Metadata scraper for AV files"""
from file_scraper.mediainfo_base import Mediainfo
from file_scraper.base import SkipElement


class VideoMediainfo(Mediainfo):
    """Scraper for various video and audio formats
    """
    # Supported mimetypes
    _supported = {'video/quicktime': [''], 'video/x-ms-asf': [''],
                  'video/avi': ['']}
    _allow_versions = True  # Allow any version

    def _s_mimetype(self):
        """Return mimetype
        """
        mime_dict = {'DV': 'video/dv',
                     'PCM': 'audio/x-wav',
                     'AIFF': 'audio/x-aiff',
                     'AIFC': 'audio/x-aiff',
                     'AAC': 'audio/mp4',
                     'AVC': 'video/mp4',
                     'MPEG Video': 'video/mpeg',
                     'MPEG Audio': 'audio/mpeg',
                     'FLAC': 'audio/flac',
                     'WMA': 'audio/x-ms-wma',
                     'WMV': 'audio/x-ms-wmv',
                     'FFV1': 'video/x-ffv'}
        if self._s_codec_name() in mime_dict:
            return mime_dict[self._s_codec_name()]
        else:
            return self.mimetype


class MpegMediainfo(Mediainfo):
    """Scraper for MPEG video and audio
    """
    # Supported mimetypes
    _supported = {'video/mpeg': ['1', '2'], 'video/mp4': [''],
                  'audio/mpeg': ['1', '2'], 'audio/mp4': ['']}
    _allow_versions = True  # Allow any version

    # pylint: disable=no-self-use
    def _s_signal_format(self):
        """Returns signal format
        """
        if self._s_stream_type() not in [None, 'video']:
            return SkipElement
        return '(:unap)'

    def _s_codec_quality(self):
        """Returns codec quality
        """
        if self._s_stream_type() not in [None, 'video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.compression_mode is not None:
            return self._mediainfo_stream.compression_mode.lower()
        return 'lossy'

    def _s_data_rate_mode(self):
        """Returns data rate mode. Must be resolved
        """
        if self._s_stream_type() not in ['video', 'audio']:
            return SkipElement
        if self._mediainfo_stream.bit_rate_mode == 'CBR':
            return 'Fixed'
        return 'Variable'

    def _s_mimetype(self):
        """Returns mimetype for stream
        """
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
        if self._mediainfo_stream.format_version is not None:
            return self._mediainfo_stream.format_version[-1]
        else:
            return ''
