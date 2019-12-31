"""Metadata scraper for image file formats."""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseScraper
from file_scraper.pil.pil_model import ImagePilMeta, JpegPilMeta, TiffPilMeta

try:
    import PIL.Image
except ImportError:
    pass


class PilScraper(BaseScraper):
    """Scraper that uses PIL to scrape tiff, png, jpeg and gif images."""

    _supported_metadata = [TiffPilMeta, ImagePilMeta, JpegPilMeta]

    def scrape_file(self):
        """Scrape data from file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        try:
            pil = PIL.Image.open(self.filename)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(six.text_type(e))
            return
        else:
            self._messages.append("The file was analyzed successfully.")

        try:
            n_frames = pil.n_frames
        except (AttributeError, ValueError):
            # ValueError happens when n_frame property exists, but
            # the tile tries to extend outside of image.
            n_frames = 1

        for pil_index in range(0, n_frames):
            for md_class in self._supported_metadata:
                if md_class.is_supported(mimetype):
                    self.streams.append(md_class(pil, pil_index))

        self._check_supported(allow_unav_version=True)
