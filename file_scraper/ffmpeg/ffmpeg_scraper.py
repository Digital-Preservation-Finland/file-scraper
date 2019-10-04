"""FFMpeg wellformed scraper."""
from __future__ import unicode_literals

import six
import re

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.ffmpeg.ffmpeg_model import FFMpegSimpleMeta
from file_scraper.utils import ensure_text, encode_path

try:
    import ffmpeg
except ImportError:
    pass


class FFMpegScraper(BaseScraper):
    """FFMpeg Wellformed scraper."""

    # Supported mimetypes
    _supported_metadata = [FFMpegSimpleMeta]

    # If stream order problems are solved, this metadata model can be used to
    # collect more information about the file.
    # _supported_metadata = [FFMpegMeta]

    _only_wellformed = True

    def scrape_file(self):
        """Scrape A/V files."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

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

        shell = ProcessRunner(["ffmpeg", "-v", "error", "-i",
                               encode_path(self.filename), "-f", "null", "-"])
        if shell.returncode == 0:
            self._messages.append("The file was analyzed successfully.")
        if self._filter_stderr(shell.stderr):
            self._errors.append(ensure_text(shell.stderr))
            return

        for md_class in self._supported_metadata:
            stream = md_class(self._given_mimetype, self._given_version)
            self.streams.append(stream)

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def _filter_stderr(self, errors):
        """
        Filter out "bpno became negative" and "Last message repeated".

        Returns a new string, containing all lines in errors except those that
        contain either "Last message repeated [number] times" or both
        "jpeg2000" and "bpno became negative".
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
