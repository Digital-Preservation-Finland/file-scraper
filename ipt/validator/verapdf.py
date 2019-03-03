"""
This is an PDF/A validator.
"""

import lxml.etree as ET
from ipt.validator.basevalidator import BaseValidator, Shell


VERAPDF_PATH = '/usr/share/java/verapdf/verapdf'


class VeraPDF(BaseValidator):
    """
    PDF/A validator
    """
    _supported_mimetypes = {
        "application/pdf": ['A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a',
                            'A-3b', 'A-3u']
    }

    def validate(self):
        """
        Validate file and version by passing the version from the METS
        metadata_info data as a flavour argument to the validator which
        selects a specific validation profile for the stated version.
        The validator returns an XML validation report to stdout. If the
        file is not valid or the version is not compliant with the
        selected validation profile the validation report is sent to
        stderr.
        """
        flavour = self.metadata_info['format']['version'][-2:]
        cmd = [
            VERAPDF_PATH, '-f', flavour, self.metadata_info['filename']]
        shell = Shell(cmd)
        if shell.returncode != 0:
            raise VeraPDFError(shell.stderr)
        self.messages(shell.stdout)

        try:
            report = ET.fromstring(shell.stdout)
            if report.xpath('//batchSummary')[0].get('failedToParse') == '0':
                valid = report.xpath(
                    '//validationReport')[0].get('isCompliant')
                if valid == 'false':
                    self.errors(shell.stdout)
            else:
                self.errors(shell.stdout)
        except ET.XMLSyntaxError:
            self.errors(shell.stderr)


class VeraPDFError(Exception):
    """
    VeraPDF Error
    """
    pass
