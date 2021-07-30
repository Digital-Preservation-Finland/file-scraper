"""Digital preservation grading."""


from file_scraper.defaults import UNAP, RECOMMENDED, ACCEPTABLE, UNACCEPTABLE


class Grader():
    """Grade file based on mimetype and version."""

    formats = {
        "application/epub+zip": {
            "2.0.1": RECOMMENDED,
            "3.0.0": RECOMMENDED,
            "3.0.1": RECOMMENDED,
            "3.2": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.text": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.spreadsheet": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.presentation": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.graphics": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.formula": {
            "1.0": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/pdf": {
            "A-1a": RECOMMENDED,
            "A-1b": RECOMMENDED,
            "A-2a": RECOMMENDED,
            "A-2b": RECOMMENDED,
            "A-2u": RECOMMENDED,
            "A-3a": RECOMMENDED,
            "A-3b": RECOMMENDED,
            "A-3u": RECOMMENDED,
            "1.2": ACCEPTABLE,
            "1.3": ACCEPTABLE,
            "1.4": ACCEPTABLE,
            "1.5": ACCEPTABLE,
            "1.6": ACCEPTABLE,
            "1.7": ACCEPTABLE
        },
        "audio/x-aiff": {
            UNAP: ACCEPTABLE,  # AIFF-C
            "1.3": RECOMMENDED  # AIFF
        },
        "audio/x-wav": {
            UNAP: RECOMMENDED,  # WAV
            "2": RECOMMENDED  # BWF
        },
        "audio/flac": {
            "1.2.1": RECOMMENDED
        },
        "audio/L8": {
            UNAP: RECOMMENDED
        },
        "audio/L16": {
            UNAP: RECOMMENDED
        },
        "audio/L20": {
            UNAP: RECOMMENDED
        },
        "audio/L24": {
            UNAP: RECOMMENDED
        },
        "audio/mp4": {
            UNAP: RECOMMENDED
        },
        "image/x-dpx": {
            "2.0": RECOMMENDED
        },
        "video/x-ffv": {
            "3": RECOMMENDED
        },
        "video/jpeg2000": {
            UNAP: RECOMMENDED
        },
        "video/mp4": {
            UNAP: RECOMMENDED
        },
        "image/tiff": {
            "1.3": RECOMMENDED,  # DNG
            "1.4": RECOMMENDED,  # DNG
            "1.5": RECOMMENDED,  # DNG
            "6.0": RECOMMENDED,  # TIFF
            "1.0": RECOMMENDED,  # GeoTiff
        },
        "image/jpeg": {
            "1.00": RECOMMENDED,
            "1.01": RECOMMENDED,
            "1.02": RECOMMENDED,
            "2.0": RECOMMENDED,  # JPEG/EXIF
            "2.1": RECOMMENDED,  # JPEG/EXIF
            "2.2": RECOMMENDED,  # JPEG/EXIF
            "2.2.1": RECOMMENDED,  # JPEG/EXIF
            "2.3": RECOMMENDED,  # JPEG/EXIF
            "2.3.1": RECOMMENDED,  # JPEG/EXIF
            "2.3.2": RECOMMENDED,  # JPEG/EXIF
        },
        "image/jp2": {
            UNAP: RECOMMENDED
        },
        "image/svg+xml": {
            "1.1": RECOMMENDED
        },
        "image/png": {
            "1.2": RECOMMENDED
        },
        "application/warc": {
            "1.0": RECOMMENDED
        },
        "application/x-siard": {
            "2.0": RECOMMENDED,
            "2.1": RECOMMENDED
        },
        "application/x-spss-por": {
            UNAP: RECOMMENDED
        },
        "application/matlab": {
            "7": RECOMMENDED,
            "7.3": RECOMMENDED
        },
        "application/x-hdf5": {
            "1.1": RECOMMENDED
        },
        "application/msword": {
            "97-2003": ACCEPTABLE
        },
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": {
            "2007 onwards": ACCEPTABLE
        },
        "application/vnd.ms-excel": {
            "8": ACCEPTABLE,
            "8X": ACCEPTABLE
        },
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
            "2007 onwards": ACCEPTABLE
        },
        "application/vnd.ms-powerpoint": {
            "97-2003": ACCEPTABLE
        },
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": {
            "2007 onwards": ACCEPTABLE
        },
        "audio/mpeg": {
            "1": ACCEPTABLE,
            "2": ACCEPTABLE
        },
        "audio/x-ms-wma": {
            "9": ACCEPTABLE
        },
        "video/dv": {
            UNAP: ACCEPTABLE
        },
        "video/mpeg": {
            "1": ACCEPTABLE,
            "2": ACCEPTABLE
        },
        "video/x-ms-wmv": {
            "9": ACCEPTABLE
        },
        "application/postscript": {
            "3.0": ACCEPTABLE
        },
        "image/gif": {
            "1987a": ACCEPTABLE,
            "1989a": ACCEPTABLE
        },
        "video/avi": {  # Container
            UNAP: RECOMMENDED
        },
        "video/x-matroska": {  # Container
            "4": RECOMMENDED
        },
        "video/MP2T": {  # Container
            UNAP: RECOMMENDED
        },
        "application/mxf": {  # Container
            UNAP: RECOMMENDED
        },
        "video/mj2": {  # Container
            UNAP: RECOMMENDED
        },
        "video/quicktime": {  # Container
            UNAP: RECOMMENDED
        },
        "video/x-ms-asf": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/MP1S": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/MP2P": {  # Container
            UNAP: ACCEPTABLE
        }
    }

    def __init__(self, mimetype, version, streams):
        """Initialize grader."""
        self.mimetype = mimetype
        self.version = version
        self.streams = streams

    @classmethod
    def is_supported(cls, mimetype):
        """Check whether grader is supported with given mimetype."""
        return mimetype in cls.formats

    def grade(self):
        """Return digital preservation grade."""
        try:
            grade = self.formats[self.mimetype][self.version]
        except KeyError:
            grade = UNACCEPTABLE

        return grade


class TextGrader(Grader):
    """Grade file based on mimetype, version and charset."""

    formats = {
        "text/csv": {
            UNAP: RECOMMENDED
        },
        "application/xhtml+xml": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "5.0": RECOMMENDED
        },
        "text/xml": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED
        },
        "text/html": {
            "4.01": RECOMMENDED,
            "5.0": RECOMMENDED,
            "5.1": RECOMMENDED,
            "5.2": RECOMMENDED
        },
        "text/plain": {
            UNAP: RECOMMENDED
        },
        "application/gml+xml": {
            "3.2.1": RECOMMENDED,
        },
        "application/vnd.google-earth.kml+xml": {
            "2.3": RECOMMENDED,
        }
    }

    allowed_charsets = ['ISO-8859-15', 'UTF-8', 'UTF-16', 'UTF-32']

    @classmethod
    def is_supported(cls, mimetype):
        """Check whether grader is supported with given mimetype."""
        return mimetype in cls.formats

    def grade(self):
        """Return digital preservation grade."""
        try:
            grade = self.formats[self.mimetype][self.version]
        except KeyError:
            grade = UNACCEPTABLE

        for stream in self.streams.values():
            if stream['charset'] not in self.allowed_charsets:
                grade = UNACCEPTABLE

        return grade
