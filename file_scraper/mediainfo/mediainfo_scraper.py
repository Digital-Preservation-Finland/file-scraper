""""Scraper for video and audio files scraped using MediaInfo."""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseScraper
from file_scraper.mediainfo.mediainfo_model import (AviMediainfoMeta,
                                                    MkvMediainfoMeta,
                                                    MovMediainfoMeta,
                                                    MpegMediainfoMeta,
                                                    MxfMediainfoMeta,
                                                    WavMediainfoMeta)
from file_scraper.utils import decode_path

try:
    from pymediainfo import MediaInfo
except ImportError:
    pass


class MediainfoScraper(BaseScraper):
    """
    Scraper for scraping audio and video files using Mediainfo.

    A guess of the MIME type of the scraped file must be supplied to the
    scraper in the params dict under the key "mimetype".
    """

    _supported_metadata = [MovMediainfoMeta, MkvMediainfoMeta,
                           WavMediainfoMeta, MpegMediainfoMeta,
                           #AviMediainfoMeta,
                           MxfMediainfoMeta]

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return
        if "mimetype_guess" not in self._params:
            raise AttributeError("MediainfoScraper was not given a parameter "
                                 "dict containing key 'mimetype_guess'.")

        try:
            mediainfo = MediaInfo.parse(decode_path(self.filename))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(six.text_type(e))
            self._check_supported()
            return

        # check that the file is whole and contains audio and/or video tracks
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
            return
        elif not truncated:
            self._messages.append("The file was analyzed successfully.")

        # If the MIME type is forced to a certain value by mimetype parameter,
        # use that value, otherwise use the given mimetype_guess
        if self._given_mimetype:
            mime_guess = self._given_mimetype
        else:
            mime_guess = self._params["mimetype_guess"]

        for index in range(len(mediainfo.tracks)):
            for md_class in self._supported_metadata:
                if md_class.is_supported(mime_guess):
                    md_object = md_class(mediainfo.tracks, index, mime_guess,
                                         self._given_mimetype,
                                         self._given_version)
                    if not md_object.hascontainer() and index == 0:
                        continue
                    self.streams.append(md_object)
        self._check_supported(allow_unav_version=True, allow_unap_version=True)
