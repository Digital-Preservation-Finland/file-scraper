"""Wrapper for calling external commands"""
from __future__ import annotations

from collections.abc import Sequence
import os
from pathlib import Path
import pty
import subprocess
from typing import TypedDict, IO

from file_scraper.logger import LOGGER
from file_scraper.utils import ensure_text
from file_scraper.paths import resolve_command


class Shell:
    """Shell command handler for non-Python 3rd party software."""

    def __init__(
        self,
        command: Sequence[str | bytes | Path],
        stdout: int | IO[str] | IO[bytes] = subprocess.PIPE,
        stderr: int | IO[str] | IO[bytes] = subprocess.PIPE,
        use_pty: bool = False,
        env: dict | None = None,
    ) -> None:
        """
        Initialize instance.

        :param command: Command to execute as list
        :param output_file: Output file handle
        :param use_pty: Fake a terminal device for stdin. Some applications
            will require this.
        :param env: Environment variables
        """
        command = list(command)
        resolved_path = resolve_command(command.pop(0))
        command.insert(0, resolved_path)
        self.command = command

        self._stdout = b""
        self._stderr = b""
        self._returncode = None

        self.stdout_file = stdout
        self.stderr_file = stderr

        self._use_pty = use_pty

        self._env = os.environ.copy()

        if env:
            for key, value in env.items():
                self._env[key] = value

    @property
    def returncode(self) -> int:
        """
        Returncode from the command.

        :returns: Returncode
        """
        return self.popen()["returncode"]

    @property
    def stderr(self) -> str:
        """
        Standard error output from the command.

        :returns: Stderr as unicode string
        """
        return ensure_text(self.stderr_raw)

    @property
    def stdout(self) -> str:
        """
        Command standard error output.

        :returns: Stdout as unicode string
        """
        return ensure_text(self.stdout_raw)

    @property
    def stderr_raw(self) -> bytes:
        """
        Standard error output from the command.

        :returns: Stderr as byte string
        """
        return self.popen()["stderr"]

    @property
    def stdout_raw(self) -> bytes:
        """
        Command standard error output.

        :returns: Stdout as byte string
        """
        return self.popen()["stdout"]

    class _POpenResults(TypedDict):
        returncode: int
        stderr: bytes
        stdout: bytes

    def popen(self) -> _POpenResults:
        """
        Run the command and store results to class attributes for caching.

        :returns: Returncode, stdout, stderr as dictionary
        """

        if self._returncode is None:
            LOGGER.debug("Executing '%s'...", self.command)

            # Some applications (*cough*, `pngcheck`) are stupid and check
            # if the stdin refers to a terminal device (using `isatty(0)`)
            # and act differently depending on the case (print help
            # if it's a terminal device,
            # otherwise assume stdin should be read for input).
            # Generally, the value `-` is passed to the application when we
            # actually want the stdin to be read, and `-h` when we want a help
            # printout.
            # For applications where that is not an option,
            # use a pseudo-terminal on demand to fool the application.
            stdin = None
            if self._use_pty:
                pty_master, pty_slave = pty.openpty()
                stdin = pty_master

            with subprocess.Popen(
                    args=self.command,
                    stdout=self.stdout_file,
                    stderr=self.stderr_file,
                    stdin=stdin,
                    shell=False,
                    env=self._env) as proc:
                (self._stdout, self._stderr) = proc.communicate()
                self._stdout = self._stdout or b""
                self._stderr = self._stderr or b""
                self._returncode = proc.returncode

            if self._use_pty:
                os.close(pty_master)
                os.close(pty_slave)

            LOGGER.info(
                "Command '%s' finished with exit code %d",
                self.command, self._returncode
            )

            if self._returncode != 0:
                LOGGER.debug(
                    "Command failed with stdout: %s, stderr: %s",
                    self._stdout[0:8192],
                    self._stderr[0:8192]
                )
        return {
            "returncode": self._returncode,
            "stderr": self._stderr,
            "stdout": self._stdout,
        }
