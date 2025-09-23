"""
States exist to encapsulate data which is used often across many different
classes and purposes.

The purpose is to prevent data manipulation without explicit intent to do so
and to preserve the origin of the data as often as possible.

Encapsulation in the other hand helps to define function scope and makes
refactoring easier.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from file_scraper.logger import LOGGER

if TYPE_CHECKING:
    from file_scraper.base import BaseApparatus

# Evaluate again after Python 3.10. In python 3.10 kw_only parameter is
# available for dataclass inheritance, so default values are not required
# anymore in the childclass with this feature.


# TODO utilize ResultState
@dataclass()
class ResultState:
    """Result which generates an list of messages and error messages"""
    _parent_object: BaseApparatus
    messages: list[str] = field(default_factory=list[str])
    error_messages: list[str] = field(default_factory=list[str])


# TODO utilize ResultStateWithForm or migrate property to base class.
@dataclass()
class ResultStateWithForm(ResultState):
    """Includes well_formedness on top of the existing messages"""
    well_formedness: bool = None


@dataclass
class MimetypeState:
    """
    Mimetype and version of the mimetype are inherently tied together.
    """
    _mimetype: str | None
    _version: str | None

    @property
    def mimetype(self) -> str | None:
        return self._mimetype

    @mimetype.setter
    def mimetype(self, value: str | None) -> None:
        self._mimetype = value

    @property
    def version(self) -> str | None:
        return self._version

    @version.setter
    def version(self, value: str | None) -> None:
        self._version = value

    def __bool__(self):
        if self._mimetype is None and self._version is None:
            return False
        else:
            return True

    def to_result(self, parent_object) -> MimetypeResultState:
        return MimetypeResultState(
            self.mimetype,
            self.version,
            parent_object)


@dataclass
class LockedMimetypeState(MimetypeState):
    """
    Replaces the frozed property of dataclass by preventing setters instead
    """
    @MimetypeState.mimetype.setter
    def mimetype(self, value: str | None) -> None:
        """Using properties to freeze this dataclass"""
        LOGGER.error(
            "Cannot overwrite mimetype in %s", self.__class__.__name__)

    @MimetypeState.version.setter
    def version(self, value: str | None) -> None:
        """Using properties to freeze this dataclass"""
        LOGGER.error(
            "Cannot overwrite version in %s", self.__class__.__name__)


@dataclass
class MimetypeParameterState(LockedMimetypeState):
    """
    Specifies that the state is given as a parameter and prevents the
    modification of the state after initial creation
    """


@dataclass
class MimetypeResultState(LockedMimetypeState):
    """
    Specifies that the state is produced by some object
    """
    parent_object: object
