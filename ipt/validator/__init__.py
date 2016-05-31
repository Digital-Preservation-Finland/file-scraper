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


def iter_validator_classes():
    """Return all validator classes as iterable"""
    for cls in BaseValidator.__subclasses__():
        yield cls
    for cls in JHove.__subclasses__():
        yield cls


def validate(fileinfo):
    """Validate digital object from given `fileinfo` record, using any of the
    validator classes.

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python

    """

    found_validator = False
    for cls in iter_validator_classes():
        if cls.is_supported_mimetype(fileinfo):
            found_validator = True
            validator = cls(fileinfo)
            yield validator.result()

    if not found_validator:
        validator = UnknownFileformat(fileinfo)
        yield validator.result()
