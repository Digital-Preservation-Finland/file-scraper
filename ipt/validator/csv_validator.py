"""The CSV validator plugin"""
import csv

from ipt.validator.basevalidator import BaseValidator


class CsvValidationError(Exception):
    """CSV validation error"""
    pass


class PythonCsv(BaseValidator):
    """The CSV validator plugin"""

    _supported_mimetypes = {
        'text/csv': ['UTF-8'],
    }

    def __init__(self, fileinfo):
        super(PythonCsv, self).__init__(fileinfo)
        self.charset = fileinfo['format']['charset']

        self.record_separator = fileinfo['addml']['separator']
        self.delimiter = fileinfo['addml']['delimiter']
        self.header_fields = fileinfo['addml']['header_fields']

    def validate(self):
        """Try to read CSV file through cvs.reader and if that can be done file
        is valid.
        :returns: (statuscode, messages, errors)
        """

        dialect = dialect_factory(self.record_separator, self.delimiter)

        try:
            with open(self.filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, dialect)
                first_line = reader.next()
                if self.header_fields and not self.header_fields == first_line:

                    self.not_valid()
                    self.errors.append("CSV validation error: no header at "
                                       "first line")
                for _ in reader:
                    pass

        except csv.Error as exception:
            self.not_valid()
            self.errors.append("CSV validation error on line %s: %s" %
                               (reader.line_num, exception))

        return (self.is_valid(),
                ("\n".join(message) for message in self.messages()),
                ("\n".join(error) for error in self.errors()))


def dialect_factory(record_separator, delimiter):
    """A factory pattern for creating dialect class.
    :record_separator: csv line separator
    :delimiter: a character separating different items within a record.
    :returns: a csv Dialect class."""

    class StrictDialect(csv.excel):
        """A strict csv dialect.
        This should work in Python 2.6 although it's only documented in 2.7"""
        def __init__(self):
            super(csv.excel, self).__init__()
            self.strict = True
            self.delimiter = delimiter
            self.lineterminator = record_separator

    return StrictDialect
