"""Wrapper for calling external commands"""

import os
import subprocess

from file_scraper.utils import ensure_text


class Shell(object):
    """Shell command handler for non-Python 3rd party software."""

    def __init__(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                 env=None):
        """
        Initialize instance.

        :command: Command to execute as list
        :output_file: Output file handle
        :env: Environment variables
        """
        self.command = command

        self._stdout = None
        self._stderr = None
        self._returncode = None

        self.stdout_file = stdout
        self.stderr_file = stderr

        self._env = os.environ.copy()

        if env:
            for key, value in iter(dict.items(env)):
                self._env[key] = value

    @property
    def returncode(self):
        """
        Returncode from the command.

        :returns: Returncode
        """
        return self.popen()["returncode"]

    @property
    def stderr(self):
        """
        Standard error output from the command.

        :returns: Stderr as unicode string
        """
        if self.stderr_raw is None:
            return None
        return ensure_text(self.stderr_raw)

    @property
    def stdout(self):
        """
        Command standard error output.

        :returns: Stdout as unicode string
        """
        if self.stdout_raw is None:
            return None
        return ensure_text(self.stdout_raw)

    @property
    def stderr_raw(self):
        """
        Standard error output from the command.

        :returns: Stderr as byte string
        """
        return self.popen()["stderr"]

    @property
    def stdout_raw(self):
        """
        Command standard error output.

        :returns: Stdout as byte string
        """
        return self.popen()["stdout"]

    def popen(self):
        """
        Run the command and store results to class attributes for caching.

        :returns: Returncode, stdout, stderr as dictionary
        """

        if self._returncode is None:

            # A context manager would be nice, but Python 2 version of
            # subprocess does not support it.
            # pylint: disable=consider-using-with
            proc = subprocess.Popen(
                args=self.command,
                stdout=self.stdout_file,
                stderr=self.stderr_file,
                shell=False,
                env=self._env)

            (self._stdout, self._stderr) = proc.communicate()
            self._returncode = proc.returncode

        return {
            "returncode": self._returncode,
            "stderr": self._stderr,
            "stdout": self._stdout
            }
