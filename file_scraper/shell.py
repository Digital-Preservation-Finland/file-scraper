"""Wrapper for calling external commands"""

import os
import subprocess
import pty

from file_scraper.utils import ensure_text


class Shell:
    """Shell command handler for non-Python 3rd party software."""

    def __init__(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                 use_pty=False, env=None):
        """
        Initialize instance.

        :param command: Command to execute as list
        :param output_file: Output file handle
        :param use_pty: Fake a terminal device for stdin. Some applications
                         will require this.
        :param env: Environment variables
        """
        self.command = command

        self._stdout = None
        self._stderr = None
        self._returncode = None

        self.stdout_file = stdout
        self.stderr_file = stderr

        self._use_pty = use_pty

        self._env = os.environ.copy()

        if env:
            for key, value in env.items():
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
                self._returncode = proc.returncode

            if self._use_pty:
                os.close(pty_master)
                os.close(pty_slave)

        return {
            "returncode": self._returncode,
            "stderr": self._stderr,
            "stdout": self._stdout
            }
