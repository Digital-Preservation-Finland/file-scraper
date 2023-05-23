"""Metadata scraper for image file formats."""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseScraper
from file_scraper.pil.pil_model import ImagePilMeta, JpegPilMeta, \
    TiffPilMeta, DngPilMeta, Jp2PilMeta

try:
    import PIL.Image
except ImportError:
    pass


class PilScraper(BaseScraper):
    """Scraper that uses PIL to scrape tiff, png, jpeg and gif images."""

    _supported_metadata = [TiffPilMeta, DngPilMeta,
                           ImagePilMeta, JpegPilMeta,
                           Jp2PilMeta]

    def scrape_file(self):
        """Scrape data from file."""
        try:
            # Raise the size limit to around a gigabyte for a 3 bpp image
            PIL.Image.MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 // 3)

            with PIL.Image.open(self.filename) as pil:

                try:
                    n_frames = pil.n_frames
                except (AttributeError, ValueError):
                    # ValueError happens when n_frame property exists, but
                    # the tile tries to extend outside of image.
                    n_frames = 1

                for pil_index in range(0, n_frames):
                    pil.seek(pil_index)
                    self.streams += list(
                        self.iterate_models(pil=pil, index=pil_index))

        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(six.text_type(e))
            return
        else:
            self._messages.append("The file was analyzed successfully.")

        self._check_supported(allow_unav_version=True)
