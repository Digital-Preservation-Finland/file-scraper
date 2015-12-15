"""Module for vallidating files with JHove 1 Validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator
from ipt.utils import UnknownException, ValidationException

JHOVE_MODULES = {
    'application/pdf': 'PDF-hul',
    'image/tiff': 'TIFF-hul',
    'image/jpeg': 'JPEG-hul',
    'image/jp2': 'JPEG2000-hul',
    'image/gif': 'GIF-hul'
}

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}


class Jhove(object):

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
        self.exec_cmd = ['jhove', '-h', 'XML']
        self.filename = filename
        self.statuscode = 1
        self.stderr = ""
        self.stdout = ""
        self.profile = None
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
            raise ValidationException(
                "jhove.py does not seem to support mimetype: %s" % mimetype)


    def validate(self):
            """Validate file with command given in variable self.exec_cmd and with
            options set in self.exec_options. Also check that validated file
            version and profile matches with validator.

            :returns: Tuple (status, report, errors) where
                status -- 0 is success, anything else failure
                report -- generated report
                errors -- errors if encountered, else None
            """

            filename_in_list = [self.filename]
            self.exec_cmd += filename_in_list
            self.exec_validator()

            if self.statuscode != 0:
                return (
                    self.statuscode, self.stdout,
                    "Validator returned error: %s\n%s" %
                    (statuscode, stderr))

            errors = []

            # Check file validity
            (validity_exitcode,
                validity_stdout,
                validity_stderr) = self.check_validity()
            if validity_exitcode != 0:
                errors.append(validity_stderr)

            # Check file version
            (version_exitcode, version_errors) = self.check_version(
                self.fileversion)
            if version_exitcode != 0:
                errors.append(version_errors)

            # Check file profile
            (profile_exitcode, profile_errors) = self.check_profile(
                self.profile)
            if profile_exitcode != 0:
                errors.append(profile_errors)

            if len(errors) == 0:
                return (0, self.stdout, '')
            else:
                return (117, self.stdout, '\n'.join(errors))


    def check_validity(self):
        """ Check if file is valid according to JHove output.

            Returns:
                None if file is valid, otherwise returns JHove's error message.
        """
        print
        print "RESULT", self.stderr, self.stdout, self.statuscode
        if self.statuscode == 254 or self.statuscode == 255:
            raise UnknownException("Jhove returned returncode: \
                %s %s %s" % (self.statuscode, self.stdout, self.stderr))
        status = self.get_report_field("status")
        filename = self.get_report_field("repInfo")
        filename = os.path.basename(filename)

        if status != 'Well-Formed and valid':
            return (117, "", "ERROR: File '%s' does not validate: %s" % (filename,
                                                               status))
        return (0, "", "")


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
            return (0, "")

        if self.mimetype == "application/pdf" and "A-1" in version:
            self.profile = "ISO PDF/A-1"
            version = "1.4"

        if report_version != version:
            return (117, ("ERROR: File version is '%s', expected '%s'" \
                % (report_version, version)))
        return (0, "")


    def check_profile(self, profile):
        """ Check if profile string matches JHove output.

            Arguments:
                profile: profile string

            Returns:
                None if profile matches, else returns JHove's error message.
        """

        report_profile = self.get_report_field("profile")
        if profile is None:
            return (0, "")

        if profile not in report_profile:
            return (117, "ERROR: File profile is '%s', expected '%s'" % (
                report_profile, profile))
        return (0, "")

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
