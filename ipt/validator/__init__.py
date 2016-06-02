"""
Validate digital objects
"""

from ipt.validator.basevalidator import BaseValidator
from ipt.validator.jhove import JHoveBasic, JHoveTextUTF8, JHovePDF, JHoveTiff, JHoveJPEG
from ipt.validator.dummytextvalidator import DummyTextValidator
from ipt.validator.xmllint import Xmllint
from ipt.validator.warctools import WarcTools
from ipt.validator.ghost_script import GhostScript
from ipt.validator.pngcheck import Pngcheck


class UnknownFileformat(object):
    """
    Validator class for unknown filetypes. This will always result as
    invalid validation result.
    """

    def __init__(self, fileinfo):
        """
        Initialize object
        """
        self.fileinfo = fileinfo

    def validate(self):
        """
        No implementation
        """
        pass

    def result(self):
        """
        Return validation result
        """
        error_message = 'No validator for mimetype: %s version: %s' % (
            self.fileinfo['format']['mimetype'],
            self.fileinfo['format']['version'])

        return {
            'is_valid': False,
            'messages': [],
            'errors':  [error_message]}


def validate(fileinfo):
    """
    Validate sip with fileinfo.
    :returns: tuple (is_valid, messages, errors)
    """
    validator = iter_validator_classes(fileinfo)
    return validator.result()


def iter_validator_classes(fileinfo):
    """
    Find a validator for digital object from given `fileinfo` record.
    :returns: validator class

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python
    """

    found_validator = False
    for cls in BaseValidator.__subclasses__():
        if cls.is_supported(fileinfo):
            found_validator = True
            validator = cls(fileinfo)
            return validator

    if not found_validator:
        validator = UnknownFileformat(fileinfo)
        return validator
