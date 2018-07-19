"""
This is an ImageMagick validator.
"""


from ipt.validator.basevalidator import BaseValidator
from wand.image import Image


FORMAT_STRINGS = {
    'image/x-dpx': 'DPX',
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
            img = Image(filename=self.metadata_info['filename'])
        except:
            self.errors("Could not read image")
        else:
            format_name = img.format
            if img.format == FORMAT_STRINGS[
                    self.metadata_info['format']['mimetype']]:
                self.messages("ImageMagick detected format: " + format_name)
            else:
                self.errors("File format does not match with MIME type.")
            # ensure that temporary files are not left in /tmp/
            img.__del__()

