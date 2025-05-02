"""Metadata scraper for image file formats."""

from file_scraper.base import BaseScraper
from file_scraper.pil.pil_model import PngPilMeta, JpegPilMeta, \
    TiffPilMeta, DngPilMeta, Jp2PilMeta, GifPilMeta, WebPPilMeta

try:
    import PIL.Image
except ImportError:
    pass


class PilScraper(BaseScraper):
    """Scraper that uses PIL to scrape tiff, png, jpeg, gif and webp images."""

    _supported_metadata = [TiffPilMeta, DngPilMeta, PngPilMeta, GifPilMeta,
                           JpegPilMeta, Jp2PilMeta, WebPPilMeta]

    @property
    def well_formed(self):
        """
        PIL is not able to check well-formedness.

        :returns: False if PIL can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

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

        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(str(e))
            return
        else:
            with PIL.Image.open(self.filename) as pil:
                for pil_index in range(0, n_frames):
                    pil.seek(pil_index)
                    self.streams += list(
                        self.iterate_models(pil=pil, index=pil_index))

            self._check_supported(allow_unav_version=True)

            self._messages.append("The file was analyzed successfully.")

    def tools(self):
        """Collect software use by scraper"""

        return {
            "pil-image": {
                "version": PIL.Image.__version__
            }
        }
