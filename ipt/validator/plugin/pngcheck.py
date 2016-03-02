"""Module for validating files with pngcheck validator"""
from ipt.validator.basevalidator import BaseValidator


class Pngcheck(BaseValidator):

    """ Initializes pngcheck validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    def __init__(self, fileinfo):
        super(Pngcheck, self).__init__(fileinfo)
        self.exec_cmd = ['pngcheck']
        self.profile = None

        if self.mimetype != "image/png":
            raise Exception("Unknown mimetype: %s" % self.mimetype)

    def check_validity(self):
        if self.statuscode == 0:
            return None
        return ""

    def check_version(self, version):
        """ pngcheck does not offer information about version but supports al
            of them (via pnglib).
            """
        return None
