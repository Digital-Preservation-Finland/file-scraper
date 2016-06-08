"""
Module for vallidating files with JHove 1 Validator
"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator, Shell


NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, '/bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/JhoveApp.jar') + ':' + EXTRA_JARS


class JHoveBase(BaseValidator):
    """
    Basic methods for jhove validation.
    """
    _supported_mimetypes = {}

    def __init__(self, fileinfo):
        """
        init
        """

        super(JHoveBase, self).__init__(fileinfo)

        self.filename = None
        self.report = None
        self.shell = None

    def jhove_command(self, validator_module, filename):
        """
        Validate file with jhove.
        :validator_module: Jhove validatormodule.
        :filename: filename
        """

        self.filename = filename

        exec_cmd = [
            'java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            validator_module, filename]
        self.shell = Shell(exec_cmd)

        errors = []

        if self.shell.returncode != 0:
            errors.append("JHove returned error: %s\n%s" % (
                self.shell.returncode, self.shell.stderr))

        self.report = lxml.etree.fromstring(self.shell.stdout)

    def check_well_formed(self):
        """
        Check_well_formed.
        """

        status = self.report_field("status")

        if status != 'Well-Formed and valid':
            self.errors("File '%s' does not validate: %s" % (
                self.filename, status))
            self.errors("Validator returned error: %s\n%s" % (
                self.shell.stdout, self.shell.stderr))

    def report_field(self, field):
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

        query = '//j:%s/text()' % field
        results = self.report.xpath(query, namespaces=NAMESPACES)
        return '\n'.join(results)


class JHoveTextUTF8(JHoveBase):
    """
    JHove validator fir text/plain UTF-8
    """
    _supported_mimetypes = {
        'text/plain': ['']
    }

    def validate(self):
        """
        Check if file is valid according to JHove output.
        """

        self.jhove_command('UTF8-hul', self.fileinfo["filename"])
        self.check_well_formed()

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


class JHovePDF(JHoveBase):
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

        self.jhove_command('PDF-hul', self.fileinfo["filename"])

        self.check_well_formed()
        self.check_version()
        self.check_profile()

    def check_version(self):
        """ Check if version string matches JHove output.
        :shell: shell utility tool
        """

        report_version = self.report_field("version")
        report_version = report_version.replace(" ", ".")
        if "A-1" in self.fileinfo["format"]["version"]:
            self.fileinfo["format"]["version"] = "1.4"

        if report_version != self.fileinfo["format"]["version"]:
            self.errors(
                "ERROR: File version is '%s', expected '%s'"
                % (report_version, self.fileinfo["format"]["version"]))

    def check_profile(self):
        """ Check if profile string matches JHove output.
        """
        if "A-1" not in self.fileinfo["format"]["version"]:
            return
        profile = "ISO PDF/A-1"
        report_profile = self.report_field("profile")
        if profile not in report_profile:
            self.errors(
                "ERROR: File profile is '%s', expected '%s'" % (
                    report_profile, profile))


class JHoveTiff(JHoveBase):
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
        self.jhove_command('TIFF-hul', self.fileinfo["filename"])
        self.messages()
        self.errors()
        self._check_version()

    def _check_version(self):
        """
        Check if version string matches JHove output.
        :shell: shell utility tool
        """

        report_version = self.report_field("version")
        report_version = report_version.replace(" ", ".")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self.fileinfo["format"]["mimetype"] == "image/tiff" and \
                report_version in ["4.0", "5.0"]:
            return
        if report_version != self.fileinfo["format"]["version"]:
            self.errors("File version is '%s', expected '%s'" % (
                report_version, self.fileinfo["format"]["version"]))


class JHoveJPEG(JHoveBase):
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
        (message, _, error) = self.jhove_command(
            'JPEG-hul', self.fileinfo["filename"])
        self.messages(message)
        self.errors(error)


class JHoveBasic(JHoveBase):
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
        validator_module = self._jhove_modules[
            self.fileinfo["format"]["mimetype"]]
        self.jhove_command(validator_module, self.fileinfo["filename"])

        self.messages()
        self.errors()
        self._check_version()

    def _check_version(self):
        """
        Check if fileinfo version matches JHove output.
        :stdout: jhove xml report in a string
        """
        if self.fileinfo["format"]["mimetype"] == 'text/plain':
            report_version = self.report_field("format")
        else:
            report_version = self.report_field("version")
            report_version = report_version.replace(" ", ".")

        if report_version != self.fileinfo["format"]["version"]:
            self.errors("ERROR: File version is '%s', expected '%s'" % (
                report_version, self.fileinfo["format"]["version"]))
