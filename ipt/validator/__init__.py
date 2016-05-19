import ipt.validator.jhove
import ipt.validator.filecommand
import ipt.validator.xmllint
import ipt.validator.warctools
import ipt.validator.ghost_script
import ipt.validator.pngcheck
import ipt.validator.csv_validator


from ipt.validator.basevalidator import BaseValidator
from ipt.validator.jhove import JHove


class UnknownMimetypeError(Exception):
    pass


class UnknownFileformat(object):
    ERROR_MSG = 'No validator for mimetype: %s version: %s'

    def __init__(self, fileinfo):
        self.mimetype = fileinfo['format']['mimetype']
        self.version = fileinfo['format']['version']

    def validate(self):
        return (117, '', self.ERROR_MSG % (self.mimetype, self.version))


def validate(fileinfo):
    # Implementation of class factory pattern from
    # http://stackoverflow.com/questions/456672/class-factory-in-python

    found_validator = False
    for cls in BaseValidator.__subclasses__():
        if cls.is_supported_mimetype(fileinfo):
            found_validator = True
            yield cls(fileinfo).validate()

    for cls in JHove.__subclasses__():
        if cls.is_supported_mimetype(fileinfo):
            found_validator = True
            yield cls(fileinfo).validate()

    if not found_validator:
        yield UnknownFileformat(fileinfo).validate()
