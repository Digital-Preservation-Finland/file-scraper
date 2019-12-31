"""Office file scraper."""
from __future__ import unicode_literals

import shutil
import tempfile

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.office.office_model import OfficeMeta
from file_scraper.utils import encode_path


class OfficeScraper(BaseScraper):
    """Office file format scraper."""

    _supported_metadata = [OfficeMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        temp_dir = tempfile.mkdtemp()
        try:
            env = {"HOME": temp_dir}
            shell = Shell([
                "soffice", "--convert-to", "pdf", "--outdir", temp_dir,
                encode_path(self.filename)], env=env)
            if shell.stderr:
                self._errors.append(shell.stderr)
            self._messages.append(shell.stdout)
        except OSError as error:
            self._errors.append("Error handling file: {}".format(error))
        finally:
            shutil.rmtree(temp_dir)
            for md_class in self._supported_metadata:
                if md_class.is_supported(self._mimetype):
                    self.streams.append(md_class())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
