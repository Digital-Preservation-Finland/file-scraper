"""Digital preservation grading."""


from file_scraper.defaults import (
    UNAP,
    UNKN,
    RECOMMENDED,
    ACCEPTABLE,
    BIT_LEVEL_WITH_RECOMMENDED,
    BIT_LEVEL,
    UNACCEPTABLE
)


class BaseGrader:
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
            "3": RECOMMENDED
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
        "application/geopackage+sqlite3": {
            "1.3.0": RECOMMENDED,
            "1.3.1": RECOMMENDED
        },
        "application/matlab": {
            "7": RECOMMENDED,
            "7.3": RECOMMENDED
        },
        "application/msword": {
            "97-2003": ACCEPTABLE
        },
        "application/mxf": {  # Container
            UNAP: RECOMMENDED
        },
        "application/postscript": {
            "3.0": ACCEPTABLE
        },
        "application/vnd.ms-excel": {
            "8": ACCEPTABLE,
            "8X": ACCEPTABLE
        },
        "application/vnd.ms-powerpoint": {
            "97-2003": ACCEPTABLE
        },
        "application/vnd.oasis.opendocument.formula": {
            "1.0": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.graphics": {
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
        "application/vnd.oasis.opendocument.spreadsheet": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.oasis.opendocument.text": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED
        },
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": {
            "2007 onwards": ACCEPTABLE
        },
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
            "2007 onwards": ACCEPTABLE
        },
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": {
            "2007 onwards": ACCEPTABLE
        },
        "application/warc": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED
        },
        "application/x.fi-dpres.atlproj": {
            "(:unap)": BIT_LEVEL_WITH_RECOMMENDED
        },
        "application/x.fi-dpres.segy": {
            "1.0": BIT_LEVEL,
            "2.0": BIT_LEVEL,
            UNKN: BIT_LEVEL
        },
        "application/x-hdf5": {
            "1.10": RECOMMENDED
        },
        "application/x-siard": {
            "2.1.1": RECOMMENDED,
            "2.2": RECOMMENDED
        },
        "application/x-spss-por": {
            UNAP: RECOMMENDED
        },
        "audio/aac": {
            UNAP: RECOMMENDED
        },
        "audio/flac": {
            UNAP: RECOMMENDED
        },
        "audio/l8": {
            UNAP: RECOMMENDED
        },
        "audio/l16": {
            UNAP: RECOMMENDED
        },
        "audio/l20": {
            UNAP: RECOMMENDED
        },
        "audio/l24": {
            UNAP: RECOMMENDED
        },
        "audio/mp4": {  # Container
            UNAP: RECOMMENDED
        },
        "audio/mpeg": {
            "1": ACCEPTABLE,
            "2": ACCEPTABLE
        },
        "audio/x-aiff": {
            UNAP: ACCEPTABLE,  # AIFF-C
            "1.3": RECOMMENDED  # AIFF
        },
        "audio/x-ms-wma": {
            "9": ACCEPTABLE
        },
        "audio/x-wav": {
            UNAP: RECOMMENDED,  # WAV
            "2": RECOMMENDED  # BWF
        },
        "image/gif": {
            "1987a": ACCEPTABLE,
            "1989a": ACCEPTABLE
        },
        "image/jp2": {
            UNAP: RECOMMENDED
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
        "image/png": {
            "1.2": RECOMMENDED
        },
        "image/svg+xml": {
            "1.1": RECOMMENDED
        },
        "image/tiff": {
            "6.0": RECOMMENDED,  # TIFF
            "1.0": RECOMMENDED,  # GeoTiff
        },
        "image/webp": {
            UNAP: RECOMMENDED
        },
        "image/x-adobe-dng": {
            "1.1": RECOMMENDED,
            "1.2": RECOMMENDED,
            "1.3": RECOMMENDED,
            "1.4": RECOMMENDED,
            "1.5": RECOMMENDED
        },
        "image/x-dpx": {
            "1.0": ACCEPTABLE,  # Allowed for special case
            "2.0": RECOMMENDED
        },
        "model/step": {
            "4.0.2.1": RECOMMENDED,
            "4.3.2.0": RECOMMENDED
        },
        "video/avi": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/dv": {
            UNAP: ACCEPTABLE
        },
        "video/h264": {
            UNAP: RECOMMENDED
        },
        "video/h265": {
            UNAP: RECOMMENDED
        },
        "video/jpeg2000": {
            UNAP: RECOMMENDED
        },
        "video/mj2": {  # Container
            UNAP: RECOMMENDED
        },
        "video/mp1s": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/mp2p": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/mp2t": {  # Container
            UNAP: RECOMMENDED
        },
        "video/mp4": {  # Container
            UNAP: RECOMMENDED
        },
        "video/mpeg": {
            "1": ACCEPTABLE,
            "2": ACCEPTABLE
        },
        "video/quicktime": {  # Container
            UNAP: RECOMMENDED
        },
        "video/x.fi-dpres.prores": {
            UNAP: BIT_LEVEL_WITH_RECOMMENDED
        },
        "video/x-ffv": {
            "3": RECOMMENDED
        },
        "video/x-matroska": {  # Container
            "4": RECOMMENDED
        },
        "video/x-ms-asf": {  # Container
            UNAP: ACCEPTABLE
        },
        "video/x-ms-wmv": {
            "9": ACCEPTABLE
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
        "application/xhtml+xml": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED,
            "5": RECOMMENDED
        },
        "application/gml+xml": {
            "3.2.2": RECOMMENDED,
        },
        "application/vnd.google-earth.kml+xml": {
            "2.3": RECOMMENDED,
        },
        "text/csv": {
            UNAP: RECOMMENDED
        },
        "text/html": {
            "4.01": RECOMMENDED,
            "5": RECOMMENDED
        },
        "text/plain": {
            UNAP: RECOMMENDED
        },
        "text/xml": {
            "1.0": RECOMMENDED,
            "1.1": RECOMMENDED
        },
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


class ContainerStreamsGrader(BaseGrader):
    """
    Grade file based on what certain containers are allowed to contain.
    This grader does not check the grade of the container itself, the grade
    of the container should be evaluated by MIMEGrader.

    Requirements based on DPRES File Formats specification 1.11.0, section 6,
    tables 2 and 3.
    """
    recommended_formats = {
        # Recommended
        "application/mxf": {
            # Audio
            ("audio/aac", UNAP),
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/h264", UNAP),
            ("video/jpeg2000", UNAP),
        },
        "audio/mp4": {
            ("audio/aac", UNAP)
        },
        "video/mj2": {
            # Audio
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/jpeg2000", UNAP),
        },
        "video/mp2t": {
            # Audio
            ("audio/aac", UNAP),

            # Video
            ("video/h264", UNAP),
            ("video/h265", UNAP)
        },
        "video/mp4": {
            # Audio
            ("audio/aac", UNAP),

            # Video
            ("video/h264", UNAP),
            ("video/h265", UNAP)
        },
        "video/quicktime": {
            # Audio
            ("audio/aac", UNAP),
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/h264", UNAP),
            ("video/h265", UNAP),
            ("video/jpeg2000", UNAP),
        },
        "video/x-matroska": {
            # Audio
            ("audio/flac", UNAP),
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/h265", UNAP),
            ("video/x-ffv", "3")
        },
    }
    acceptable_formats = {
        # Acceptable
        "application/mxf": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/avi": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/dv": {
            # Audio
            ("audio/l8", UNAP),
            ("audio/l16", UNAP),
            ("audio/l20", UNAP),
            ("audio/l24", UNAP),

            # Video
            ("video/dv", UNAP)
        },
        "video/mp1s": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/mp2p": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/mp2t": {
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
        "video/quicktime": {
            # Audio
            ("audio/mpeg", "1"),
            ("audio/mpeg", "2"),

            # Video
            ("video/dv", UNAP),
            ("video/mpeg", "1"),
            ("video/mpeg", "2"),
        },
        "video/x-ms-asf": {
            # Audio
            ("audio/x-ms-wma", "9"),

            # Video
            ("video/x-ms-wmv", "9"),
        },
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
        contained_formats = {
            (stream["mimetype"], stream["version"])
            for index, stream in self.streams.items()
            if index != 0
        }

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
