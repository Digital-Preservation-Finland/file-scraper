"""
The module tests that:
    - Given command is run and its returncode is returned as the first member
      of the returned tuple.
    - If no stdout file is given, the output of the command is returned as the
      second member of the returned tuple.
    - The stderr output of t he command is returned as the third member of the
      returned tuple.
    - If a stdout file is given, the stdout output of the command is recorded
      in that file.
    - If custom environment variables are supplied, they are used when running
      the command.
"""

import os
from tempfile import TemporaryFile

import six

import pytest

from file_scraper.shell import Shell


@pytest.mark.parametrize(
    ["command", "expected_returncode", "expected_stdout", "expected_stderr"],
    [
        (["echo", "testing"], 0, "testing\n", ""),
        (["seq", "5"], 0, "1\n2\n3\n4\n5\n", ""),
        (["cd", "nonexistentdir"], 1, "",
         "/usr/bin/cd: line 2: cd: nonexistentdir: "
         "No such file or directory\n")
    ]
)
def test_shell(command, expected_returncode, expected_stdout,
               expected_stderr):
    """
    Test running commands normally.

    :command: Shell command
    :expected_returncode: Expected return code
    :expected_stdout: Expected stdout
    :expected_stderr: Expected stderr
    """

    shell = Shell(command)

    assert isinstance(shell.stdout, six.text_type)
    assert isinstance(shell.stderr, six.text_type)

    assert isinstance(shell.stdout_raw, six.binary_type)
    assert isinstance(shell.stderr_raw, six.binary_type)

    assert shell.returncode == expected_returncode
    assert shell.stderr == expected_stderr
    assert shell.stdout == expected_stdout


def test_shell_output_to_file():
    """Test having output of a shell command directed to a file"""
    with TemporaryFile("w+") as outfile:
        shell = Shell(["seq", "5"], stdout=outfile)

        assert shell.returncode == 0
        assert not shell.stdout
        assert not shell.stderr

        outfile.seek(0)
        expected_number = 1
        for line in outfile:
            assert line == six.text_type(expected_number) + "\n"
            expected_number += 1


def test_shell_with_env():
    """Test running commands using custom environment variables."""
    custom_env = os.environ.copy()
    custom_env["TEST_VARIABLE"] = "testing"
    shell = Shell(["printenv", "TEST_VARIABLE"], env=custom_env)

    assert shell.returncode == 0
    assert shell.stdout == "testing\n"
    assert not shell.stderr
