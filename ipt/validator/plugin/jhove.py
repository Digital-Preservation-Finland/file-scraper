"""Module for vallidating files with JHove 1 Validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator

JHOVE_MODULES = {
    'application/pdf': 'PDF-hul',
    'image/tiff': 'TIFF-hul',
    'image/jpeg': 'JPEG-hul',
    'image/jp2': 'JPEG2000-hul',
    'image/gif': 'GIF-hul'
}

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}


class UnknownReturnCode(Exception):
    """Raised when any validation returns unknown returncode."""
    pass


class Jhove(BaseValidator):

    """ Initializes JHove 1 validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.

        .. note:: The following mimetypes and JHove modules are supported:
                  'application/pdf': 'PDF-hul', 'image/tiff': 'TIFF-hul',
                  'image/jpeg': 'JPEG-hul', 'image/jp2': 'JPEG2000-hul',
                  'image/gif': 'GIF-hul'

        .. seealso:: http://jhove.sourceforge.net/documentation.html
    """

    def __init__(self, mimetype, fileversion, filename):
        super(Jhove, self).__init__()
        self.exec_cmd = ['jhove', '-h', 'XML']
        self.filename = filename
        # only names with whitespace are quoted. this might break the
        # filename otherwise ::
        if filename.find(" ") != -1:
            if not (filename[0] == '"' and filename[-1] == '"'):
                self.filename = '%s%s%s' % ('"', filename, '"')

        self.fileversion = fileversion
        self.mimetype = mimetype

        if mimetype in JHOVE_MODULES.keys():
            validator_module = JHOVE_MODULES[mimetype]
            command = ['-m', validator_module]
            self.exec_cmd += command
        else:
            raise Exception("Unknown mimetype: %s" % mimetype)

    def check_validity(self):
        """ Check if file is valid according to JHove output.

            Returns:
                None if file is valid, otherwise returns JHove's error message.
        """
        if self.statuscode != 255:
            raise UnknownReturnCode("Jhove returned unknown returncode: \
                %s %s %s" % (self.statuscode, self.stdout, self.stderr))
        status = self.get_report_field("status")
        filename = self.get_report_field("repInfo")
        filename = os.path.basename(filename)

        if status != 'Well-Formed and valid':
            return "ERROR: File '%s' does not validate: %s" % (filename,
                                                               status)

        return None

    def check_version(self, version):
        """ Check if version string matches JHove output.

            Arguments:
                version: version string

            Returns:
                None if version matches, else returns JHove's error message.
        """

        report_version = self.get_report_field("version")
        report_version = report_version.replace(" ", ".")

        if version is None:
            return None

        if self.mimetype == "application/pdf" and "A-1" in version:
            self.profile = "ISO PDF/A-1"
            version = "1.4"

        if report_version != version:
            return "ERROR: File version is '%s', expected '%s'" \
                % (report_version, version)
        return None

    def check_profile(self, profile):
        """ Check if profile string matches JHove output.

            Arguments:
                profile: profile string

            Returns:
                None if profile matches, else returns JHove's error message.
        """

        report_profile = self.get_report_field("profile")
        if profile is None:
            return None

        if profile not in report_profile:
            return "ERROR: File profile is '%s', expected '%s'" % (
                report_profile, profile)
        return None

    def get_report_field(self, field):
        """ Return field value from JHoves XML output. This method assumes that
            JHove's XML output handler is used: jhove -h XML. Method uses XPath
            for querying JHoves output. This method is mainly used by validator
            class itself. Example usage:

            .. code-block:: python

                get_report_field("Version", report)
                1.2

                get_report_field("Status", report)
                "Well formed"

            Arguments:
                field: Field name which content we are looking for. In practise
                field is an element in XML document.

            Returns:
                Concatenated string where each result is on own line. An empty
                string is returned if there's no results.

        """

        root = lxml.etree.fromstring(self.stdout)
        query = '//j:%s/text()' % field
        results = root.xpath(query, namespaces=NAMESPACES)

        return '\n'.join(results)
