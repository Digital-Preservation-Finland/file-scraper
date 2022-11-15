"""FFMpeg wellformed scraper."""
from __future__ import unicode_literals

import re
import six

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.ffmpeg.ffmpeg_model import FFMpegSimpleMeta, FFMpegMeta
from file_scraper.utils import ensure_text, encode_path
from file_scraper.defaults import UNAV

try:
    import ffmpeg
except ImportError:
    pass


class FFMpegScraper(BaseScraper):
    """
    Scraper using FFMpeg to check well-formedness / gather metadata.

    For most file types, no metadata is scraped: for those files
    FFMpegSimpleMeta metadata model is used. This is done as both
    Mediainfo and FFMpeg cannot be used simultaneously to scrape the
    metadata as reliable matching of streams from two scrapers is not
    currently possible. For AVI files, Mediainfo is not able to report
    all required metadata, so for those files all metadata collection is
    done with FFMpegScraper, using FFMpegMeta as the metadata model.
    """

    # Supported metadata models
    _supported_metadata = [FFMpegSimpleMeta, FFMpegMeta]

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.
        If file contains streams that can not be identified, the scraper can
        not check well-formedness.

        :returns: None if scraper does not check well-formedness, True if the
                  file has been scraped without errors and otherwise False
        """
        valid = super(FFMpegScraper, self).well_formed
        unsupported_av_format_found = any(
            stream.av_format_supported() is False for stream in self.streams)

        if valid and unsupported_av_format_found:
            return None

        return valid

    def scrape_file(self):
        """Scrape A/V files."""
        try:
            probe_results = ffmpeg.probe(encode_path(self.filename))
            streams = [probe_results["format"]] + probe_results["streams"]
            for stream in streams:
                if "index" not in stream:
                    stream["index"] = 0
                else:
                    stream["index"] = stream["index"] + 1
        except ffmpeg.Error as err:
            self._errors.append("Error in analyzing file.")
            self._errors.append(ensure_text(err.stderr))

        shell = Shell(["ffmpeg", "-v", "error", "-i",
                       encode_path(self.filename), "-f", "null", "-"])

        if shell.returncode == 0:
            self._messages.append("The file was analyzed successfully.")

        if self._filter_stderr(shell.stderr):
            self._errors.append(shell.stderr)
            return

        # We deny e.g. A-law PCM, mu-law PCM, DPCM and ADPCM and allow
        # only signed/unsigned linear PCM. Note that we need this check
        # only if PCM audio is present. This should not be given e.g.
        # for video streams nor audio streams of another type (such as
        # MPEG).
        # The exception is AIFF-C, where all kinds of PCM is allowed
        probe_format_name = probe_results["format"].get("format_name", UNAV)
        for stream in streams:
            if probe_format_name == "aiff":
                continue
            if "PCM" in stream.get("codec_long_name", UNAV) and not \
                    any(stream.get("codec_long_name", UNAV).startswith(x)
                        for x in ["PCM signed", "PCM unsigned"]):
                self._errors.append("%s does not seem to be LPCM format."
                                    % stream["codec_long_name"])

        container = False
        for index in range(len(streams)):
            # FFMpeg has separate "format" (relevant for containers) and
            # "streams" (relevant for all files) elements in its output.
            # We know whether we'll have streams + container or just
            # streams only after scraping the first stream, so there's a
            # risk of trying to add one too many streams. This check
            # prevents constructing more metadata models than there are
            # streams.
            if not container and index == len(streams) - 1:
                break

            self.streams += list(self.iterate_models(
                probe_results=probe_results, index=index))

            for stream in self.streams:
                if stream.hascontainer():
                    container = True

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def iterate_models(self, **kwargs):
        """
        Iterate Scraper models.

        :kwargs: FFProbe results and index
        :returns: Metadata model
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(self._predefined_mimetype,
                                     self._predefined_version, self._params):
                md_object = md_class(**kwargs)
                if md_object.av_format_supported() is not None:
                    yield md_object

    def _filter_stderr(self, errors):
        """
        Filter out "bpno became negative" and "Last message repeated".

        Returns a new string, containing all lines in errors except
        those that contain either "Last message repeated [number] times"
        or both "jpeg2000" and "bpno became negative".

        :errors: Stderr result from Shell in scraping
        :returns: Filtered error message result
        """
        # pylint: disable=no-self-use
        constructed_string = ""
        repeat = re.compile("Last message repeated [0-9]+ times")
        for line in six.text_type(errors).split("\n"):
            if not line:
                continue
            if "jpeg2000" in line and "bpno became negative" in line:
                continue
            if repeat.match(line.strip()):
                continue
            constructed_string = constructed_string + line + "\n"
        return constructed_string
