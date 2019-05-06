"""FFMpeg wellformed scraper."""
from file_scraper.base import BaseScraper, Shell
from file_scraper.ffmpeg.ffmpeg_model import FFMpegMeta
from file_scraper.utils import ensure_str


class FFMpegScraper(BaseScraper):
    """FFMpeg Wellformed scraper."""

    # Supported mimetypes
    _supported_metadata = [FFMpegMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape A/V files."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        shell = Shell(["ffmpeg", "-v", "error", "-i", self.filename, "-f",
                       "null", "-"])

        if shell.returncode == 0:
            self._messages.append("The file was analyzed successfully.")

        if shell.stderr:
            self._errors.append(ensure_str(shell.stderr))
        if shell.stdout:
            self._messages.append(ensure_str(shell.stdout))

        for md_class in self._supported_metadata:
            self.streams.append(md_class())
