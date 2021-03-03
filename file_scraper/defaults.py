"""Common constants and dictionaries"""
from __future__ import unicode_literals

# Prioritize these pronom codes in identification
PRIORITY_PRONOM = [
    "x-fmt/18", "fmt/483", "fmt/102", "fmt/103", "fmt/101", "fmt/100",
    "fmt/471", "fmt/136", "fmt/290", "fmt/291", "fmt/137", "fmt/294",
    "fmt/295", "fmt/138", "fmt/292", "fmt/293", "fmt/139", "fmt/296",
    "fmt/297", "fmt/95", "fmt/354", "fmt/476", "fmt/477", "fmt/478",
    "fmt/479", "fmt/480", "fmt/481", "x-fmt/111", "x-fmt/135", "fmt/527",
    "fmt/279", "fmt/199", "fmt/141", "fmt/541", "x-fmt/392", "fmt/438",
    "fmt/730", "fmt/42", "fmt/43", "fmt/44", "x-fmt/398", "x-fmt/390",
    "x-fmt/391", "fmt/645", "x-fmt/392", "fmt/353", "fmt/13", "x-fmt/219",
    "fmt/289", "fmt/289", "fmt/155", "x-fmt/227", "fmt/244", "fmt/997",
    "fmt/40", "fmt/412", "fmt/61", "fmt/62", "fmt/214", "fmt/126",
    "fmt/215", "fmt/16", "fmt/17", "fmt/18", "fmt/19", "fmt/20", "fmt/276",
    "x-fmt/136", "fmt/134", "fmt/132", "x-fmt/152", "fmt/649", "fmt/640",
    "fmt/133", "fmt/124", "fmt/3", "fmt/4", "fmt/131", "fmt/5", "x-fmt/385",
    "x-fmt/386", "fmt/585", "fmt/200", "fmt/337", "x-fmt/384"]

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
    "application/msword": {"97-2003": None},
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.document": {"2007 onwards": None},
    "application/vnd.ms-powerpoint": {"97-2003": None},
    "application/vnd.openxmlformats-officedocument"
    ".presentationml.presentation": {"2007 onwards": None},
    "application/vnd.ms-excel": {"8": None, "8X": None},
    "application/vnd.openxmlformats-officedocument"
    ".spreadsheetml.sheet": {"2007 onwards": None}
}

# Dict between detectors' pronom results and known mimetypes and versions.
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
