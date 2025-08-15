"""
Metadata extractor for pdf files, based on Ghostscript.

This extractor does not scrape metadata but instead checks well-formedness
of pdf versions 1.7, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u."""
import re

from file_scraper.base import BaseExtractor
from file_scraper.ghostscript.ghostscript_model import GhostscriptMeta
from file_scraper.shell import Shell
from file_scraper.logger import LOGGER
from file_scraper.utils import ensure_text
from file_scraper.defaults import UNAV


class GhostscriptExtractor(BaseExtractor[GhostscriptMeta]):
    """Ghostscript pdf extractor."""

    # Supported mimetype and versions
    _supported_metadata = [GhostscriptMeta]
    _only_wellformed = True   # Only well-formed check

    def extract(self):
        """Scrape file."""
        shell = Shell(["gs", "-o", "/dev/null", "-sDEVICE=nullpage",
                       self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"Ghostscript returned invalid return code: "
                f"{shell.returncode}\n{shell.stderr}"
                )

        # Ghostscript may print characters which cannot be converted to UTF-8
        stdout_message = ensure_text(shell.stdout_raw, errors='replace')
        stderr_message = ensure_text(shell.stderr_raw, errors='replace')

        # Ghostscript will result 0 if it can repair errors.
        # However, in those cases an error is logged to either _errors or
        # _messages. This case should be handled as well-formed failure.
        if stderr_message:
            self._errors.append(stderr_message)
            self._errors.append(stdout_message)

        # If no errors have been logged, the file is valid.
        else:
            self._messages.append(stdout_message)
            self._messages.append("Well-Formed and valid")

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    @property
    def well_formed(self):
        """
        Overwrite the normal well-formedness check to also look at the stdout.

        This is needed as ghostscript can log errors to stdout if it has been
        able to repair the file. In these cases, extractor messages contain
        "**** Error" or "**** Warning" (any capitalization is detected), which
        is interpreted as well-formedness failure.

        :returns: True if the file is well-formed, False if it is not.
        """
        for message in self._messages:
            if ("**** error" in message.lower() or
                    "**** warning" in message.lower()):
                return False
        return super().well_formed

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        version_shell = Shell(["gs", "-version"])
        regex = r"Ghostscript ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, version_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not retrieve GhostScript version from stdout: %s",
                version_shell.stdout
            )
            version = UNAV

        return {"Ghostscript": {
            "version": version
            }
        }
