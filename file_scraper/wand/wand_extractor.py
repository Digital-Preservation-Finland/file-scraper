"""Metadata extractor for image file formats.

Wand is a ctypes-based simple ImageMagick binding for Python.

http://docs.wand-py.org/en/0.5.2/

Collects metadata from JPEG, PNG, JPEG2000, GIF, TIFF and DNG files.

Checks well-formedess by testing if ImageMagick can open and read then
file. More complete well-formedness test is required by specific validator
tool.

"""
import re
from concurrent.futures import ProcessPoolExecutor

from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.logger import LOGGER
from file_scraper.wand.wand_model import (WandExifMeta, WandImageMeta,
                                          WandTiffMeta, WandWebPMeta)

from collections import namedtuple

try:
    import wand.image
    import wand.version
except ImportError:
    pass


WandSingleImageContainerResult = namedtuple(
    "WandSingleImageContainerResult", ["mimetype", "metadata"]
)
WandSingleImageResult = namedtuple(
    "WandSingleImageResult",
    [
        "index", "container", "colorspace", "width", "height", "depth",
        "compression", "compression_quality"
    ]
)
WandImageResult = namedtuple("WandImageResult", ["sequence"])


def _get_wand_result(filename):
    with wand.image.Image(filename=filename) as image:
        # Convert the result into namedtuple instances that we can marshal
        # back over into the main process.
        #
        # The `wand.image.Image` instance uses a C library behind
        # the scenes, meaning it is not safe to marshal as-is.
        return WandImageResult(
            sequence=[
                WandSingleImageResult(
                    index=seq.index,
                    container=WandSingleImageContainerResult(
                        mimetype=seq.container.mimetype,
                        metadata={
                            key: seq.container.metadata[key]
                            for key in seq.container.metadata
                            # Do not read all metadata fields; some of them
                            # might contain values in Latin-1 charset that
                            # cannot be parsed by Wand.
                            # In practice we only need certain known fields,
                            # meaning we can ignore the problematic fields
                            # entirely.
                            # Also see KDKPAS-2801.
                            if key in (
                                "tiff:endian", "exif:ExifVersion",
                                "icc:description"
                            )
                        }
                    ) if seq.container else None,
                    colorspace=seq.colorspace,
                    width=seq.width,
                    height=seq.height,
                    depth=seq.depth,
                    compression=seq.compression,
                    compression_quality=seq.compression_quality
                )
                for seq in image.sequence
            ]
        )


class WandExtractor(BaseExtractor[WandImageMeta]):
    """Extractor for the Wand/ImageMagick library."""

    _supported_metadata = [
        WandExifMeta,
        WandTiffMeta,
        WandImageMeta,
        WandWebPMeta
    ]

    _allow_unav_version = True

    def __init__(self, *args, **kwargs):
        """
        Initialize WandExtractor.

        The class inherits the __init__ method from its parent class
        while adding the image file data as _wandresults.

        The _wandresults are needed to be initialized to be able to
        properly close them after the class has been executed.
        """
        super().__init__(*args, **kwargs)
        self._wandresults = None

    @property
    def well_formed(self):
        """Wand is not able to check well-formedness.

        :returns: False if Wand can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def extract(self):
        """
        Populate streams with supported metadata objects.
        """
        try:
            # Perform Wand scraping in a separate process. Wand library
            # currently suffers from memory leaks.
            with ProcessPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_get_wand_result, self.filename)
                self._wandresults = future.result()
        except Exception as e:  # pylint: disable=broad-except, invalid-name
            self._errors.append("Error in analyzing file")
            self._errors.append(str(e))
        else:
            for md_class in self._supported_metadata:
                for image in self._wandresults.sequence:
                    if md_class.is_supported(image.container.mimetype):
                        self.streams.append(md_class(image=image))
            self._validate()
            self._messages.append("The file was analyzed successfully.")

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        version_str = wand.version.MAGICK_VERSION
        # ImageMagick following a group with any character, digit, number and
        # also can include dash or dot one or more times.
        regex = r"ImageMagick ([\w\-.]+)"
        try:
            version = next(
                re.finditer(regex, version_str, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not retrieve Wand version from string %s",
                version_str
            )
            version = UNAV
        return {"ImageMagick": {"version": version}}
