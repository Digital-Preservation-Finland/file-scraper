"""The CSV validator plugin"""
import csv


class CsvValidationError(Exception):
    """CSV validation error"""
    pass


class Csv(object):
    """The CSV validator plugin"""

    def __init__(self, techmd):
        """
        :techmd: Dictionary which holds techical metadata.
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
        :returns: (statuscode, messages, errors)
        """
        try:
            dialect = dialect_factory(self.record_separator, self.delimiter)
            with open(self.filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, dialect)
                first_line = reader.next()
                if self.header_fields and not self.header_fields == first_line:
                    return (117, "",
                        "CSV validation error on line 1, header mismatch")
                for _ in reader:
                    pass
            return (0, "", "")
        except csv.Error, err:
            return (117, "", "CSV validation error on line %s: %s" %
                    (reader.line_num, err))


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
