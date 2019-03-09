"""Common dictionaries
"""

# Dict between detectors' results and known mimetypes.
MIMETYPE_DICT = {
    'application/xml': 'text/xml',
    'application/mp4': None,
    'application/vnd.ms-asf': 'video/x-ms-asf',
    'video/x-msvideo': 'video/avi',
    'application/x-ia-arc': 'application/x-internet-archive'
}

# Dict between detectors' results and known file format versions.
VERSION_DICT = {
    'text/xml': {'5': '5.0'},
    'application/pdf': {'1a': 'A-1a', '1b': 'A-1b',
                        '2a': 'A-2a', '2b': 'A-2b', '2u': 'A-2u',
                        '3a': 'A-3a', '3b': 'A-3b', '3u': 'A-3u'},
    'audio/x-wav': {'2 Generic': '2'}
}

# Dict between detectors' pronom results and known mimetypes and versions.
PRONOM_DICT = {
    'x-fmt/135': ('audio/x-aiff', '1.3'),
    'fmt/541': ('image/x-dpx', '2.0'),
    'fmt/410': ('application/x-internet-archive', '1.1'),
    'fmt/289': ('application/warc', None),  # does not result version
    'fmt/244': ('application/vnd.google-earth.kml+xml', '2.3'),
    'fmt/997': ('application/x-spss-por', ''),
    'fmt/649': ('video/mpeg', '1'),
    'fmt/640': ('video/mpeg', '2'),
    'x-fmt/385': ('video/MP1S', ''),
    'x-fmt/386': ('video/MP2P', ''),
    'fmt/585': ('video/MP2T', '')
}
