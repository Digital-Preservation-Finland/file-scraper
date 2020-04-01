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
            self.streams = list(self.iterate_models())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
