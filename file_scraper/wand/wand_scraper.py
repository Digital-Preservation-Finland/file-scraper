"""Metadata scraper for image file formats.

Wand is a ctypes-based simple ImageMagick binding for Python.

http://docs.wand-py.org/en/0.5.2/

Collects metadata from JPEG, PNG, JPEG2000, GIF, TIFF and DNG files.

Checks well-formedess by testing if ImageMagick can open and read then
file. More complete well-formedness test is required by specific validator
tool.

"""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.wand.wand_model import (WandImageMeta, WandTiffMeta,
                                          WandExifMeta, WandDngMeta)

try:
    import wand.image
except ImportError:
    pass


class WandScraper(BaseScraper):
    """Scraper for the Wand/ImageMagick library."""

    _supported_metadata = [WandExifMeta, WandTiffMeta, WandImageMeta,
                           WandDngMeta]

    def __init__(self, *args, **kwargs):
        """
        Initialize WandScraper.

        The class inherits the __init__ method from its parent class
        while adding the image file data as _wandresults.

        The _wandresults are needed to be initialized to be able to
        properly close them after the class has been executed.
        """
        super(WandScraper, self).__init__(*args, **kwargs)
        self._wandresults = None

    @property
    def well_formed(self):
        """Wand is not able to check well-formedness.

        :returns: False if Wand can not open or handle the file,
                  None otherwise.
        """
        valid = super(WandScraper, self).well_formed
        if not valid:
            return valid

        return None

    def scrape_file(self):
        """
        Populate streams with supported metadata objects.
        """
        try:
            self._wandresults = wand.image.Image(filename=self.filename)
        except Exception as e:  # pylint: disable=broad-except, invalid-name
            self._errors.append("Error in analyzing file")
            self._errors.append(str(e))
        else:
            for md_class in self._supported_metadata:
                for image in self._wandresults.sequence:
                    if md_class.is_supported(image.container.mimetype):
                        self.streams.append(md_class(image=image))
            self._check_supported(allow_unav_version=True)
            self._messages.append("The file was analyzed successfully.")

    def __del__(self):
        """
        Close potential open image files using Python's File
        close() method.
        """

        if self._wandresults:
            for frame in self._wandresults.sequence:
                frame.destroy()
            self._wandresults.close()
