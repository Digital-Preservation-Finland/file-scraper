"""
This is an PDF/A validator.
"""

import os
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
        Validate file
        """
        flavour = self.fileinfo['format']['version'][-2:]
        cmd = [
            VERAPDF_PATH, '-f', flavour, self.fileinfo['filename']]
        shell = Shell(cmd)
        self.errors(shell.stderr)
        self.messages(shell.stdout)
        report = ET.fromstring(shell.stdout)
        if report.xpath('//batchSummary')[0].get('failedToParse') == '0':
            valid = report.xpath('//validationReport')[0].get('isCompliant')
            if valid == 'false':
                self.errors(
                    report.xpath('//validationReport')[0].get(
                        'statement') + " " + shell.stdout)

            #self.validate_version(report)


    def validate_version(self, report):
        """Checks the version of the file by reading the validation
        report and extracting the validation profile used by the
        validator. Then compares the version with the supplied fileinfo
        and writes to self.errors if the versions don't match.
        """
        conversion = {'PDF/A-1A': 'A-1a', 'PDF/A-1B': 'A-1b',
                      'PDF/A-2A': 'A-2a', 'PDF/A-2B': 'A-2b',
                      'PDF/A-2U': 'A-2u', 'PDF/A-3A': 'A-3a',
                      'PDF/A-3B': 'A-3b', 'PDF/A-3U': 'A-3u'
                      }
        profile = report.xpath('//validationReport')[0].get('profileName')
        version = conversion.get(profile.split()[0])
        if version != self.fileinfo['format']['version']:
            self.errors(
                    'Wrong version detected, got %s version %s, expected '
                    '%s version %s.\n%s' % (
                        self.fileinfo['format']['mimetype'], version,
                        self.fileinfo['format']['mimetype'],
                        self.fileinfo['format']['version'], report)
                    )
