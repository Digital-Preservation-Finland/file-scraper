"""
This is an ImageMagick validator.
"""


from ipt.validator.basevalidator import BaseValidator
try:
    from wand.image import Image
except ImportError:
    WAND_IMPORT = False
else:
    WAND_IMPORT = True


FORMAT_STRINGS = {
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
        if not WAND_IMPORT:
            self.errors("Unable to load Wand library for Python. "
                        "The ImageMagicK library might be missing.")
            return

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
