"""
Metadata extractor for pdf files, based on Ghostscript.

This extractor does not scrape metadata but instead checks well-formedness
of pdf versions 1.7, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u.
"""

from __future__ import annotations

import re

from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.ghostscript.ghostscript_model import GhostscriptMeta
from file_scraper.logger import LOGGER
from file_scraper.shell import Shell
from file_scraper.utils import ensure_text


class GhostscriptExtractor(BaseExtractor[GhostscriptMeta]):
    """Ghostscript pdf extractor."""

    # Supported mimetype and versions
    _supported_metadata = [GhostscriptMeta]
    _only_wellformed = True  # Only well-formed check

    _allow_unav_mime = True
    _allow_unav_version = True

    def _extract(self) -> None:
        """Scrape file."""
        shell = Shell(
            [
                "gs",
                "-o",
                "/dev/null",
                "-sDEVICE=nullpage",
                # Redirect stdout to stderr. By default, Ghostscript should
                # output errors to stderr and warnings to stdout, but some
                # warnings are printed to stderr. To fix this, we redirect
                # everything to stderr and parse the whole output.
                "-sstdout=%stderr",
                self.filename,
            ]
        )

        # Ghostscript may print characters which cannot be converted to UTF-8
        output = ensure_text(shell.stderr_raw, errors="replace")

        if shell.returncode != 0:
            self._errors.append(
                "Ghostscript returned invalid return code: "
                f"{shell.returncode}\n{output}"
            )

        extracted_messages = self._extract_messages(output)

        self._errors.extend(extracted_messages["errors"])

        if not self._errors:
            self._messages.extend(extracted_messages["warnings"])
            self._messages.append("Well-Formed and valid")
        else:
            # If any errors were found, add all warnings to errors.
            # Ghostscript can fix some errors on its own, but in this case, the
            # error section will contain an "<error> was repaired" message and
            # the actual error will be under warnings.
            self._errors.extend(extracted_messages["warnings"])

        self.streams = list(self.iterate_models())

    def _extract_messages(self, text: str) -> dict[str, list[str]]:
        """Extract warning and error messages from Ghostscript output.

        :param text: Ghostscript output.
        :returns: Dict with lists of warnings and errors.
        """
        errors_marker = (
            "The following errors were encountered at least "
            "once while processing this file:"
        )
        warnings_marker = (
            "The following warnings were encountered at least "
            "once while processing this file:"
        )

        return {
            "errors": self._extract_section_lines(
                text,
                errors_marker,
                warnings_marker,
            ),
            "warnings": self._extract_section_lines(
                text,
                warnings_marker,
                None,
            ),
        }

    @staticmethod
    def _extract_section_lines(
        text: str, marker: str, stop_marker: str | None
    ) -> list[str]:
        """Extract lines from a specified section of Ghostscript output.

        :param text: Ghostscript output.
        :param marker: Start of section to extract.
        :param stop_marker: End of section to extract. If `None`, extract until
            the summary section (starting with "****") is reached.
        :returns: List of lines in the section.
        """
        if marker not in text:
            return []

        section = text.split(marker, 1)[1]

        if stop_marker and stop_marker in section:
            section = section.split(stop_marker, 1)[0]

        section = section.split("****", 1)[0]

        return [line.strip() for line in section.splitlines() if line.strip()]

    def tools(self) -> dict[str, dict[str, str]]:
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
                version_shell.stdout,
            )
            version = UNAV

        return {"Ghostscript": {"version": version}}
