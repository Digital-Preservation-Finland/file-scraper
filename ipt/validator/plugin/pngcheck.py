"""Module for validating files with pngcheck validator"""
from ipt.validator.basevalidator import BaseValidator


class Pngcheck(BaseValidator):

    """ Initializes pngcheck validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    def __init__(self, mimetype, fileversion, filename):
        super(Pngcheck, self).__init__()
        self.exec_cmd = ['pngcheck']
        self.filename = filename
        self.fileversion = fileversion
        self.mimetype = mimetype

        if mimetype != "image/png":
            raise Exception("Unknown mimetype: %s" % mimetype)

    def check_validity(self):
        if self.statuscode == 0:
            return None
        return ""

    def check_version(self, version):
        """ pngcheck does not offer information about version but supports al
            of them (via pnglib).
            """
        return None

    def check_profile(self, profile):
        """ PNG file format does not have profiles """
        return None
