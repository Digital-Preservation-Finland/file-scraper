""""Scraper for video and audio files scraped using MediaInfo."""

try:
    from pymediainfo import MediaInfo
except ImportError:
    pass

from file_scraper.mediainfo.mediainfo_meta import (MovMediainfoMeta,
                                                   MkvMediainfoMeta,
                                                   WavMediainfoMeta,
                                                   MpegMediainfoMeta)
from file_scraper.base import BaseScraper
from file_scraper.utils import decode


class MediainfoScraper(BaseScraper):
    """
    Scraper for scraping audio and video files using Mediainfo.

    A guess of the MIME type of the scraped file must be supplied to the
    scraper in the params dict under the key "mimetype".
    """

    _supported_metadata = [MovMediainfoMeta, MkvMediainfoMeta,
                           WavMediainfoMeta, MpegMediainfoMeta]

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return
        if "mimetype" not in self._params:
            raise AttributeError("MediainfoScraper was not given a parameter "
                                 "dict containing mimetype of the file")

        try:
            mediainfo = MediaInfo.parse(decode(self.filename))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append("Error in analyzing file.")
            self._errors.append(str(e))
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
            return  # TODO new addition, is return reasonable here?
        elif not truncated:
            self._messages.append("The file was analyzed successfully.")

        mime_guess = self._params["mimetype"]
        for index in range(len(mediainfo.tracks)):
            for md_class in self._supported_metadata:
                if md_class.is_supported(mime_guess):
                    md_object = md_class(mediainfo.tracks, index, mime_guess)
                    self.streams.append(md_object)

        self._check_supported()


def _sort_tracks(mediainfo):
    """
    Sort tracks within the given mediainfo object.

    The container comes first, followed by audio and video tracks.

    :mediainfo: Mediainfo.parse() result
    """
    # container first
    for index, track in enumerate(mediainfo.tracks):
        if track.track_type == "General":
            mediainfo.tracks.insert(
                0, mediainfo.tracks.pop(index))
            break

    # then video and audio tracks
    stream_index = 1
    track_index = 1
    while track_index < len(mediainfo.tracks):
        if mediainfo.tracks[track_index].track_type in ["Audio", "Video"]:
            mediainfo.tracks.insert(stream_index,
                                    mediainfo.tracks.pop(track_index))
            stream_index += 1
        track_index += 1
