"""Module for validating files with pngcheck validator"""

from ipt.validator.basevalidator import BaseValidator, Shell


class Pngcheck(BaseValidator):

    """ Initializes pngcheck validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_mimetypes = {
        'image/png': []
    }

    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: True if validation was successful

        """

        shell = Shell(['pngcheck', self.fileinfo["filename"]])

        if shell.returncode != 0:
            self.errors("Validation failed: returncode %s" % shell.returncode)
            self.errors(shell.stderr)

        self.messages(shell.stdout)
