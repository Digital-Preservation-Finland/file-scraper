"""The CSV validator plugin"""
import csv

from ipt.validator.basevalidator import BaseValidator


class CsvValidationError(Exception):
    """CSV validation error"""
    pass


class PythonCsv(BaseValidator):
    """The CSV validator plugin"""

    _supported_mimetypes = {
        'text/csv': [''],
    }

    def __init__(self, fileinfo):
        super(PythonCsv, self).__init__(fileinfo)
        self.filename = fileinfo['filename']
        self.charset = fileinfo['addml']['charset']
        self.record_separator = fileinfo['addml']['separator']
        self.delimiter = fileinfo['addml']['delimiter']
        self.header_fields = fileinfo['addml']['header_fields']

    def validate(self):
        """Try to read CSV file through cvs.reader and if that can be done file
        is valid.
        :returns: (statuscode, messages, errors)
        """

        class _Dialect(csv.excel):
            """Init dialect, example from Python csv.py library"""
            strict = True
            delimiter = self.delimiter
            doublequote = True
            lineterminator = self.record_separator

        try:
            with open(self.filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, _Dialect)
                first_line = reader.next()
                if self.header_fields and not self.header_fields == first_line:
                    self.errors("CSV validation error: no header at "
                                "first line")
                    return
                for _ in reader:
                    pass

        except csv.Error as exception:
            self.errors("CSV validation error on line %s: %s" %
                        (reader.line_num, exception))
            return
        self.messages("CSV validation OK")
