"""Office file extractor."""

import shutil
import tempfile

from file_scraper.base import BaseExtractor
from file_scraper.logger import LOGGER
from file_scraper.office.office_model import OfficeMeta
from file_scraper.shell import Shell


class OfficeExtractor(BaseExtractor[OfficeMeta]):
    """Office file format extractor."""

    _supported_metadata = [OfficeMeta]
    _only_wellformed = True  # Only well-formed check

    _allow_unav_mime = True
    _allow_unav_version = True

    def extract(self):
        """Scrape file."""
        temp_dir = tempfile.mkdtemp()
        LOGGER.debug(
            "Temporary directory %s created for OfficeExtractor", temp_dir
        )

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
            LOGGER.warning("Error handling file", exc_info=True)
            self._errors.append(f"Error handling file: {error}")
        finally:
            shutil.rmtree(temp_dir)
            self.streams = list(self.iterate_models())
            self._validate()

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        version_shell = Shell(["soffice", "--version"])
        return {
            "libreoffice": {
                "version": version_shell.stdout.split(" ")[1]
            }
        }
