"""Metadata scraper for image file formats"""
from dpres_scraper.pil_base import Pil


class TiffPil(Pil):
    """Collect TIFF image metadata
    """

    _supported = {'image/tiff': []}  # Supported mimetype

    def _s_colorspace(self):
        """We will get colorspace from another scraper
        """
        return None

    def _s_samples_per_pixel(self):
        """Returns samples per pixel
        """
        tag_info = self._pil.tag_v2
        if tag_info and 277 in tag_info.keys():
            return str(tag_info[277])
        return super(TiffPil, self)._s_samples_per_pixel()


class ImagePil(Pil):
    """Collect image image metadata
    """
    # Supported mimetypes
    _supported = {'image/png': [], 'image/jp2': [], 'image/gif': []}

    def _s_colorspace(self):
        """We will get colorspace from another scraper
        """
        return None


class JpegPil(Pil):
    """Collect JPEG image metadata
    """

    _supported = {'image/jpeg': []}  # Supported mimetypes

    def _s_colorspace(self):
        """We will get colorspace from another scraper
        """
        return None

    def _s_samples_per_pixel(self):
        """Returns samples per pixel
        """
        exif_info = self._pil._getexif()
        if exif_info and 277 in exif_info.keys():
            return str(exif_info[277])
        return super(JpegPil, self)._s_samples_per_pixel()
