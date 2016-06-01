"""Module for vallidating files with JHove 1 Validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator
from ipt.utils import UnknownException, run_command

JHOVE_MODULES = {
    'application/pdf': 'PDF-hul',
    'image/tiff': 'TIFF-hul',
    'image/jpeg': 'JPEG-hul',
    'image/jp2': 'JPEG2000-hul',
    'image/gif': 'GIF-hul',
    'text/html': 'HTML-hul',
    'text/plain': 'UTF8-hul'
}

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, '/bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/JhoveApp.jar') + ':' + EXTRA_JARS


class JHove(BaseValidator):
    """
    JHove base class, implement basic functionalities of JHove validation.
    """
    _supported_mimetypes = {
        'image/jp2': [""],
        'image/gif': ['1987a', '1989a'],
        'text/html': ['HTML.4.01']
    }

    def __init__(self, fileinfo):
        """init.
        :fileinfo: a dictionary with format

            fileinfo["filename"]
            fileinfo["algorithm"]
            fileinfo["digest"]
            fileinfo["format"]["version"]
            fileinfo["format"]["mimetype"]
            fileinfo["format"]["charset"]
            fileinfo["format"]["format_registry_key"]
            fileinfo["object_id"]["type"]
            fileinfo["object_id"]["value"]
        """

        super(JHove, self).__init__(fileinfo)
        self.filename = fileinfo['filename']
        self.mimetype = fileinfo['format']['mimetype']
        if "version" in fileinfo["format"]:
            self.fileversion = fileinfo['format']['version']

        validator_module = JHOVE_MODULES[self.mimetype]
        self.exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.filename]
        self.statuscode = None
        self.stdout = None
        self.stderr = None

    def _check_validity(self):
        """
        Check if file is valid according to JHove output.
        """

        if self.statuscode != 0:
            self.is_valid(False)
            self._errors.append(
                "Validator returned error: %s\n%s" % (
                    self.statuscode, self.stderr))

        if self.statuscode == 254 or self.statuscode == 255:
            raise UnknownException("Jhove returned returncode: \
                %s %s %s" % (self.statuscode, self.stdout, self.stderr))

        status = self.get_report_field("status")
        filename = os.path.basename(self.filename)

        if status != 'Well-Formed and valid':
            self._errors.append("ERROR: File '%s' does not validate: %s" % (
                filename, status))
            self._errors.append("Validator returned error: %s\n%s" % (
                self.stdout, self.stderr))
            self.is_valid(False)

        self._messages.append(status)

    def _check_profile(self):
        """
        """
        pass

    def _check_charset(self):
        """
        """
        pass

    def _check_version(self):
        """
        _check_version abstract method
        Check if version string matches JHove output.
        """
        if self.mimetype == 'text/plain':
            report_version = self.get_report_field("format")
        else:
            report_version = self.get_report_field("version")
            report_version = report_version.replace(" ", ".")

        if report_version != self.fileversion:
            self.is_valid(False)
            self._errors.append("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileversion))

    def validate(self):
        """Validate file with command given in variable self.exec_cmd and with
        options set in self.exec_options. Also check that validated file
        version and profile matches with validator.

        :returns: Tuple (validity, messages, errors) where
            validity -- True is success, False failure, anything else failure
            messages -- generated report
            errors -- errors if encountered, else None
        """
        (self.statuscode,
         self.stdout,
         self.stderr) = run_command(cmd=self.exec_cmd)

        self._check_charset()
        self._check_validity()
        self._check_version()
        messages = "\n".join(message for message in self.messages())
        errors = "\n".join(error for error in self.errors())
        return (self.is_valid(), messages, errors)

    def get_report_field(self, field):
        """
        Return field value from JHoves XML output. This method assumes that
        JHove's XML output handler is used: jhove -h XML. Method uses XPath
        for querying JHoves output. This method is mainly used by validator
        class itself. Example usage:

        .. code-block:: python

            get_report_field("Version", report)
            1.2

            get_report_field("Status", report)
            "Well formed"

        :field: Field name which content we are looking for. In practise
            field is an element in XML document.
        :returns:
            Concatenated string where each result is on own line. An empty
            string is returned if there's no results.
        """

        root = lxml.etree.fromstring(self.stdout)
        query = '//j:%s/text()' % field
        results = root.xpath(query, namespaces=NAMESPACES)

        return '\n'.join(results)


class JHoveTextUTF8(JHove):
    """
    JHove validator fir text/plain UTF-8
    """
    _supported_mimetypes = {
        'text/plain': []
    }

    def __init__(self, fileinfo):
        """
        init.
        :fileinfo: a dictionary with fileinfo
        """
        super(JHoveTextUTF8, self).__init__(fileinfo)
        self.charset = fileinfo['format']['charset']

    @classmethod
    def is_supported_mimetype(cls, fileinfo):
        """
        Check suported mimetypes.
        :fileinfo: fileinfo
        """
        if fileinfo['format']['mimetype'] == 'text/plain':
            if fileinfo['format']['charset'] == 'UTF-8':
                return True
        return False

    def _check_version(self):
        pass


class JHovePDF(JHove):
    """
    JHove validator for PDF
    """

    _supported_mimetypes = {
        'application/pdf': ['1.3', '1.4', '1.5', '1.6', 'A-1a', 'A-1b']
    }

    def __init__(self, fileinfo):
        """
        init.
        :fileinfo: a dictionary with fileinfo
        """
        super(JHovePDF, self).__init__(fileinfo)
        self.fileversion = fileinfo['format']['version']

    def _check_version(self):
        """ Check if version string matches JHove output.
        :version: version string
        """

        report_version = self.get_report_field("version")
        report_version = report_version.replace(" ", ".")
        if "A-1" in self.fileversion:
            self.fileversion = "1.4"

        if report_version != self.fileversion:
            self.is_valid(False)
            self._errors.append("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileversion))

    def _check_profile(self):
        """ Check if profile string matches JHove output.
        """
        if "A-1" not in self.fileversion:
            return
        profile = "ISO PDF/A-1"
        report_profile = self.get_report_field("profile")
        if profile not in report_profile:
            self.is_valid(False)
            self._errors.append(
                "ERROR: File profile is '%s', expected '%s'" % (
                    report_profile, profile))


class JHoveTiff(JHove):
    """
    JHove validator for tiff
    """
    _supported_mimetypes = {
        'image/tiff': ['6.0']
    }

    def __init__(self, fileinfo):
        """
        init.
        :fileinfo: a dictionary with fileinfo
        """
        super(JHoveTiff, self).__init__(fileinfo)
        self.fileversion = fileinfo['format']['version']

    def _check_version(self):
        """ Check if version string matches JHove output.
        :version: version string
        :returns: a tuple (0/117, errormessage)
        """

        report_version = self.get_report_field("version")
        report_version = report_version.replace(" ", ".")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self.mimetype == "image/tiff" and report_version in ["4.0", "5.0"]:
            return
        if report_version != self.fileversion:
            self.is_valid(False)
            self._errors.append("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileversion))


class JHoveJPEG(JHove):
    """
    JHove validator for JPEG
    """
    _supported_mimetypes = {
        'image/jpeg': [''],
    }

    def _check_version(self):
        """
        JPEG version is not checked.
        """
        pass
