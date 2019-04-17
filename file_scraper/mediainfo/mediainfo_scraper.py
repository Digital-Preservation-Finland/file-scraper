""""TODO"""

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
    """TODO"""

    _supported_metadata = [MovMediainfoMeta, MkvMediainfoMeta,
                           WavMediainfoMeta, MpegMediainfoMeta]

    def scrape_file(self):
        """TODO"""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return
        try:
            mediainfo = MediaInfo.parse(decode(self.filename))
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self._errors.append('Error in analyzing file.')
            self._errors.append(str(e))
            #self.set_tool_stream(0)  # TODO
            self._check_supported()
            #self._collect_elements() # TODO
            return

        # TODO do these sorting steps really need to be done?
        # container first
        for index, track in enumerate(mediainfo.tracks):
            if track.track_type == 'General':
                self._mediainfo.tracks.insert(
                    0, self._mediainfo.tracks.pop(index))
                break

        # then video and audio tracks
        stream_index = 1
        track_index = 1
        # TODO implementation changed (old modified a list while it was
        #      iterated over), is this ok?
        while track_index < len(mediainfo.tracks):
            if mediainfo.tracks[track_index].track_type in ["Audio", "Video"]:
                mediainfo.tracks.insert(stream_index,
                                        mediainfo.tracks.pop(track_index))
                stream_index += 1
            track_index += 1

        # check that the file is whole and contains audio and/or video tracks
        truncated = False
        track_found = False
        for track in mediainfo.tracks:
            if track.istruncated == 'Yes':
                truncated = True
                self._errors.append('The file is truncated.')
            if track.track_type.lower() in ['audio', 'video']:
                track_found = True
        if not track_found:
            self._errors.append('No audio or video tracks found.')
            return  # TODO new addition, is return reasonable here?
        elif not truncated:
            self._messages.append('The file was analyzed successfully.')

        for index, stream in enumerate(mediainfo.tracks):
            for md_class in self._supported_metadata:
                md_object = md_class(stream, index, index == 0,
                                     mediainfo.tracks[0])
                if md_class.is_supported(md_object.mimetype()):
                    self.streams.append(md_object)

        self._check_supported()
