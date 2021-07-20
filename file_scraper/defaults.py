"""Common constants and dictionaries."""
from __future__ import unicode_literals

# Prioritize these pronom codes in identification.
# fmt/289 could possibly be removed when fmt/1355 is known by FIDO.
PRIORITY_PRONOM = [
    "fmt/3", "fmt/4", "fmt/5", "fmt/13", "fmt/16", "fmt/17", "fmt/18",
    "fmt/19", "fmt/20", "fmt/40", "fmt/42", "fmt/43", "fmt/44", "fmt/61",
    "fmt/62", "fmt/92", "fmt/95", "fmt/100", "fmt/101", "fmt/102", "fmt/103",
    "fmt/124", "fmt/126", "fmt/131", "fmt/132", "fmt/133", "fmt/134",
    "fmt/136", "fmt/137", "fmt/138", "fmt/139", "fmt/141", "fmt/155",
    "fmt/199", "fmt/199", "fmt/214", "fmt/215", "fmt/224", "fmt/276",
    "fmt/279", "fmt/286", "fmt/287", "fmt/289", "fmt/290", "fmt/291",
    "fmt/292", "fmt/293", "fmt/294", "fmt/295", "fmt/296", "fmt/297",
    "fmt/337", "fmt/353", "fmt/354", "fmt/412", "fmt/438", "fmt/471",
    "fmt/476", "fmt/477", "fmt/478", "fmt/479", "fmt/480", "fmt/481",
    "fmt/483", "fmt/527", "fmt/541", "fmt/569", "fmt/585", "fmt/640",
    "fmt/645", "fmt/649", "fmt/730", "fmt/806", "fmt/807", "fmt/828",
    "fmt/995", "fmt/997", "fmt/1047", "fmt/1196", "fmt/1355",
    "x-fmt/18", "x-fmt/111", "x-fmt/135", "x-fmt/136", "x-fmt/152",
    "x-fmt/384", "x-fmt/385", "x-fmt/386", "x-fmt/390", "x-fmt/391",
    "x-fmt/392", "x-fmt/392", "x-fmt/398"]

# Dict between detectors' results and known mimetypes.
MIMETYPE_DICT = {
    "application/xml": "text/xml",
    "application/mp4": None,
    "application/vnd.ms-asf": "video/x-ms-asf",
    "video/x-msvideo": "video/avi",
}

# Dict between detectors' results and known file format versions.
VERSION_DICT = {
    "text/html": {"5": "5.0"},
    "application/pdf": {"1a": "A-1a", "1b": "A-1b",
                        "2a": "A-2a", "2b": "A-2b", "2u": "A-2u",
                        "3a": "A-3a", "3b": "A-3b", "3u": "A-3u"},
    "audio/x-wav": {"2 Generic": "2"},
}

# Dict between detectors' pronom results and known mimetypes and versions.
# fmt/289 might be need to change to fmt/1355 when supported by FIDO.
PRONOM_DICT = {
    "x-fmt/135": ("audio/x-aiff", "1.3"),
    "fmt/541": ("image/x-dpx", "2.0"),
    "fmt/289": ("application/warc", None),  # does not result version
    "fmt/244": ("application/vnd.google-earth.kml+xml", "2.3"),
    "fmt/997": ("application/x-spss-por", ""),
    "fmt/649": ("video/mpeg", "1"),
    "fmt/640": ("video/mpeg", "2"),
    "x-fmt/385": ("video/MP1S", ""),
    "x-fmt/386": ("video/MP2P", ""),
    "fmt/585": ("video/MP2T", ""),
    "fmt/5": ("video/avi", ""),
    "fmt/569": ("video/x-matroska", "4")
}

# (:unap) = Not applicable, makes no sense
# (:unav) = Value unavailable, possibly unknown
# See: http://digitalpreservation.fi/specifications/vocabularies/unknown-values
UNAP = "(:unap)"
UNAV = "(:unav)"

# Digital preservation grading
RECOMMENDED = "fi-preservation-recommended-file-format"
ACCEPTABLE = "fi-preservation-acceptable-file-format"
BIT_LEVEL_WITH_RECOMMENDED \
    = "fi-preservation-bit-level-file-format-with-recommended"
BIT_LEVEL = "fi-preservation-bit-level-file-format"
UNACCEPTABLE = "fi-preservation-unacceptable-file-format"


FILE_FORMAT_GRADE = {
    "text/csv": {
        "(:unap)": RECOMMENDED
    },
    "application/epub+zip": {
        "2.0.1": RECOMMENDED,
        "3.0.0": RECOMMENDED,
        "3.0.1": RECOMMENDED,
        "3.2": RECOMMENDED
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
    "text/plain": {
        "(:unap)": RECOMMENDED
    },
    "audio/x-aiff": {
        "(:unap)": ACCEPTABLE,  # AIFF-C
        "1.3": RECOMMENDED  # AIFF
    },
    "audio/x-wav": {
        "(:unap)": RECOMMENDED,  # WAV
        "2": RECOMMENDED  # BWF
    },
    "audio/flac": {
        "1.2.1": RECOMMENDED
    },
    "audio/L8": {
        "(:unap)": RECOMMENDED
    },
    "audio/L16": {
        "(:unap)": RECOMMENDED
    },
    "audio/L20": {
        "(:unap)": RECOMMENDED
    },
    "audio/L24": {
        "(:unap)": RECOMMENDED
    },
    "audio/mp4": {
        "(:unap)": RECOMMENDED
    },
    "image/x-dpx": {
        "2.0": RECOMMENDED
    },
    "video/x-ffv": {
        "3": RECOMMENDED
    },
    "video/jpeg2000": {
        "(:unap)": RECOMMENDED
    },
    "video/mp4": {
        "(:unap)": RECOMMENDED
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
        "(:unap)": RECOMMENDED
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
    "application/gml+xml": {
        "3.2.1": RECOMMENDED,
    },
    "application/vnd.google-earth.kml+xml": {
        "2.3": RECOMMENDED,
    },
    "application/x-siard": {
        "2.0": RECOMMENDED,
        "2.1": RECOMMENDED
    },
    "application/x-spss-por": {
        "(:unap)": RECOMMENDED
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
        "(:unap)": ACCEPTABLE
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
        "(:unap)": RECOMMENDED
    },
    "video/x-matroska": {  # Container
        "4": RECOMMENDED
    },
    "video/MP2T": {  # Container
        "(:unap)": RECOMMENDED
    },
    "application/mxf": {  # Container
        "(:unap)": RECOMMENDED
    },
    "video/mj2": {  # Container
        "(:unap)": RECOMMENDED
    },
    "video/quicktime": {  # Container
        "(:unap)": RECOMMENDED
    },
    "video/x-ms-asf": {  # Container
        "(:unap)": ACCEPTABLE
    },
    "video/MP1S": {  # Container
        "(:unap)": ACCEPTABLE
    },
    "video/MP2P": {  # Container
        "(:unap)": ACCEPTABLE
    }
}
