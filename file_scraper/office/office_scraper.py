"""Office file scraper."""

import shutil
import tempfile

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.office.office_model import OfficeMeta


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
                "soffice", "--convert-to",
                "pdf", "--outdir", temp_dir, self.filename
                ], env=env)
            if shell.stderr:
                self._errors.append(shell.stderr)
            if shell.returncode != 0:
                self._errors.append(
                    f"Office returned invalid return code: "
                    f"{shell.returncode}\n{shell.stderr}")
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
        version_shell = Shell(["soffice", "--version"])
        return {
            "libreoffice": {
                "version": version_shell.stdout.split(" ")[1]
            }
        }
