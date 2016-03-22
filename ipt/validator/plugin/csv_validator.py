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

    def __init__(self, techmd):
        """
        :mimetype: mimetype of digital object.
        :filename: Full path of digital object.
        :techmd: Dictionary which
        """
        if techmd["mimetype"] != "text/csv":
            raise CsvValidationError(
                "Unknown mimetype: %s" % techmd["mimetype"])
        self.filename = str(techmd["filename"])
        self.mimetype = techmd["mimetype"]
        self.record_separator = techmd["separator"]
        self.delimiter = techmd["delimiter"]
        self.header_fields = techmd["header_fields"]
        self.charset = techmd["charset"]

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
