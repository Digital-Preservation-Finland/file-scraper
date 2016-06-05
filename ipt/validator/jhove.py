"""
Module for vallidating files with JHove 1 Validator
"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import UnknownException, run_command


NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, '/bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/JhoveApp.jar') + ':' + EXTRA_JARS


class JHoveUtils(object):
    """
    Basic methods for jhove validation.
    """
    def jhove_validation(self, validator_module, filename):
        """
        Validate file with jhove.
        :validator_module: Jhove validatormodule.
        :filename: filename
        :returns: tuple (status, stdout, errors)
            :status: status for report
            :stdout: xml based jhove report for other validation steps.
            :errors: errors
        """
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, filename]
        shell = Shell(exec_cmd)

        errors = []
        if shell.returncode != 0:
            errors.append("Validator returned error: %s\n%s" % (
                shell.returncode, shell.stderr))
        status = self.get_report_field("status", shell.stdout)
        filename = os.path.basename(filename)
        if status != 'Well-Formed and valid':
            errors.append("File '%s' does not validate: %s" % (
                filename, status))
            errors.append("Validator returned error: %s\n%s" % (
                shell.stdout, shell.stderr))
        return status, shell.stdout, '\n'.join(errors)


    def get_report_field(self, field, stdout):
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
        :stdout: jhove xml report in a string
        :returns:
            Concatenated string where each result is on own line. An empty
            string is returned if there's no results.
        """
        root = lxml.etree.fromstring(stdout)
        query = '//j:%s/text()' % field
        results = root.xpath(query, namespaces=NAMESPACES)

        return '\n'.join(results)


class JHoveTextUTF8(BaseValidator, JHoveUtils):
    """
    JHove validator fir text/plain UTF-8
    """
    _supported_mimetypes = {
        'text/plain': []
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        (message, _, error)  = self.jhove_validation('UTF8-hul', self.fileinfo["filename"])
        self.messages(message)
        self.errors(error)

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


class JHovePDF(BaseValidator, JHoveUtils):
    """
    JHove validator for PDF
    """

    _supported_mimetypes = {
        'application/pdf': ['1.3', '1.4', '1.5', '1.6', 'A-1a', 'A-1b']
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        (message, stdout, error) = self.jhove_validation('PDF-hul', self.fileinfo["filename"])
        self.messages(message)
        self.errors(error)
        self._check_version(stdout)
        self._check_profile()


    def _check_version(self, shell):
        """ Check if version string matches JHove output.
        :shell: shell utility tool
        """

        report_version = self.get_report_field("version", shell)
        report_version = report_version.replace(" ", ".")
        if "A-1" in self.fileinfo["format"]["version"]:
            self.fileinfo["format"]["version"] = "1.4"

        if report_version != self.fileinfo["format"]["version"]:
            self.errors("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))

    def _check_profile(self):
        """ Check if profile string matches JHove output.
        """
        if "A-1" not in self.fileinfo["format"]["version"]:
            return
        profile = "ISO PDF/A-1"
        report_profile = self.get_report_field("profile")
        if profile not in report_profile:
            self.errors(
                "ERROR: File profile is '%s', expected '%s'" % (
                    report_profile, profile))


class JHoveTiff(BaseValidator, JHoveUtils):
    """
    JHove validator for tiff
    """
    _supported_mimetypes = {
        'image/tiff': ['6.0']
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        (message, stdout, error) = self.jhove_validation('TIFF-hul', self.fileinfo["filename"])
        self.messages(message)
        self.errors(error)
        self._check_version(stdout)

    def _check_version(self, shell):
        """
        Check if version string matches JHove output.
        :shell: shell utility tool
        """

        report_version = self.get_report_field("version", shell)
        report_version = report_version.replace(" ", ".")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self.fileinfo["format"]["mimetype"] == "image/tiff" and \
            report_version in ["4.0", "5.0"]:
            return
        if report_version != self.fileinfo["format"]["version"]:
            self.errors("File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))


class JHoveJPEG(BaseValidator, JHoveUtils):
    """
    JHove validator for JPEG
    """
    _supported_mimetypes = {
        'image/jpeg': [''],
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        (message, _, error) = self.jhove_validation('JPEG-hul', self.fileinfo["filename"])
        self.messages(message)
        self.errors(error)


class JHoveBasic(BaseValidator, JHoveUtils):
    """
    JHove basic class, implement JHove validation.
    """
    _supported_mimetypes = {
        'image/jp2': [""],
        'image/gif': ['1987a', '1989a'],
        'text/html': ['HTML.4.01']
    }

    _jhove_modules = {
    'image/jp2': 'JPEG2000-hul',
    'image/gif': 'GIF-hul',
    'text/html': 'HTML-hul'
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        validator_module = self._jhove_modules[self.fileinfo["format"]["mimetype"]]
        (message, stdout, error) = self.jhove_validation(
            validator_module, self.fileinfo["filename"])

        self.messages(message)
        self.errors(error)
        self._check_version(stdout)
 

    def _check_version(self, stdout):
        """
        Check if fileinfo version matches JHove output.
        :stdout: jhove xml report in a string
        """
        if self.fileinfo["format"]["mimetype"] == 'text/plain':
            report_version = self.get_report_field("format", stdout)
        else:
            report_version = self.get_report_field("version", stdout)
            report_version = report_version.replace(" ", ".")

        if report_version != self.fileinfo["format"]["version"]:
            self.errors("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))