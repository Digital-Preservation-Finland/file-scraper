"""FFMpeg wellformed scraper."""
from file_scraper.base import BaseScraper, Shell
from file_scraper.ffmpeg.ffmpeg_model import FFMpegMeta
from file_scraper.utils import ensure_str

try:
    import ffmpeg
except ImportError:
    pass


class FFMpegScraper(BaseScraper):
    """FFMpeg Wellformed scraper."""

    # Supported mimetypes
    _supported_metadata = [FFMpegMeta]

    def scrape_file(self):
        """Scrape A/V files."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        try:
            probe_results = ffmpeg.probe(self.filename)
            streams = [probe_results["format"]] + probe_results["streams"]
            for stream in streams:
                if "index" not in stream:
                    stream["index"] = 0
                else:
                    stream["index"] = stream["index"] + 1
        except ffmpeg.Error as err:
            self._errors.append("Error in analyzing file.")
            self._errors.append(ensure_str(err.stderr))

        # this detects empty files and other problems
        shell = Shell(["ffmpeg", "-v", "error", "-i", self.filename, "-f",
                       "null", "-"])
        if shell.returncode == 0:
            self._messages.append("The file was analyzed successfully.")
        if shell.stderr:
            self._errors.append(ensure_str(shell.stderr))
            return

        for index in range(len(streams)):
            for md_class in self._supported_metadata:
                self.streams.append(md_class(probe_results, index))
        
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
