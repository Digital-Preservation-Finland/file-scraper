"""
This is an ImageMagick validator.
"""


from ipt.validator.basevalidator import BaseValidator
from wand.image import Image


FORMAT_STRINGS = {
    'image/dpx': 'DPX',
    'image/png': 'PNG',
    }


class ImageMagick(BaseValidator):
    """
    ImageMagick validator
    """
    _supported_mimetypes = {
        'image/dpx': ['2.0'],
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
            self.messages("ImageMagick detected format: " + format_name)
            if not img.format == FORMAT_STRINGS[self.fileinfo['format']['mimetype']]:
                self.errors("File format does not match with MIME type.")
