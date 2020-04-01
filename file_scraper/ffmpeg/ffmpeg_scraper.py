"""FFMpeg wellformed scraper."""
from __future__ import unicode_literals

import re
import six

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.ffmpeg.ffmpeg_model import FFMpegSimpleMeta, FFMpegMeta
from file_scraper.utils import ensure_text, encode_path

try:
    import ffmpeg
except ImportError:
    pass


class FFMpegScraper(BaseScraper):
    """
    Scraper using FFMpeg to check well-formedness / gather metadata.

    For most file types, no metadata is scraped: for those files
    FFMpegSimpleMeta metadata model is used. This is done as both Mediainfo and
    FFMpeg cannot be used simultaneously to scrape the metadata as reliable
    matching of streams from two scrapers is not currently possible. For AVI
    files, Mediainfo is not able to report all required metadata, so for those
    files all metadata collection is done with FFMpegScraper, using FFMpegMeta
    as the metadata model.
    """

    # Supported metadata models
    _supported_metadata = [FFMpegSimpleMeta, FFMpegMeta]

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
        # if "truncated" in self.filename:
        #     __import__('pdb').set_trace()

        if self._filter_stderr(shell.stderr):
            self._errors.append(shell.stderr)
            return

        container = False
        for index in range(len(streams)):
            # FFMpeg has separate "format" (relevant for containers) and
            # "streams" (relevant for all files) elements in its output. We
            # know whether we'll have streams + container or just streams only
            # after scraping the first stream, so there's a risk of trying to
            # add one too many streams. This check prevents constructing more
            # metadata models than there are streams.
            if not container and index == len(streams) - 1:
                break

            self.streams += list(self.iterate_models(
                probe_results=probe_results, index=index))

            for stream in self.streams:
                if stream.hascontainer():
                    container = True

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def _filter_stderr(self, errors):
        """
        Filter out "bpno became negative" and "Last message repeated".

        Returns a new string, containing all lines in errors except those that
        contain either "Last message repeated [number] times" or both
        "jpeg2000" and "bpno became negative".

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
