from file_scraper.state import (MimetypeState,
                                MimetypeResultState,
                                MimetypeParameterState,
                                ResultStateWithForm,
                                ResultState,
                                LockedMimetypeState,
                                )
from unittest.mock import patch


class DummyApparatus:
    pass


def test_result_state_initialization():
    parent = DummyApparatus()
    rs = ResultState(_parent_object=parent)
    assert rs._parent_object is parent
    assert rs.messages == []
    assert rs.error_messages == []


def test_result_state_with_form():
    parent = DummyApparatus()
    rsf = ResultStateWithForm(_parent_object=parent, well_formedness=True)
    assert rsf._parent_object is parent
    assert rsf.well_formedness is True
    assert rsf.messages == []
    assert rsf.error_messages == []


def test_mimetype_state_properties():
    ms = MimetypeState(_mimetype="application/json", _version="1.0")
    assert ms.mimetype == "application/json"
    assert ms.version == "1.0"
    ms.mimetype = "text/plain"
    ms.version = "2.0"
    assert ms.mimetype == "text/plain"
    assert ms.version == "2.0"


def test_mimetype_state_bool():
    ms1 = MimetypeState(_mimetype=None, _version=None)
    ms2 = MimetypeState(_mimetype="application/json", _version=None)
    ms3 = MimetypeState(_mimetype=None, _version="1.0")
    assert not ms1
    assert ms2
    assert ms3


def test_mimetype_state_to_result():
    parent = DummyApparatus()
    ms = MimetypeState(_mimetype="application/json", _version="1.0")
    result = ms.to_result(parent)
    assert isinstance(result, MimetypeResultState)
    assert result.mimetype == "application/json"
    assert result.version == "1.0"
    assert result.parent_object is parent


def test_locked_mimetype_state_setters():
    lms = LockedMimetypeState(_mimetype="application/json", _version="1.0")
    with patch("file_scraper.logger.LOGGER.error") as mock_error:
        lms.mimetype = "text/plain"
        lms.version = "2.0"
        assert mock_error.call_count == 2
        mock_error.assert_any_call(
            "Cannot overwrite mimetype in %s", "LockedMimetypeState"
        )
        mock_error.assert_any_call(
            "Cannot overwrite version in %s", "LockedMimetypeState"
        )


def test_mimetype_parameter_state_inheritance():
    mps = MimetypeParameterState(_mimetype="application/xml", _version="1.1")
    assert isinstance(mps, LockedMimetypeState)
    assert mps.mimetype == "application/xml"
    assert mps.version == "1.1"


def test_mimetype_result_state_inheritance():
    parent = DummyApparatus()
    mrs = MimetypeResultState(_mimetype="image/png",
                              _version="1.2",
                              parent_object=parent)
    assert isinstance(mrs, LockedMimetypeState)
    assert mrs.mimetype == "image/png"
    assert mrs.version == "1.2"
    assert mrs.parent_object is parent
