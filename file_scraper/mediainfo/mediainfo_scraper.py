"""Scraper for video and audio files scraped using MediaInfo."""

from file_scraper.base import BaseScraper
import file_scraper.mediainfo
from file_scraper.mediainfo.mediainfo_model import (
    ContainerMediainfoMeta,
    DvMediainfoMeta,
    FfvMediainfoMeta,
    FlacMediainfoMeta,
    AiffMediainfoMeta,
    LpcmMediainfoMeta,
    MkvMediainfoMeta,
    MpegMediainfoMeta,
    WavMediainfoMeta,
    VersionlessFormatMeta,
    WmaMediainfoMeta,
    WmvMediainfoMeta,
    UnknownStreamFormatMeta
)
from file_scraper.defaults import UNAV
from file_scraper.logger import LOGGER


try:
    import pymediainfo
except ImportError:
    pass


class MediainfoScraper(BaseScraper):
    """Scraper for scraping audio and video files using Mediainfo."""

    _supported_metadata = [
        ContainerMediainfoMeta,
        DvMediainfoMeta,
        FfvMediainfoMeta,
        FlacMediainfoMeta,
        AiffMediainfoMeta,
        LpcmMediainfoMeta,
        MkvMediainfoMeta,
        MpegMediainfoMeta,
        WavMediainfoMeta,
        WmaMediainfoMeta,
        WmvMediainfoMeta,
        VersionlessFormatMeta,
        UnknownStreamFormatMeta
    ]

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.

        :returns: None if scraper does not check well-formedness, True if the
                  file has been scraped without errors and otherwise False
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        try:
            mediainfo = pymediainfo.MediaInfo.parse(self.filename)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            LOGGER.warning(
                "Error analyzing file %s with MediaInfo",
                self.filename
            )
            self._errors.append("Error in analyzing file.")
            self._errors.append(str(e))
            self._check_supported()
            return

        if not self._tracks_ok(mediainfo):
            return

        self._messages.append("The file was analyzed successfully.")

        for index, track in enumerate(mediainfo.tracks):

            # Use predefined mimetype/version for first stream, and
            # detected mimetype for other streams
            if len(self.streams) == 0:
                mimetype = self._predefined_mimetype
                version = self._predefined_version

            # WAV is a special container format. For WAV files,
            # no distinction between container and soundtrack needs to
            # be made, as both are treated as one in the DPS.
            elif (self._predefined_mimetype == 'audio/x-wav'
                  or file_scraper.mediainfo.track_mimetype(mediainfo.tracks[0])
                  == 'audio/x-wav'):
                LOGGER.debug("Normalizing MIME type to 'audio/x-wav'")
                mimetype = 'audio/x-wav'
                version = None

            else:
                mimetype = file_scraper.mediainfo.track_mimetype(track)
                version = None

            # Add track as stream
            self.streams += list(
                self.iterate_models(
                    mimetype=mimetype,
                    version=version,
                    tracks=mediainfo.tracks,
                    index=index
                )
            )

        self._check_supported(allow_unav_version=True, allow_unap_version=True)

    def iterate_models(self, **kwargs):
        """Iterate metadata models.

        :param kwargs: Model specific parameters. The dictionary should
                       contain mimetype and version of stream format,
                       list of all tracks in the file, and index of
                       track.
        :returns: Metadata model
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(kwargs['mimetype'], kwargs['version']):
                md_object = md_class(kwargs['tracks'], kwargs['index'])
                # Skip tracks that are not streams
                if md_object.stream_type():
                    yield md_object

    def _tracks_ok(self, mediainfo):
        """Check that the file is complete and contains tracks.

        Returns True if the file is not truncated and contains at least
        one audio or video track. Otherwise returns False.

        If problems are encountered, they are recorded in self.errors.
        Otherwise a success message is recorded in self.messages.

        :mediainfo: Output from MediaInfo.parse
        :returns: True for complete AV file, False otherwise
        """
        truncated = False
        track_found = False
        for track in mediainfo.tracks:
            if track.istruncated == "Yes":
                truncated = True
                self._errors.append("The file is truncated.")
            if track.track_type.lower() in ["audio", "video"]:
                track_found = True
        if not track_found:
            self._errors.append("No audio or video tracks found.")
        if truncated:
            self._errors.append("File contains a truncated track.")

        return not truncated and track_found

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNAV.
        """
        pymediaversion = pymediainfo.__version__
        try:
            # Determine the library version from
            # `MediaInfo_Option(handle, "Info_Version", "")`
            # result. This is only available via the private
            # interface, so take care to clean up the handle
            # ourselves afterwards.
            # pylint: disable=protected-access
            lib, handle, libmediaversion, *_ \
                = pymediainfo.MediaInfo._get_library()
            lib.MediaInfo_Close(handle)
            lib.MediaInfo_Delete(handle)

        except Exception:  # pylint: broad-except
            LOGGER.warning(
                "Could not retrieve MediaInfo version due to exception",
                exc_info=True
            )
            libmediaversion = UNAV

        return {
            "pymediainfo": {
                "version": pymediaversion
            },
            "MediaInfoLib": {
                    "version": libmediaversion
            }
        }
