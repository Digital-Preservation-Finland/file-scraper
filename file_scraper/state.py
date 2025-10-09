"""
States exist to encapsulate data which is used often across many different
classes and purposes.

The purpose is to prevent data manipulation without explicit intent to do so
and to preserve the origin of the data as often as possible.

Encapsulation in the other hand helps to define function scope and makes
refactoring easier.
"""
from __future__ import annotations
from typing import NamedTuple


class Mimetype(NamedTuple):
    """
    Mimetype represents a media type which consists of
    the mimetype and version of the mimetype
    """
    mimetype: str
    version: str | None
