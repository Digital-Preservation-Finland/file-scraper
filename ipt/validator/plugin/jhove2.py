"""Module for vallidating files with JHove 2 Validator"""
import os
import tempfile
import lxml.etree

from ipt.validator.basevalidator import BaseValidator

JHOVE_MODULES = [
    'application/x-internet-archive',
    'text/plain',
    'application/warc'
]

NAMESPACES = {'j2': 'http://jhove2.org/xsd/1.0.0'}


class Jhove2(BaseValidator):

    """ Initializes JHove 2 validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.

        .. note:: The following mimetypes and JHove modules are supported:
                  'application/pdf': 'PDF-hul', 'image/tiff': 'TIFF-hul',
                  'image/jpeg': 'JPEG-hul', 'image/jp2': 'JPEG2000-hul',
                  'image/gif': 'GIF-hul'

        .. seealso:: http://jhove.sourceforge.net/documentation.html
    """

    def __init__(self, fileinfo):
        super(Jhove2, self).__init__(fileinfo)

        # Create temp dir for jhove
        tempdir = tempfile.mkdtemp()
        self.exec_cmd = ['jhove2',  '--display', 'XML', '--temp', tempdir]
        self.environment['JAVA_OPTS'] = "-Djava.io.tmpdir=%s" % tempdir

        if self.mimetype not in JHOVE_MODULES:
            raise Exception("Unknown mimetype: %s" % self.mimetype)

    def check_validity(self):
        """ Check if file is valid according to JHove output.

            Returns:
                None if file is valid, otherwise returns JHove's error message.
        """

        status = self.get_report_field("isValid")
        filename = self.get_report_field("repInfo")
        filename = os.path.basename(filename)

        if status != 'true':
            return "ERROR: File '%s' does not validate: %s" % (filename, status)

        return None

    def check_version(self, version):
        """ Check if version string matches JHove output.

            Arguments:
                version: version string

            Returns:
                None if version matches, else returns JHove's error message.
        """

        # If mimetype is text/plain don't check version. This validator can only
        # validate UTF-8 charset.
        if self.mimetype == 'text/plain':
            return None

        report_version = self.get_report_field("FileVersion")

        if report_version != version:
            return "ERROR: File version is '%s', expected '%s'" % (
                report_version,
                version)
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

        query = ""
        if self.mimetype == 'application/x-internet-archive':
            query = '//j2:feature[@ftid = "http://jhove2.org/terms/' \
                    'reportable/org/jhove2/module/format/arc/ArcModule"]/' \
                    'j2:features/j2:feature[@name="%s"]/j2:value/text()' % field
        elif self.mimetype == 'text/plain':
            query = '//j2:feature[@ftid = "http://jhove2.org/terms/' \
                    'reportable/org/jhove2/module/format/utf8/UTF8Module"]/' \
                    'j2:features/j2:feature[@name="%s"]/j2:value/text()' % field
        elif self.mimetype == 'application/warc':
            query = '//j2:feature[@ftid = "http://jhove2.org/terms/' \
                    'reportable/org/jhove2/module/format/warc/WarcModule"]/' \
                    'j2:features/j2:feature[@name="%s"]/j2:value/text()' % field
        results = root.xpath(query, namespaces=NAMESPACES)

        return '\n'.join(results)

    def validate(self):
        """This overrides Basevalidators validate() method because of
           https://jira.csc.fi/browse/KDKPAS-432 """

        (status, message, error) = super(Jhove2, self).validate()

        return status, "", error
