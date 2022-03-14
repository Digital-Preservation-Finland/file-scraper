"""Digital preservation grading."""


from file_scraper.defaults import (
    UNAP,
    RECOMMENDED,
    ACCEPTABLE,
    BIT_LEVEL_WITH_RECOMMENDED,
    UNACCEPTABLE
)


class BaseGrader(object):
    """Base class for graders."""
    def __init__(self, scraper):
        """Initialize grader."""
        self.scraper = scraper

    @property
    def mimetype(self):
        """MIME type of the file to grade"""
        return self.scraper.mimetype

    @property
    def version(self):
        """MIME version of the file to grade"""
        return self.scraper.version

    @property
    def streams(self):
        """List of streams of the file to grade"""
        return self.scraper.streams

    @classmethod
    def is_supported(cls, mimetype):
        """Check whether grader is supported with given mimetype."""
        raise NotImplementedError

    def grade(self):
        """Determine and return digital preservation grade for the file."""
        raise NotImplementedError


class MIMEGrader(BaseGrader):
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
            "2.1.1": RECOMMENDED,
            "2.2": RECOMMENDED
        },
        "application/x-spss-por": {
            UNAP: RECOMMENDED
        },
        "application/matlab": {
            "7": RECOMMENDED,
            "7.3": RECOMMENDED
        },
        "application/x-hdf5": {
            "1.10": RECOMMENDED
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
            UNAP: ACCEPTABLE
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
        },
        "video/x.fi-dpres.prores": {
            UNAP: BIT_LEVEL_WITH_RECOMMENDED
        },
    }

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


class TextGrader(BaseGrader):
    """Grade file based on mimetype, version and charset."""

    formats = {
        "text/csv": {
            UNAP: RECOMMENDED
        },
        "application/xhtml+xml": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "5.0": RECOMMENDED,
            "5.1": RECOMMENDED,
            "5.2": RECOMMENDED
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
            "3.2.2": RECOMMENDED,
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


class ContainerGrader(BaseGrader):
    """
    Grade file based on container formats and what they're allowed to contain.

    Requirements based on DPRES File Formats specification 1.10.0, section 6,
    tables 2 and 3.
    """
    recommended_formats = {
        # Recommended
        "video/x-matroska": {
            # Audio
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),
            ("audio/flac", "1.2.1"),

            # Video
            ("video/x-ffv", "3"),
        },
        "video/MP2T": {
            # Audio
            ("audio/mp4", UNAP),

            # Video
            ("video/mp4", UNAP)
        },
        "video/mp4": {
            # Audio
            ("audio/mp4", UNAP),

            # Video
            ("video/mp4", UNAP)
        },
        "application/mxf": {
            # Audio
            ("audio/mp4", UNAP),
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),

            # Video
            ("video/mp4", UNAP),
            ("video/jpeg2000", UNAP),
        },
        "video/mj2": {
            # Audio
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),

            # Video
            ("video/jpeg2000", UNAP),
        },
        "video/quicktime": {
            # Audio
            ("audio/mp4", UNAP),
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),

            # Video
            ("video/mp4", UNAP),
            ("video/jpeg2000", UNAP),
        }
    }
    acceptable_formats = {
        # Acceptable
        "video/x-ms-asf": {
            # Audio
            ("audio/x-ms-wma", "9"),

            # Video
            ("video/x-ms-wmv", "9"),
        },
        "video/avi": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/dv": {
            # Audio
            ("audio/L16", UNAP),
            ("audio/L8", UNAP),
            ("audio/L20", UNAP),
            ("audio/L24", UNAP),

            # Video
            ("video/dv", UNAP)
        },
        "video/MP1S": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/MP2P": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/MP2T": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/mp4": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "application/mxf": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/quicktime": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        }
    }
    bit_level_recommended_formats = {
        "video/quicktime": {
            # Video
            ("video/x.fi-dpres.prores", UNAP),
        }
    }

    @classmethod
    def is_supported(cls, mimetype):
        """Check whether grader is supported with given mimetype."""
        return (
            mimetype in cls.recommended_formats
            or mimetype in cls.acceptable_formats
        )

    def grade(self):
        """Return digital preservation grade."""
        # First stream should be the container
        container = self.streams[0]
        container_mimetype = container["mimetype"]

        # Create a set of (mime_type, version) tuples
        # This makes it trivial to check which grade should be assigned
        # using set operations.
        contained_formats = set(
            (stream["mimetype"], stream["version"])
            for index, stream in self.streams.items()
            if index != 0
        )

        recommended = self.recommended_formats.get(container_mimetype, set())
        acceptable = self.acceptable_formats.get(container_mimetype, set())
        bit_level_recommended = self.bit_level_recommended_formats.get(
            container_mimetype, set()
        )

        formats_left_after_recommended = contained_formats - recommended
        formats_left_after_acceptable = (
            formats_left_after_recommended - acceptable
        )
        formats_left_after_bit_level_recommended = (
            formats_left_after_acceptable - bit_level_recommended
        )

        if not formats_left_after_recommended:
            # Only contains recommended formats or contains nothing at all
            grade = RECOMMENDED
        elif not formats_left_after_acceptable:
            # Contains at least one acceptable format
            grade = ACCEPTABLE
        elif not formats_left_after_bit_level_recommended:
            # Contains at least one bit_level_with_recommended format
            grade = BIT_LEVEL_WITH_RECOMMENDED
        else:
            # Contains at least one unacceptable format
            grade = UNACCEPTABLE

        return grade
