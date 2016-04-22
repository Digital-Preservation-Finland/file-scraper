"""Module for vallidating files with JHove 2 Validator"""
import subprocess
import tempfile
import lxml.etree

from ipt.validator.basevalidator import BaseValidator

NAMESPACES = {'j2': 'http://jhove2.org/xsd/1.0.0'}


class Jhove2Text(BaseValidator):

    """ Initializes JHove 2 validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.

        .. note:: The following mimetypes and JHove modules are supported:
                  'application/pdf': 'PDF-hul', 'image/tiff': 'TIFF-hul',
                  'image/jpeg': 'JPEG-hul', 'image/jp2': 'JPEG2000-hul',
                  'image/gif': 'GIF-hul'

        .. seealso:: http://jhove.sourceforge.net/documentation.html
    """

    _supported_mimetypes = {
        'text/plain': ['UTF-8'],
    }

    def __init__(self, fileinfo):
        super(Jhove2Text, self).__init__(fileinfo)
        self.charset = fileinfo['format']['charset']

    def validate(self):

        # Create temp dir for jhove
        tempdir = tempfile.mkdtemp()

        # Execute Jhove2
        cmd = ['jhove2',  '--display', 'XML', '--temp', tempdir]
        environment = {
            'JAVA_OPTS': "-Djava.io.tmpdir=%s" % tempdir
        }

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=environment)

        (stdout, stderr) = proc.communicate()
        returncode = proc.returncode

        # Determine validity
        self._is_valid = bool(returncode)

        self._check_report()
        self._check_version()
        self._check_charset()

    def _check_report(self):
        if self.get_report_field("isValid") != 'true':
            self.errors.append("ERROR: File '%s' does not validate: %s" % (filename, status))


    def _check_version(self):
        if self._get_report_field("FileVersion") != self.version:
            return "ERROR: File version is '%s', expected '%s'" % (
                report_version,
                version)


    def _check_charset(self):
        """Check text files' charset matches with given charset."""

        root = lxml.etree.fromstring(self.stdout)

        query = '//j2:feature[@fid = "http://jhove2.org/terms/' \
            'property/org/jhove2/core/format/Format/Name"]/j2:value/text()'
        results = root.xpath(query, namespaces=NAMESPACES)

        if self.charset not in results:
            return False


    def _get_report_field(self, field):
        """

        """
        root = lxml.etree.fromstring(self.stdout)
        query = '//j2:feature[@ftid = "http://jhove2.org/terms/' \
                    'reportable/org/jhove2/module/format/utf8/UTF8Module"]/' \
                    'j2:features/j2:feature[@name="%s"]/j2:value/text()' % field

        results = root.xpath(query, namespaces=NAMESPACES)
        return '\n'.join(results)
