"""Common constants and dictionaries."""

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
    "application/mp4": None,
    "application/vnd.ms-asf": "video/x-ms-asf",
    "application/x-wine-extension-ini": "text/plain",
    "application/xml": "text/xml",
    "audio/x-m4a": "audio/mp4",
    "audio/x-ms-wma": "video/x-ms-asf",
    "video/x-dv": "video/dv",
    "video/x-ms-wmv": "video/x-ms-asf",
    "video/x-msvideo": "video/avi",
}

# Dict between detectors' results and known file format versions.
VERSION_DICT = {
    "application/pdf": {"1a": "A-1a", "1b": "A-1b",
                        "2a": "A-2a", "2b": "A-2b", "2u": "A-2u",
                        "3a": "A-3a", "3b": "A-3b", "3u": "A-3u"},
    "audio/x-wav": {"2 Generic": "2"},
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

# (:unap) = Not applicable, makes no sense
# (:unav) = Value unavailable, possibly unknown
# (:unac) = Temporarily inaccessible
# See: https://digitalpreservation.fi/support/vocabularies#Tuntemattomatarvot
UNAP = "(:unap)"
UNAV = "(:unav)"
UNKN = "(:unkn)"
UNAC = "(:unac)"

# Digital preservation grading
RECOMMENDED = "fi-dpres-recommended-file-format"
ACCEPTABLE = "fi-dpres-acceptable-file-format"
BIT_LEVEL_WITH_RECOMMENDED \
    = "fi-dpres-bit-level-file-format-with-recommended"
BIT_LEVEL = "fi-dpres-bit-level-file-format"
UNACCEPTABLE = "fi-dpres-unacceptable-file-format"
