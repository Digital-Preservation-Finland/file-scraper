"""Module for vallidating files with JHove 1 Validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator, Shell
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


class JHoveTextUTF8(BaseValidator):
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
        validator_module = JHOVE_MODULES[self.fileinfo["format"]["mimetype"]]
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.fileinfo["filename"]]
        shell = Shell(exec_cmd)
        check_jhove_errors(shell, self)

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


class JHovePDF(BaseValidator):
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
        validator_module = JHOVE_MODULES[self.fileinfo["format"]["mimetype"]]
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.fileinfo["filename"]]
        shell = Shell(exec_cmd)
        check_jhove_errors(shell, self)
        self._check_version(shell)


    def _check_version(self, shell):
        """ Check if version string matches JHove output.
        :version: version string
        """

        report_version = get_report_field("version", shell)
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
        report_profile = get_report_field("profile")
        if profile not in report_profile:
            self.errors(
                "ERROR: File profile is '%s', expected '%s'" % (
                    report_profile, profile))


class JHoveTiff(BaseValidator):
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
        validator_module = JHOVE_MODULES[self.fileinfo["format"]["mimetype"]]
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.fileinfo["filename"]]
        shell = Shell(exec_cmd)
        check_jhove_errors(shell, self)
        self._check_version(shell)

    def _check_version(self, shell):
        """
        Check if version string matches JHove output.
        """

        report_version = get_report_field("version", shell)
        report_version = report_version.replace(" ", ".")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self.fileinfo["format"]["mimetype"] == "image/tiff" and \
            report_version in ["4.0", "5.0"]:
            return
        if report_version != self.fileinfo["format"]["version"]:
            self.errors("File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))


class JHoveJPEG(BaseValidator):
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
        validator_module = JHOVE_MODULES[self.fileinfo["format"]["mimetype"]]
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.fileinfo["filename"]]
        shell = Shell(exec_cmd)
        check_jhove_errors(shell, self)


class JHoveBasic(BaseValidator):
    """
    JHove basic class, implement JHove validation.
    """
    _supported_mimetypes = {
        'image/jp2': [""],
        'image/gif': ['1987a', '1989a'],
        'text/html': ['HTML.4.01']
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """
        validator_module = JHOVE_MODULES[self.fileinfo["format"]["mimetype"]]
        exec_cmd = ['java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, self.fileinfo["filename"]]
        shell = Shell(exec_cmd)
        check_jhove_errors(shell, self)
        self._check_version(shell)
        

    def _check_version(self, shell):
        """
        _check_version abstract method
        Check if version string matches JHove output.
        """
        if self.fileinfo["format"]["mimetype"] == 'text/plain':
            report_version = get_report_field("format", shell)
        else:
            report_version = get_report_field("version", shell)
            report_version = report_version.replace(" ", ".")

        if report_version != self.fileinfo["format"]["version"]:
            self.errors("ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))

def check_jhove_errors(shell, validator):
    """
    """
    if shell.returncode != 0:
        validator.errors("Validator returned error: %s\n%s" % (
            shell.returncode, shell.stderr))
        print "RET", shell.returncode

    status = get_report_field("status", shell)
    filename = os.path.basename(validator.fileinfo["filename"])

    if status != 'Well-Formed and valid':
        validator.errors("File '%s' does not validate: %s" % (
            filename, status))
        validator.errors("Validator returned error: %s\n%s" % (
            shell.stdout, shell.stderr))

    validator.messages(status)


def get_report_field(field, shell):
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
    print type(shell.stdout), shell.stderr, shell.stdout
    root = lxml.etree.fromstring(shell.stdout)
    query = '//j:%s/text()' % field
    results = root.xpath(query, namespaces=NAMESPACES)

    return '\n'.join(results)

