"""WARC file extractor using Warchaeology."""

from __future__ import annotations

import json

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.warchaeology.warchaeology_model import WarchaeologyMeta


class WarchaeologyExtractor(BaseExtractor[WarchaeologyMeta]):
    """Warchaeology WARC file extractor.

    .. seealso:: https://nlnwa.github.io/warchaeology/
    """

    _supported_metadata = [WarchaeologyMeta]

    def extract(self) -> None:
        """Extract WARC file."""
        shell = Shell(
            [
                "warc",
                "validate",
                self.filename,
                "--log-format=json",
                "--force",
                "--suffixes=",
            ]
        )
        errors, messages, files, records = self.parse_output(shell.stderr)
        self._messages.extend(messages)

        if files != 1:
            self._errors.append(f"Invalid number of input files: {files}")
            return

        if records == 0:
            self._errors.append("No WARC records found in file")

        self._errors.extend(errors)

        if not self._errors:
            self._messages.append("Well-Formed and valid")

        self.streams = list(
            self.iterate_models(
                well_formed=self.well_formed,
                header=self._get_header(),
            )
        )
        self._check_supported()

    def _get_header(self) -> bytes:
        shell = Shell(
            ["warc", "cat", self.filename, "--header", "--suffixes="]
        )
        return shell.stdout_raw

    @staticmethod
    def parse_output(output: str) -> tuple[list[str], list[str], int, int]:
        """Parse Warcheology output.

        Warchaeology prints everything to stderr.

        :param output: stderr output from Warchaology.
        :returns: (error list, message list, file count, record count) tuple.
        """
        errors = []
        messages = []
        files = 0
        records = 0
        lines = output.splitlines()
        for line in lines:
            entry = json.loads(line)
            if entry["level"] == "ERROR":
                errors.append(entry["error"])
            elif entry["level"] == "WARN":
                messages.append(entry["msg"])
            elif entry["msg"] == "Total":
                files = entry["files"]
                records = entry["records"]

        return errors, messages, files, records

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        shell = Shell(["warc", "--version"])
        version = shell.stdout.strip()
        return {"Warchaeology": {"version": version}}
