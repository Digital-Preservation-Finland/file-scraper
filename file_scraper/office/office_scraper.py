"""Office file scraper."""
import os
import shutil
import tempfile

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.office.office_model import OfficeMeta
from file_scraper.config import get_value


def _choose_cmd():
    if os.path.isfile(get_value("SOFFICE_PATH")):
        return get_value("SOFFICE_PATH")
    else:
        return "soffice"


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
                _choose_cmd(), "--convert-to", "pdf", "--outdir",
                temp_dir, os.fsencode(self.filename)], env=env)
            if shell.stderr:
                self._errors.append(shell.stderr)
            if shell.returncode != 0:
                self._errors.append(
                    "Office returned invalid return code: %s\n%s"
                    % (shell.returncode, shell.stderr))
            self._messages.append(shell.stdout)
        except OSError as error:
            self._errors.append(f"Error handling file: {error}")
        finally:
            shutil.rmtree(temp_dir)
            self.streams = list(self.iterate_models())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the scraper

        :returns: a dictionary with the used software or UNAV.
        """
        version_shell = Shell([_choose_cmd(), "--version"])
        return {
            "libreoffice": {
                "version": version_shell.stdout.split(" ")[1]
            }
        }
