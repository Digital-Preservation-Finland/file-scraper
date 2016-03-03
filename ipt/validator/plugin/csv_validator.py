"""The CSV validator plugin"""
import csv


class StrictDialect(csv.excel):
    """A strict csv dialect.
    This should work in Python 2.6 although it's only documented in 2.7"""
    strict = True


class CsvValidationError(Exception):
    """CSV validation error"""
    pass


class Csv(object):
    """The CSV validator plugin"""

    def __init__(self, mimetype, fileversion, filename):
        if mimetype != "text/csv":
            raise CsvValidationError("Unknown mimetype: %s" % mimetype)
        self.filename = str(filename)
        self.fileversion = fileversion
        self.mimetype = mimetype

    def validate(self):
        """The actual validation. Runs the CSV file through cvs.reader and
        returns (statuscode, messages, errors)
        """
        try:
            with open(self.filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, StrictDialect)
                for _ in reader:
                    pass
            return (0, "", "")
        except csv.Error, err:
            return (1, "", "CSV validation error on line %s: %s" %
                    (reader.line_num, err))
