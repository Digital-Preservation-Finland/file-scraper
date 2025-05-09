"""
FFMpeg scraper for gathering metadata and well-formed checking.

For most file types, no real metadata is scraped: for those files
FFMpegSimpleMeta metadata model is used. This is done as both
Mediainfo and FFMpeg cannot be used simultaneously to scrape the
metadata as reliable matching of streams from two scrapers is not
currently possible. For AVI files, Mediainfo is not able to report
all required metadata, so for those files all metadata collection is
done with FFMpegScraper, using FFMpegMeta as the metadata model.
"""

import re

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.ffmpeg.ffmpeg_model import FFMpegSimpleMeta, FFMpegMeta
from file_scraper.utils import ensure_text, encode_path
from file_scraper.defaults import UNAV

try:
    import ffmpeg
except ImportError:
    pass


class FFMpegMetaScraper(BaseScraper):
    """
    Scraper using FFMpeg to gather metadata without well-formed check.
    """

    # Supported metadata models
    _supported_metadata = [FFMpegMeta]

    @property
    def well_formed(self):
        """
        Do not check well-formedness.

        :returns: False if errors found, None otherwise.
        """
        valid = super().well_formed

        return None if valid else valid

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):
        """
        Metadata gathering is needed also in well-formed check, so it is not
        necessary to run this scraper with well-formed check.
        """
        if check_wellformed:
            return False

        return super().is_supported(
            mimetype=mimetype, version=version,
            check_wellformed=check_wellformed, params=params)

    def scrape_file(self):
        """Scrape A/V files."""
        self._gather_metadata()
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True)

    def _gather_metadata(self):
        """Gather video and audio stream metadata with FFProbe.
        """
        try:
            probe_results = ffmpeg.probe(encode_path(self.filename))
            probe_results["format"]["index"] = 0
            for stream in probe_results["streams"]:
                if "index" not in stream:
                    stream["index"] = 0
                else:
                    stream["index"] = stream["index"] + 1
            self._messages.append(
                "The file was analyzed successfully with FFProbe.")

            # We deny e.g. A-law PCM, mu-law PCM, DPCM and ADPCM and allow
            # only signed/unsigned linear PCM. Note that we need this check
            # only if PCM audio is present. This should not be given e.g.
            # for video streams nor audio streams of another type (such as
            # MPEG). For AIFF-C, all kinds of PCM is allowed.

            if probe_results["format"].get("format_name", UNAV) != "aiff":

                for stream in probe_results["streams"]:

                    if "PCM" not in stream.get("codec_long_name", UNAV):
                        continue

                    if not any(
                            stream.get("codec_long_name", UNAV).startswith(x)
                            for x in ["PCM signed", "PCM unsigned"]):
                        self._errors.append(
                            "%s does not seem to be LPCM format."
                            % stream["codec_long_name"])

            container = False
            for index in range(len(probe_results["streams"]) + 1):
                # FFMpeg has separate "format" (relevant for containers) and
                # "streams" (relevant for all files) elements in its output.
                # We know whether we'll have streams + container or just
                # streams only after scraping the first stream, so there's a
                # risk of trying to add one too many streams. This check
                # prevents constructing more metadata models than there are
                # streams.
                if not container and index == len(probe_results["streams"]):
                    break

                self.streams += list(self.iterate_models(
                    probe_results=probe_results, index=index))

                for stream in self.streams:
                    if stream.hascontainer():
                        container = True

            # Some audio and video files need a bit of a special treatment.
            # They only have one stream, but because ffmpeg reports the format
            # and the stream's codec separately, file-scraper would print two
            # streams (one with the real info and one empty) for them without
            # this check.
            if probe_results["format"].get("format_long_name", UNAV) in [
                                "Audio IFF",
                                "MP2/3 (MPEG audio layer 2/3)",
                                "raw MPEG video",
                                "WAV / WAVE (Waveform Audio)"]:
                self.streams = self.streams[:1]

        except ffmpeg.Error as err:
            self._errors.append("Error in analyzing file with FFProbe.")
            self._errors.append(ensure_text(err.stderr))

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

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNAV.
        """

        toolShell = Shell(["ffmpeg", "-version"])
        """ Find version with capture group to capture integers and dots
            until any other character appears.
        """
        regex = r"[vV]ersion ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, toolShell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            version = UNAV
        return {"ffmpeg": {"version": version}}


class FFMpegScraper(FFMpegMetaScraper):
    """
    Scraper using FFMpeg to check well-formedness and gather metadata.
    """

    # Supported metadata models
    _supported_metadata = [FFMpegSimpleMeta, FFMpegMeta]
    # Run only when checking well-formedness. There is another scraper for
    # the case without checking. The proper metadata is still gathered.
    _only_wellformed = True

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):
        """
        Report whether the scraper supports the given MIME type and version.

        Use super class of super class, i.e. BaseScraper.
        """
        return super(FFMpegMetaScraper, cls).is_supported(
            mimetype=mimetype, version=version,
            check_wellformed=check_wellformed, params=params)

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.
        If the file contains streams that can not be identified or
        is a container with unacceptable av streams, the scraper
        can not check well-formedness.

        :returns: None if there were no errors but a stream was not
                  identified or a container has unacceptable streams,
                  True if the file has been scraped without errors
                  and otherwise False
        """
        # Use super class of super class, i.e. BaseScraper for initial result.
        valid = super(FFMpegMetaScraper, self).well_formed
        unsupported_av_format_found = any(
            stream.av_format_supported() is False for stream in self.streams)

        if valid and unsupported_av_format_found:
            return None

        return valid

    def scrape_file(self):
        """Scrape A/V files.

        We need to probe streams also for checking well-formedness, because
        otherwise we don't know if the MIME types of streams are supported by
        Scraper or not. If the a stream can not be identified by Scraper, then
        well-formedness can not be True.
        """
        super().scrape_file()
        self._validate_file()

    def _validate_file(self):
        """Validate A/V file"""
        shell = Shell(["ffmpeg", "-v", "error", "-i",
                       encode_path(self.filename),
                       "-max_muxing_queue_size", "1024",
                       "-f", "null", "-"])

        if shell.returncode == 0:
            self._messages.append(
                "The file was analyzed successfully with FFMpeg.")
        else:
            self._errors.append("FFMpeg returned invalid return code: %s\n%s" %
                                (shell.returncode, shell.stderr))

        # Do not add errors, if only errors to be filtered exist,
        # otherwise add all errors without filtering
        if _filter_stderr(shell.stderr):
            self._errors.append(shell.stderr)


def _filter_stderr(errors):
    """
    Filter out "bpno became negative" and "Last message repeated".

    Message "bpno became negative" is not considered as error, see e.g.:
    http://ffmpeg.org/pipermail/ffmpeg-devel/2020-April/259454.html

    Message "bpno became invalid" is not considered as error, see:
    https://trac.ffmpeg.org/ticket/5360

    Returns a new string, containing all lines in errors except
    those that contain either "Last message repeated [number] times"
    or both "jpeg2000" and "bpno became negative" or both "jpeg2000" and "bpno
    became invalid".

    Note: Message "Last message repeated" may be targeted also
    to another (valid) error message. It will still be filtered.

    :errors: Stderr result from Shell in scraping
    :returns: Filtered error message result
    """
    constructed_string = ""
    repeat = re.compile("Last message repeated [0-9]+ times")
    for line in str(errors).split("\n"):
        if not line:
            continue
        if "jpeg2000" in line and "bpno became negative" in line:
            continue
        if "jpeg2000" in line and "bpno became invalid" in line:
            continue
        if repeat.match(line.strip()):
            continue
        constructed_string = constructed_string + line + "\n"
    return constructed_string
