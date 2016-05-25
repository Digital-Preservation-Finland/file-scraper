"""Validate digital objects"""

from ipt.validator.basevalidator import BaseValidator
from ipt.validator.jhove import JHove
from ipt.validator.dummytextvalidator import DummyTextValidator
from ipt.validator.xmllint import Xmllint
from ipt.validator.warctools import WarcTools
from ipt.validator.ghost_script import GhostScript
from ipt.validator.pngcheck import Pngcheck


class UnknownFileformat(object):
    """Validator class for unknown filetypes. This will always result as
    invalid validation result"""

    def __init__(self, fileinfo):
        """Initialize object"""
        self.fileinfo = fileinfo

    def validate(self):
        """No implementation"""
        pass

    def result(self):
        """Return validation result"""
        error_message = 'No validator for mimetype: %s version: %s' % (
            self.fileinfo['format']['mimetype'],
            self.fileinfo['format']['version'])

        return {
            'is_valid': False,
            'messages': [],
            'errors':  [error_message]}


def validate(fileinfo):
    """Validate digital object from given `fileinfo` record, using any of the
    validator classes.

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python

    """

    base_validators = [BaseValidator, JHove]
    found_validator = False

    for base_validator in base_validators:
        for cls in base_validator.__subclasses__():
            if cls.is_supported_mimetype(fileinfo):
                found_validator = True
                validator = cls(fileinfo)
                yield validator.result()

    if not found_validator:
        validator = UnknownFileformat(fileinfo)
        yield validator.result()
