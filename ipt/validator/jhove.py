"""Module for validating files with Jhove validator"""
import os
import lxml.etree

from ipt.validator.basevalidator import BaseValidator, Shell


NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, 'bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/JhoveApp.jar') + ':' + EXTRA_JARS


class JHoveBase(BaseValidator):
    """Base class for Jhove file format validator"""

    _supported_mimetypes = ['']

    def run_jhove(self):
        """Run JHove command and store XML output to self.report"""

        exec_cmd = [
            'java', '-classpath', CP, 'Jhove', '-h', 'XML', '-m',
            self._jhove_module, self.fileinfo['filename']]
        self.shell = Shell(exec_cmd)

        if self.shell.returncode != 0:
            self.errors("JHove returned error: %s\n%s" % (
                self.shell.returncode, self.shell.stderr))

        self.report = lxml.etree.fromstring(self.shell.stdout)

    def validate(self):
        """Run validation and compare technical metadata to given fileinfo"""

        self.run_jhove()
        self.check_mimetype()
        self.check_well_formed()
        self.check_version()

        # Check validation outcome by comparing self.fileinfo and self._techmd
        # dictionaries
        for key in self.fileinfo['format']:
            if key == 'alt-format':
                continue

            if self.fileinfo['format'][key] == self._techmd['format'][key]:
                self.messages('Validation %s check OK' % key)
            else:
                self.errors('Metadata mismatch: found %s "%s", expected "%s"' %
                            (key,
                             self._techmd['format'][key],
                             self.fileinfo['format'][key]))

    def check_well_formed(self):
        """Check_well_formed."""

        status = self.report_field("status")
        self.messages(status)

        if 'Well-Formed and valid' not in status:
            self.errors("Validator returned error: %s\n%s" % (
                self.shell.stdout, self.shell.stderr))

    def check_mimetype(self):
        """Save the mime type from JHOVE to our validator"""
        self._techmd['format']['mimetype'] = self.report_field('mimeType')

    def check_version(self):
        """Check if fileinfo version matches JHove output."""

        self._techmd['format']['version'] = self.report_field("version")

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


class JHoveHTML(JHoveBase):
    """Jhove HTML file format validator"""

    _supported_mimetypes = {
        'text/html': ['4.01'],
        'application/xhtml+xml': ['1.0', '1.1']
    }

    _jhove_module = 'HTML-hul'

    def check_mimetype(self):
        """JHOVE reports the XHTML MIME type as 'text/xml' but in mets.xml it's
        marked as 'application/xhtml+xml' which is more appropriate. If we're
        validating an XHTML file, use the MIME type from mets.xml. Otherwise
        call the same method in our superclass."""
        finfo_mimetype = self.fileinfo['format']['mimetype']
        if finfo_mimetype == "application/xhtml+xml":
            self._techmd['format']['mimetype'] = finfo_mimetype
        else:
            super(JHoveHTML, self).check_mimetype()


class JHoveJPEG(JHoveBase):
    """JHove validator for JPEG"""

    _supported_mimetypes = {
        'image/jpeg': [''],
    }

    _jhove_module = 'JPEG-hul'

    @classmethod
    def is_supported(cls, fileinfo):
        return fileinfo['format']['mimetype'] in cls._supported_mimetypes

    def check_version(self):
        # JHove doesn't detech JPEG file version so we assume that it's correct
        self._techmd['format']['version'] = self.fileinfo['format']['version']


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

        self._techmd['format']['version'] = self.report_field("version")
        # There is no version tag in TIFF images.
        # TIFF 4.0 and 5.0 is also valid TIFF 6.0.
        if self._techmd['format']['version'] in ["4.0", "5.0", "6.0"]:
            self._techmd['format']['version'] = self.fileinfo[
                'format']['version']


class JHovePDF(JHoveBase):
    """JHove validator for PDF"""

    _supported_mimetypes = {
        'application/pdf': ['1.2', '1.3', '1.4', '1.5', '1.6', 'A-1a', 'A-1b']
    }

    _jhove_module = 'PDF-hul'

    def check_version(self):
        """Check if version string matches JHove output."""

        self._techmd['format']['version'] = self.report_field("version")

        # PDF-A versions are subsets of 1.4 so patch 1.4 to be found PDF-A1/B
        # if claimed
        if self.fileinfo['format']['version'] in ['A-1a', 'A-1b']:
            if 'A-1' in self.report_field('profile'):
                self._techmd['format']['version'] = self.fileinfo[
                    'format']['version']


class JHoveTextUTF8(JHoveBase):
    """JHove validator for text/plain UTF-8."""

    _supported_mimetypes = {
        'text/plain': ['']
    }

    _jhove_module = 'UTF8-hul'

    @classmethod
    def is_supported(cls, fileinfo):
        """
        Check suported mimetypes.
        :fileinfo: fileinfo
        """
        if fileinfo['format']['mimetype'] == 'text/plain':
            if fileinfo['format']['charset'] == 'UTF-8':
                return True
        return False

    def check_mimetype(self):
        """Save the mimetype from JHOVE to our validator"""
        self._techmd['format']['mimetype'] = \
            self.report_field('mimeType').split(';')[0]

    def check_charset(self):
        """Save the charset from JHOVE to our validator"""
        self._techmd['format']['charset'] = self.report_field('format')

    def validate(self):
        self.run_jhove()
        self.check_charset()
        super(self.__class__, self).validate()
