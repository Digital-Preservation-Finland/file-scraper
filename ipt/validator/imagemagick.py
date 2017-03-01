"""
This is an ImageMagick validator.
"""


from ipt.validator.basevalidator import BaseValidator
from wand.image import Image


FORMAT_STRINGS = {
    'image/dpx': 'DPX',
    'image/png': 'PNG',
    'image/jpeg': 'JPEG',
    'image/jp2': 'JP2',
    'image/tiff': 'TIFF',
    }


class ImageMagick(BaseValidator):
    """
    ImageMagick validator
    """
    _supported_mimetypes = {
        "image/dpx": ["2.0"],
        "image/png": [""],
        "image/jpeg": ["1.00", "1.01", "1.02"],
        "image/jp2": [""],
        "image/tiff": ["6.0"],
    }

    def validate(self):
        """
        Validate file
        """
        try:
            img = Image(filename=self.fileinfo['filename'])
        except:
            self.errors("Could not read image")
        else:
            format_name = img.format
            if img.format == FORMAT_STRINGS[self.fileinfo['format']['mimetype']]:
                self.messages("ImageMagick detected format: " + format_name)
            else:
                self.errors("File format does not match with MIME type.")
