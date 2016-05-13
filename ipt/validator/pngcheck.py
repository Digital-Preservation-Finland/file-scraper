"""Module for validating files with pngcheck validator"""
from ipt.validator.basevalidator import BaseValidator

from ipt.utils import UnknownException, run_command


class Pngcheck(BaseValidator):

    """ Initializes pngcheck validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_mimetypes = {
        'image/png': []
    }

    def __init__(self, fileinfo):
        super(Pngcheck, self).__init__(fileinfo)
        self.exec_cmd = ['pngcheck', fileinfo["filename"]]
        self.profile = None
        self.statuscode = None
        self.stdout = None
        self.stderr = None

    def _check_validity(self):
        """
        check validity
        """
        if self.statuscode != 0:
            self.is_valid(False)
            self._errors.append("ERROR: %s" % self.stderr)
        return ""

    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: Tuple (status, report, errors) where
            status -- True is success, False failure, anything else failure
            report -- generated report
            errors -- errors if encountered, else None
        """
        (self.statuscode,
         self.stdout,
         self.stderr) = run_command(cmd=self.exec_cmd)
        self._messages.append(self.stdout)

        self._check_validity()

        messages = "\n".join(message for message in self.messages())
        errors = "\n".join(error for error in self.errors())
        return (self.is_valid(), messages, errors)
