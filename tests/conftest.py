"""Configure py.test default values and functionality."""

import tempfile
import shutil

import pytest


@pytest.yield_fixture(scope="function")
def testpath():
    """
    Creates temporary directory and clean up after testing.

    :yields: Path to temporary directory
    """
    temp_path = tempfile.mkdtemp(prefix="tests.testpath.")
    yield temp_path
    shutil.rmtree(temp_path)
