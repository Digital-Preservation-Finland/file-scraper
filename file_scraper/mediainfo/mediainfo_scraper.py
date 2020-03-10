""""Scraper for video and audio files scraped using MediaInfo."""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseScraper
from file_scraper.mediainfo.mediainfo_model import (
    MkvMediainfoMeta,
    MovMediainfoMeta,
    MpegMediainfoMeta,
    SimpleMediainfoMeta,
    WavMediainfoMeta,
    )
from file_scraper.utils import decode_path

try:
    from pymediainfo import MediaInfo
except ImportError:
    pass


class MediainfoScraper(BaseScraper):
    """
    Scraper for scraping audio and video files using Mediainfo.
    """

    _supported_metadata = [
        MkvMediainfoMeta,
        MovMediainfoMeta,
        MpegMediainfoMeta,
        SimpleMediainfoMeta,
        WavMediainfoMeta,
    ]

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        try:
            mediainfo = MediaInfo.parse(decode_path(self.filename))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(six.text_type(e))
            self._check_supported()
            return

        if not self._tracks_ok(mediainfo):
            return
        else:
            self._messages.append("The file was analyzed successfully.")

        for index in range(len(mediainfo.tracks)):
            self.iterate_models(tracks=mediainfo.tracks, index=index)

        # Files scraped with SimpleMediainfoMeta will have (:unav) MIME type,
        # but for other scrapes the tests need to be performed without allowing
        # unavs MIME types.
        if self.streams and isinstance(self.streams[0], SimpleMediainfoMeta):
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
            return
        self._check_supported(allow_unav_version=True, allow_unap_version=True)

    def iterate_models(self, **kwargs):
        """
        Iterate metadata models.
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(self._predefined_mimetype):
                md_object = md_class(**kwargs)
                if md_object.hascontainer() or kwargs["index"] > 0:
                    self.streams.append(md_object)

    def _tracks_ok(self, mediainfo):
        """
        Check that the file is complete and contains audio and/or video tracks.

        Returns True if the file is not truncated and contains at least one
        track. Otherwise returns False.

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
