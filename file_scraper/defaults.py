"""Common constants and dictionaries."""

from dpres_file_formats.defaults import Grades, UnknownValue

UNAC = UnknownValue.UNAC.value
UNAL = UnknownValue.UNAL.value
UNAP = UnknownValue.UNAP.value
UNAS = UnknownValue.UNAS.value
UNAV = UnknownValue.UNAV.value
UNKN = UnknownValue.UNKN.value
UVNONE = UnknownValue.UVNONE.value
UVNULL = UnknownValue.UVNULL.value
TBA = UnknownValue.TBA.value
ETAL = UnknownValue.ETAL.value

RECOMMENDED = Grades.RECOMMENDED.value
ACCEPTABLE = Grades.ACCEPTABLE.value
BIT_LEVEL_WITH_RECOMMENDED = Grades.WITH_RECOMMENDED.value
BIT_LEVEL = Grades.BIT_LEVEL.value
UNACCEPTABLE = Grades.UNACCEPTABLE.value

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
    "application/csv": "text/csv",
    "application/vnd.ms-asf": "video/x-ms-asf",
    "application/x-wine-extension-ini": "text/plain",
    "application/x-subrip": "text/plain",
    "application/xml": "text/xml",
    "audio/x-m4a": "audio/mp4",
    "audio/x-ms-wma": "video/x-ms-asf",
    "video/x-dv": "video/dv",
    "video/x-ms-wmv": "video/x-ms-asf",
    "video/x-msvideo": "video/avi",
}

# Map FIDO version strings to actual versions
VERSION_DICT = {
    "application/pdf": {"1a": "A-1a", "1b": "A-1b",
                        "2a": "A-2a", "2b": "A-2b", "2u": "A-2u",
                        "3a": "A-3a", "3b": "A-3b", "3u": "A-3u"},
    "application/vnd.ms-excel": {
        "8": "8X",
    },
    "audio/x-wav": {
        "2 Generic": "2",
        # Try for example tests/data/audio_x-wav/valid_2_bwf.wav
        "0 PCM Encoding": None,
    },
    "audio/ac3": {None: UNAP},
    "audio/flac": {
        # TODO: Other versions are probably possible, and all of them
        # should be UNAP?
        "1.2.1": UNAP,
    },
    "image/gif": {
        "87a": "1987a",
        "89a": "1989a",
    },
    "image/png": {
        # Fido does not detect PNG version correctly?
        "1.0": None,
    },
    None: {
        # Fido detects version of video/x-ms-asf, but not the mimetype?
        "9 Advanced Profile (WVC1)": UNAP,
        # Fido detects wrong AIFF version, and not the mimetype? Try for
        # example tests/data/audio_x-aiff/valid_1.3.aiff
        "1.2": None,
        # Fido detects version of webp file as "Extended", but it does
        # not detect the mimetype? Try for example
        # tests/data/image_webp/valid__lossy.webp
        "Extended": None,
    }
}

# Dict between detectors' pronom results and known mimetypes and versions.
# fmt/289 might be need to change to fmt/1355 when supported by FIDO.
PRONOM_DICT = {
    "fmt/5": ("video/avi", ""),
    "fmt/244": ("application/vnd.google-earth.kml+xml", "2.3"),
    "fmt/289": ("application/warc", None),  # does not result version
    "fmt/541": ("image/x-dpx", "2.0"),
    "fmt/569": ("video/x-matroska", "4"),
    "fmt/585": ("video/mp2t", ""),
    "fmt/640": ("video/mpeg", "2"),
    "fmt/649": ("video/mpeg", "1"),
    "fmt/997": ("application/x-spss-por", ""),
    "fmt/1134": ("text/xml", None),  # GPX 1.1 XML schema
    "x-fmt/135": ("audio/x-aiff", "1.3"),
    "x-fmt/385": ("video/mp1s", ""),
    "x-fmt/386": ("video/mp2p", ""),
}

COMPATIBLE_ENCODINGS = {
    "UTF-8": ["US-ASCII"],
    "UTF-16": ["UTF-16BE", "UTF-16LE"],
    "UTF-32": ["UTF-32BE", "UTF-32LE"],
    "ISO-8859-15": ["US-ASCII", "ISO-8859-1"],
}

# TODO: Version compatibility should be specific to mimetype!
COMPATIBLE_VERSIONS = {
    # JPEG JFIF versions are compatible with EXIF versions
    # TODO: Add all versions here.
    "2.2.1": ["1.01"],
    "2.2": ["1.01"],
    # Some PDF versions are compatible with PDF-A versions
    # TODO: The PDF version compatibility lists have been generated
    # based on out test files. Check that these versions actually should
    # be compatible, and add missing versions!
    "A-1a": [
        # valid_A-1a.pdf
        # valid_A-1a_invalid_resource_name.pdf
        "1.4",
        # valid_A-1a_root_1.6.pdf
        "1.6",
        # valid_A-1a_root_1.7.pdf
        "1.7"
    ],
    "A-1b": [
        # valid_A-1b_root_1.7.pdf
        "1.7"
    ],
    "A-2b": [
        # valid_A-2b.pdf
        "1.7",
    ],
    "A-2u": [
        # valid_A-2u_root_1.5.pdf
        "1.5"
    ],
    "A-3b": [
        # valid_A-3b_no_file_extension
        # valid_A-3b.pdf
        "1.7",
    ],
}
