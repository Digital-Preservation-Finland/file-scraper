"""Module for validating files with GNU file command. Instead of validating
this module is more like identifying file formats. At the moment this is used
only for validating text files. """
import os
import re
import subprocess

from ipt.validator.basevalidator import BaseValidator

class Filecommand(BaseValidator):

    """ Initializes validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.
    
    
    .. seealso:: http://linux.die.net/man/1/file
    """
    def __init__(self, mimetype, fileversion, filename):
        self.exec_cmd = ['file', '-e', 'soft']
        self.filename = filename
        self.fileversion = fileversion
        self.mimetype = mimetype
        
        if mimetype != "text/plain":
            raise Exception("Unknown mimetype: %s" % mimetype)

    def check_validity(self):
        filename = os.path.basename(self.filename)

        if not "text" in self.stdout:
            return "ERROR: File '%s' does not validate." % filename

        return None

    def check_version(self, version):
        """ Check the file version of given file. In WARC format version string
            is stored at the first line of file so this methods read the first
            line and check that it matches. """

        if version == "ISO-8859-15":
            if "ASCII" in self.stdout:
                return None
            if "ISO-8859" in self.stdout:
                return None
        elif version == "UTF-8":
            if "UTF-8" in self.stdout:
                return None

        return "ERROR: File version is '%s', expected '%s'" % \
               (self.stdout, version)
  
    
    def check_profile(self, profile):
        """ FIXME: Remove this from BaseValidator class. """
        return None
