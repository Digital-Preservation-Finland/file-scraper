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

    def __init__(self, metadata_info):
        super(PythonCsv, self).__init__(metadata_info)

        self.filename = metadata_info['filename']

        if "addml" in metadata_info:
            self.charset = metadata_info['addml']['charset']
            self.record_separator = metadata_info['addml']['separator']
            self.delimiter = metadata_info['addml']['delimiter']
            self.header_fields = metadata_info['addml']['header_fields']

    def validate(self):
        """Try to read CSV file through cvs.reader and if that can be done file
        is valid.
        :returns: (statuscode, messages, errors)
        """
        # TODO: This issue involves all validators that use ADDML
        # Fix this issue more generically if it becomes more widespread
        if "addml" not in self.metadata_info:
            self.errors("ADDML data was expected, but not found")
            return

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

                if len(self.header_fields) > 0 and \
                        len(self.header_fields) != len(first_line):
                    self.errors(
                        "CSV validation error: field counts in the ADDML "
                        "document and the CSV header don't match"
                    )
                    return
                for _ in reader:
                    pass

        except csv.Error as exception:
            self.errors("CSV validation error on line %s: %s" %
                        (reader.line_num, exception))
            return
        self.messages("CSV validation OK")
