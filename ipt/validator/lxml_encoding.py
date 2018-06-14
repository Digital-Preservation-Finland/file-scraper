"""class for XML and HTML5 header encoding check with lxml. """

from lxml import etree

from ipt.validator.basevalidator import BaseValidator

class XmlEncoding(BaseValidator):
    """
    Character encoding validator for HTML5 and XML files
    """

    _supported_mimetypes = {
        'text/xml': ['1.0'],
        'text/html': ['5.0']
    }

    def validate(self):
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        fd = open(self.metadata_info['filename'])
        tree = etree.parse(fd, parser)
        if tree.docinfo.encoding == self.metadata_info['format']['charset']:
            self.messages('Encoding metadata match found.')
        else:
            self.errors(' '.join(
                'Encoding metadata mismatch:', tree.docinfo.encoding,
                'was found, but', self.metadata_info['format']['charset'],
                'was expected.'))
