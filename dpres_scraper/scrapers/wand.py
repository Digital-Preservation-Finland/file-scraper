"""Metadata scraper for image file formats"""
from dpres_scraper.wand_base import Wand


class TiffWand(Wand):
    """Collect TIFF image metadata
    """

    _supported = {'image/tiff': []}

    def _s_byte_order(self):
        """Returns byte order
        """
        for key, value in self._wand.metadata.items():
            if key.startswith('tiff:endian'):
                if value == 'msb':
                    return 'big endian'
                else:
                    return 'little endian'


class ImageWand(Wand):
    """Collect image metadata
    """

    _supported = {'image/png': [], 'image/jpeg': [], 'image/jp2': [],
                  'image/gif': [], 'image/x-dpx': []}
