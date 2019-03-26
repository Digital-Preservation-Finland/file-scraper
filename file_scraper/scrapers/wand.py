"""Metadata scraper for image file formats."""
from file_scraper.utils import metadata
from file_scraper.wand_base import Wand


class TiffWand(Wand):
    """Collect TIFF image metadata."""

    _supported = {'image/tiff': ['6.0']}  # Supported mimetype
    _allow_versions = True                 # Allow any version

    @metadata()
    def _s_byte_order(self):
        """Return byte order."""
        if self._wand is None:
            return None
        for key, value in self._wand.metadata.items():
            if key.startswith('tiff:endian'):
                if value == 'msb':
                    return 'big endian'
                if value == 'lsb':
                    return 'little endian'
        return None


class ImageWand(Wand):
    """Collect image metadata."""

    # Supported mimetypes
    _supported = {'image/png': ['1.2'],
                  'image/jpeg': ['1.00', '1.01', '1.02', '2.0', '2.1',
                                 '2.2', '2.2.1'],
                  'image/jp2': [''],
                  'image/gif': ['1987a', '1989a']}
    _allow_versions = True  # Allow any version
