"""Office file scraper."""
from __future__ import unicode_literals

import os.path
import shutil
import tempfile

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.office.office_model import OfficeMeta
from file_scraper.utils import encode_path
from file_scraper.config import SOFFICE_PATH


class OfficeScraper(BaseScraper):
    """Office file format scraper."""

    _supported_metadata = [OfficeMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        temp_dir = tempfile.mkdtemp()

        cmd = "soffice"
        if os.path.isfile(SOFFICE_PATH):
            cmd = SOFFICE_PATH

        try:
            env = {"HOME": temp_dir}
            shell = Shell([
                cmd, "--convert-to", "pdf", "--outdir", temp_dir,
                encode_path(self.filename)], env=env)
            if shell.stderr:
                self._errors.append(shell.stderr)
            if shell.returncode != 0:
                self._errors.append(
                    "Office returned invalid return code: %s\n%s"
                    % (shell.returncode, shell.stderr))
            self._messages.append(shell.stdout)
        except OSError as error:
            self._errors.append("Error handling file: {}".format(error))
        finally:
            shutil.rmtree(temp_dir)
            self.streams = list(self.iterate_models())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
