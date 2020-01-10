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

    # Supported mimetypes
    _supported_metadata = [FFMpegSimpleMeta, FFMpegMeta]

    def __init__(self, filename, check_wellformed=True, params=None):
        """
        Store mimetype_guess in addition to the normal init process.

        If MIME type is forced ("mimetype" in params), it is used over
        "mimetype_guess" possibly present in the parameters. At least one of
        the two must be given or a KeyError is raised.
        """
        if "mimetype" in params and params["mimetype"]:
            self._mimetype_guess = params["mimetype"]
        elif "mimetype_guess" in params:
            self._mimetype_guess = params["mimetype_guess"]
        else:
            raise KeyError("FFMpegScraper must be given 'mimetype_guess' or"
                           "'mimetype' in params")
        super(FFMpegScraper, self).__init__(filename, check_wellformed, params)

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

            for md_class in self._supported_metadata:
                if md_class.is_supported(self._mimetype_guess):
                    stream = md_class(probe_results, index,
                                      self._given_mimetype,
                                      self._given_version)
                    self.streams.append(stream)
                    if stream.hascontainer():
                        container = True

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
