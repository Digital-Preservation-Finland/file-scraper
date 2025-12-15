"""Metadata extractor for image file formats."""
from __future__ import annotations

from typing import Literal

from file_scraper.base import BaseExtractor
from file_scraper.logger import LOGGER
from file_scraper.pil.pil_model import (
    BasePilMeta,
    DngPilMeta,
    GifPilMeta,
    Jp2PilMeta,
    JpegPilMeta,
    PngPilMeta,
    TiffPilMeta,
    WebPPilMeta,
)

try:
    import PIL.Image
except ImportError:
    pass


class PilExtractor(BaseExtractor[BasePilMeta]):
    """Extractor that uses PIL to scrape tiff, png, jpeg, gif and webp
    images.
    """

    _supported_metadata: list[type[BasePilMeta]] = [
        TiffPilMeta,
        DngPilMeta,
        PngPilMeta,
        GifPilMeta,
        JpegPilMeta,
        Jp2PilMeta,
        WebPPilMeta,
    ]

    _allow_unav_version = True

    # We need to remove 'FLI' from the formats detected by PIL, because the
    # PIL FLI code erroneously detects TIFF images as FLI or FLIC.
    # PIL does file detection in two phases. First, a few basic formats and
    # then all the rest. We aim to do the same here, but only for the specific
    # file formats that we actually support so PIL won't erroneously detect any
    # other file formats.
    # See KDKPAS-3594.
    # These format list have been collected by debugging the PIL code.
    # These are the common formats between Pillow 10.0.1 (in EPEL9) and
    # 11.3.0, which is the newest release at the time of writing this code.
    # If PIL gains support for new file formats which we want to support, these
    # lists needs to be updated.
    # If FLI/FLIC detection in PIL gets fixed, we can get rid of these lists
    # and this implementation.
    pil_basic_formats = ['GIF', 'JPEG', 'PNG']
    pil_additional_formats = ['JPEG2000', 'TIFF', 'WEBP']
    # Start with the basic format list
    pil_formats = pil_basic_formats

    @property
    def well_formed(self) -> Literal[False] | None:
        """
        PIL is not able to check well-formedness.

        :returns: False if PIL can not open or handle the file,
            None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def _extract(self) -> None:
        """Scrape data from file."""
        # Raise the size limit to around a gigabyte for a 3 bpp image
        PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024 // 3

        # Find out if we can use the minimal set of Pillow plugins to open
        # the file. If not, use a larger set. If the file can not be opened at
        # all, fail in the exception handler.
        try:
            with PIL.Image.open(
                self.filename, formats=self.pil_formats
            ) as pil:
                # File can be opened
                pass
        except PIL.Image.UnidentifiedImageError:
            self.pil_formats = self.pil_additional_formats
        except Exception as e:
            LOGGER.warning("Error analyzing file", exc_info=True)
            self._errors.append("Error in analyzing file.")
            self._errors.append(str(e))
            return

        # Do the metadata collection. We are either able to read the file
        # with the PIL plugins we have in pil_formats or we fail in the
        # (second) exception handler.
        try:
            with PIL.Image.open(
                self.filename, formats=self.pil_formats
            ) as pil:
                try:
                    n_frames = pil.n_frames
                except (AttributeError, ValueError):
                    # ValueError happens when n_frame property exists, but
                    # the tile tries to extend outside of image.
                    n_frames = 1

        except Exception as e:  # pylint: disable=invalid-name, broad-except
            LOGGER.warning("Error analyzing file", exc_info=True)
            self._errors.append("Error in analyzing file.")
            self._errors.append(str(e))
            return
        else:
            with PIL.Image.open(
                self.filename, formats=self.pil_formats
            ) as pil:
                for pil_index in range(0, n_frames):
                    pil.seek(pil_index)
                    self.streams += list(
                        self.iterate_models(pil=pil, index=pil_index)
                    )

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {
            "Pillow": {
                "version": PIL.__version__
            }
        }
