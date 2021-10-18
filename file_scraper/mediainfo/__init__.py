"""Mediainfo scraper and metadata model."""

# This list contains mimetypes of all formats that can be identified
# with mediainfo, and properties of pymediainfo track that are used for
# identification.
FORMATS = [
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
        "mimetype": "video/quicktime",
        "properties": {"format": "MPEG-4", "format_profile": "QuickTime"}
    },
    {
        "mimetype": "video/dv",
        "properties": {"format": "DV"}
    },
    {
        "mimetype": "audio/mp4",
        "properties": {"format": "AAC"}
    },
    {
        "mimetype": "video/mp4",
        "properties": {"format": "AVC"}
    },
    {
        "mimetype": "video/mp4",
        "properties": {"format": "MPEG-4", "format_profile": "Base Media"}
    },
    {
        "mimetype": "video/mpeg",
        "properties": {"format": "MPEG Video"}
    },
    {
        "mimetype": "video/MP2T",
        "properties": {"format": "MPEG-TS"}
    },
    {
        "mimetype": "video/MP1S",
        "properties": {"format": "MPEG-PS", "format_version": "Version 1"}
    },
    {
        "mimetype": "video/MP2P",
        "properties": {"format": "MPEG-PS", "format_version": "Version 2"}
    },
    {
        "mimetype": "audio/mpeg",
        "properties": {"format": "MPEG Audio"}
    },
    {
        "mimetype": "video/avi",
        "properties": {"format": "AVI"}
    },
    {
        "mimetype": "video/x-matroska",
        "properties": {"format": "Matroska"}
    },
    {
        "mimetype": "audio/flac",
        "properties": {"format": "FLAC"}
    },
    {
        "mimetype": "video/x-ffv",
        "properties": {"format": "FFV1"}
    },
    {
        "mimetype": "video/x.fi-dpres.prores",
        "properties": {"format": "ProRes"}
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
