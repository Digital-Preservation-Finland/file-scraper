"""Module for validating files with Jhove validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator, Shell
from ipt.utils import parse_mimetype


NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, 'bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/jhove-apps-1.18.1.jar') + ':' + EXTRA_JARS


class JHoveBase(BaseValidator):
    """Base class for Jhove file format validator"""

    _supported_mimetypes = ['']
    _validate_methods = ["run_jhove", "check_mimetype", "check_well_formed",
                         "check_version"]

    def run_jhove(self):
        """Run JHove command and store XML output to self.report"""

        exec_cmd = [
            'jhove', '-h', 'XML', '-m',
            self._jhove_module, self.metadata_info['filename']]
        self.shell = Shell(exec_cmd)

        if self.shell.returncode != 0:
            self.errors("JHove returned error: %s\n%s" % (
                self.shell.returncode, self.shell.stderr))

        self.report = lxml.etree.fromstring(self.shell.stdout)

    def validate(self):
        """Run validation and compare technical metadata to given
           metadata_info"""
        # validate() is the same for the general case and *HTML objects, except
        # get_charset() needs to be run for *HTML.
        for method in self._validate_methods:
            getattr(self, method)()

        # Check validation outcome by comparing self.metadata_info and
        # self.validator_info dictionaries
        for key in self.metadata_info['format']:
            if key == 'alt-format':
                continue

            try:
                if self.metadata_info['format'][key] == \
                        self.validator_info['format'][key]:
                    self.messages('Validation %s check OK' % key)
                else:
                    self.errors(
                        'Metadata mismatch: found %s "%s", expected "%s"' %
                        (key,
                         self.validator_info['format'][key],
                         self.metadata_info['format'][key]))
            except KeyError:
                self.errors(
                    'The %s information could not be found from the JHove '
                    'report' % key)

    def check_well_formed(self):
        """Check_well_formed."""

        status = self.report_field("status")
        self.messages(status)

        if 'Well-Formed and valid' not in status:
            self.errors("Validator returned error: %s\n%s" % (
                self.shell.stdout, self.shell.stderr))

    def check_mimetype(self):
        """Save the mime type from JHOVE to our validator"""
        self.validator_info['format']['mimetype'] = \
            self.report_field('mimeType')

    def check_version(self):
        """Check if metadata_info version matches JHove output."""

        self.validator_info['format']['version'] = self.report_field("version")

    def report_field(self, field):
        """Return field value from JHoves XML output stored to self.report."""

        query = '//j:%s/text()' % field
        results = self.report.xpath(query, namespaces=NAMESPACES)
        return '\n'.join(results)


class JHoveGif(JHoveBase):
    """JHove GIF file format validator"""

    _supported_mimetypes = {
        'image/gif': ['1987a', '1989a']
    }

    _jhove_module = 'GIF-hul'

    def check_version(self):
        """Jhove returns the version as '87a' or '89a' but in mets.xml '1987a'
        or '1989a' is used. Hence '19' is prepended to the version returned by
        Jhove"""
        self.validator_info['format']['version'] = \
            '19' + self.report_field("version")


class JHoveHTML(JHoveBase):
    """Jhove HTML file format validator"""

    _supported_mimetypes = {
        'text/html': ['4.01'],
        'application/xhtml+xml': ['1.0', '1.1']
    }

    _validate_methods = ["run_jhove", "check_mimetype", "check_well_formed",
                         "check_version", "get_charset"]
    _jhove_module = 'HTML-hul'

    def check_mimetype(self):
        """JHOVE reports the XHTML MIME type as 'text/xml' but in mets.xml it's
        marked as 'application/xhtml+xml' which is more appropriate. If we're
        validating an XHTML file, use the MIME type from mets.xml. Otherwise
        call the same method in our superclass."""
        finfo_mimetype = self.metadata_info['format']['mimetype']
        if finfo_mimetype == "application/xhtml+xml":
            self.validator_info['format']['mimetype'] = finfo_mimetype
        else:
            super(JHoveHTML, self).check_mimetype()

    def check_version(self):
        """Jhove returns the version as 'HTML 4.01' but in mets.xml '4.01' is
        used. Hence we drop 'HTML ' prefix from the string returned by Jhove"""

        version = self.report_field("version")
        if len(version) > 0:
            version = version.split()[-1]
        self.validator_info['format']['version'] = version

    def get_charset_html(self):
        """Get the charset from the JHove report for HTML files and save it to
        self.validator_info"""
        query = '//j:property[j:name="Content"]//j:value/text()'
        results = self.report.xpath(query, namespaces=NAMESPACES)
        try:
            parsed = parse_mimetype(results[0])
            self.validator_info["format"]["charset"] = \
                parsed["format"]["charset"]
        except IndexError:
            # This will be handled by validate()
            pass

    def get_charset_xml(self):
        """Get the charset from the JHove report for XHTML files and save it to
        self.validator_info"""
        query = '//j:property[j:name="Encoding"]//j:value/text()'
        results = self.report.xpath(query, namespaces=NAMESPACES)
        try:
            self.validator_info["format"]["charset"] = results[0]
        except IndexError:
            # This will be handled by validate()
            pass

    def get_charset(self):
        """Get the charset from *HTML files"""
        if "xml" in self.metadata_info["format"]["mimetype"]:
            self.get_charset_xml()
        else:
            self.get_charset_html()


class JHoveJPEG(JHoveBase):
    """JHove validator for JPEG"""

    _supported_mimetypes = {
        'image/jpeg': [''],
    }

    _jhove_module = 'JPEG-hul'

    @classmethod
    def is_supported(cls, metadata_info):
        return metadata_info['format']['mimetype'] in cls._supported_mimetypes

    def check_version(self):
        # JHove doesn't detect JPEG file version so we assume that it's correct
        self.validator_info['format']['version'] = \
            self.metadata_info['format']['version']


class JHoveTiff(JHoveBase):
    """JHove validator for tiff"""

    _supported_mimetypes = {
        'image/tiff': ['6.0']
    }

    _jhove_module = 'TIFF-hul'

    def check_version(self):
        """
        Check if version string matches JHove output.
        :shell: shell utility tool
        """

        self.validator_info['format']['version'] = self.report_field("version")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self.validator_info['format']['version'] in ["4.0", "5.0", "6.0"]:
            self.validator_info['format']['version'] = self.metadata_info[
                'format']['version']


class JHovePDF(JHoveBase):
    """JHove validator for PDF"""

    _supported_mimetypes = {
        'application/pdf': ['1.2', '1.3', '1.4', '1.5', '1.6']
    }

    _jhove_module = 'PDF-hul'

    def check_version(self):
        """Check if version string matches JHove output."""

        self.validator_info['format']['version'] = self.report_field("version")


class JHoveTextUTF8(JHoveBase):
    """JHove validator for text/plain UTF-8."""

    _supported_mimetypes = {
        'text/csv': [''],
        'text/plain': [''],
        'text/xml': ['1.0'],
        'text/html': ['4.01', '5.0'],
        'application/xhtml+xml': ['1.0', '1.1']
    }

    _jhove_module = 'UTF8-hul'
    _validate_methods = ["run_jhove", "check_mimetype", "check_well_formed",
                         "check_version", "check_charset"]

    @classmethod
    def is_supported(cls, metadata_info):
        """
        Check suported mimetypes.
        :metadata_info: metadata_info
        """
        if metadata_info['format']['mimetype'] in cls._supported_mimetypes:
            if metadata_info['format']['charset'] != 'UTF-8':
                return False
        return super(JHoveTextUTF8, cls).is_supported(metadata_info)

    def check_mimetype(self):
        """We are only interested in charset"""
        self.validator_info['format']['mimetype'] = \
            self.metadata_info['format']['mimetype']

    def check_version(self):
        """We are only interested in charset"""
        if 'version' in self.metadata_info['format']:
            self.validator_info['format']['version'] = \
                self.metadata_info['format']['version']

    def check_charset(self):
        """Save the charset from JHOVE to our validator"""
        self.validator_info['format']['charset'] = self.report_field('format')
