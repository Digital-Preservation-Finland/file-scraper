"""Mediainfo scraper and metadata model."""

# This list contains mimetypes of all formats that can be identified
# with mediainfo, and properties of pymediainfo track that are used for
# identification.
FORMATS = [
    {
        "mimetype": "audio/aac",
        "properties": {"format": "AAC"}
    },
    {
        "mimetype": "audio/flac",
        "properties": {"format": "FLAC"}
    },
    {
        "mimetype": "audio/L8",
        "properties": {"format": "PCM", "bit_depth": 8}
    },
    {
        "mimetype": "audio/L16",
        "properties": {"format": "PCM", "bit_depth": 16}
    },
    {
        "mimetype": "audio/L20",
        "properties": {"format": "PCM", "bit_depth": 20}
    },
    {
        "mimetype": "audio/L24",
        "properties": {"format": "PCM", "bit_depth": 24}
    },
    {
        "mimetype": "audio/mp4",
        "properties": {"format": "MPEG-4", "format_profile": "Apple audio "
                                                             "with iTunes "
                                                             "info"}
    },
    {
        "mimetype": "audio/mpeg",
        "properties": {"format": "MPEG Audio"}
    },
    {
        "mimetype": "audio/x-aiff",
        "properties": {"format": "AIFF"}
    },
    {
        "mimetype": "audio/x-ms-wma",
        "properties": {"format": "WMA"}
    },
    {
        "mimetype": "video/avi",
        "properties": {"format": "AVI"}
    },
    {
        "mimetype": "video/dv",
        "properties": {"format": "DV"}
    },
    {
        "mimetype": "video/h264",
        "properties": {"format": "AVC"}
    },
    {
        "mimetype": "video/h265",
        "properties": {"format": "HEVC"}
    },
    {
        "mimetype": "video/MP1S",
        "properties": {"format": "MPEG-PS",
                       "internet_media_type": "video/mpeg"}
    },
    {
        "mimetype": "video/MP2P",
        "properties": {"format": "MPEG-PS",
                       "internet_media_type": "video/MP2P"}
    },
    {
        "mimetype": "video/MP2T",
        "properties": {"format": "MPEG-TS"}
    },
    {
        "mimetype": "video/mp4",
        "properties": {"format": "MPEG-4", "format_profile": "Base Media"}
    },
    {
        "mimetype": "video/mp4",
        "properties": {
            "format": "MPEG-4",
            "format_profile": "Base Media / Version 2"
        }
    },
    {
        "mimetype": "video/mpeg",
        "properties": {"format": "MPEG Video"}
    },
    {
        "mimetype": "video/quicktime",
        "properties": {"format": "MPEG-4", "format_profile": "QuickTime"}
    },
    {
        "mimetype": "video/quicktime",
        "properties": {"format": "QuickTime",
                       "format_info": "Original Apple specifications"}
    },
    {
        "mimetype": "video/x.fi-dpres.prores",
        "properties": {"format": "ProRes"}
    },
    {
        "mimetype": "video/x-ffv",
        "properties": {"format": "FFV1"}
    },
    {
        "mimetype": "video/x-matroska",
        "properties": {"format": "Matroska"}
    },
    {
        "mimetype": "video/x-ms-asf",
        "properties": {"format": "Windows Media"}
    },
    {
        "mimetype": "video/x-ms-wmv",
        "properties": {"format": "VC-1"}
    },
    {
        "mimetype": "video/x-ms-wmv",
        "properties": {"format": "WMV1"}
    },
    {
        "mimetype": "video/x-ms-wmv",
        "properties": {"format": "WMV2"}
    },
    {
        "mimetype": "video/x-ms-wmv",
        "properties": {"format": "WMV3"}
    },
]


def track_mimetype(track):
    """Detect mimetype of track.

    :param track: Pymediainfo Track object
    :returns: detected mimetype or `None`
    """
    candidates = []
    for format_ in FORMATS:
        if all(track.to_data().get(property_, None)
               == format_['properties'][property_]
               for property_ in format_["properties"]):
            # Track has all properties of this format, choose this
            # mimetype
            candidates.append(format_['mimetype'])

    if len(candidates) == 0:
        # Track did not match any format
        return None
    if len(candidates) == 1:
        return candidates[0]

    raise ValueError("Could not detect track mimetype, track properties "
                     "match more than one format.")
