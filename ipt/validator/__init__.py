import ipt.validator.jhove
import ipt.validator.jhove2
import ipt.validator.libxml
import ipt.validator.filecommand
import ipt.validator.xmllint
import ipt.validator.warctools

from ipt.validator.basevalidator import BaseValidator


class UnknownMimetypeError(Exception):
    pass


def Validator(fileinfo):
    # Implementation of class factory pattern from
    # http://stackoverflow.com/questions/456672/class-factory-in-python

    for cls in BaseValidator.__subclasses__():
        if cls.is_supported_mimetype(fileinfo):
            return cls(fileinfo)
    raise UnknownMimetypeError('No validator for mimetype: %s version: %s' %
                               (fileinfo['format']['mimetype'],
                                fileinfo['format']['version']))
