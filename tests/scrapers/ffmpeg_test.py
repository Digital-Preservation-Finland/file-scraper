"""
Test module for ffmpeg.py.

This module tests that:
    - For valid audio and video files the scraping is reported as
      successful, the file is well-formed and metadata is scraped
      correctly.
    - For empty files the results are similar but file is not
      well-formed and errors should contain an error message. The error
      message should contain the following string:
        - With video/x-matroska, video/mpeg, video/mp4, video/MP2T
          files: "Invalid data found when processing input".
        - With audio/mpeg files: "could not find codec parameters"
        - With video/dv files: "Cannot find DV header"
    - For invalid files the file is not well-formed and errors should
      contain an error message. With the files with missing data the
      error message should contain the following string:
        - With video/x-matroska files: "Truncating packet of size"
        - With video/mpeg and video/mp4 files: "end mismatch"
        - With video/MP2T files: "invalid new backstep"
        - With audio/mpeg files: "Error while decoding stream"
        - With video/dv files: "AC EOB marker is absent"
    - The extractor should give an error if PCM stream is not LPCM. This
      is tested with a WAV file which includes A-law PCM format.
    - For mp3 files with wrong version reported in the header, the file
      is not well-formed and errors should contain "Error while decoding
      stream".
    - The mimetypes tested are:
        - video/quicktime
        - video/x-matroska
        - video/dv
        - video/mpeg, with version 1 and 2 separately
        - video/mp4
        - video/MP2T
        - audio/mpeg version 1 file
        - application/mxf
        - audio/flac
        - audio/x-wav
        - audio/x-aiff
        - video/x-ms-asf
    - Whether well-formed check is performed or not, the extractor reports
      the following combinations of mimetypes and versions as supported:
        - video/mpeg, "1" or None
        - video/mp4, "" or None
        - video/MP1S, "" or None
        - video/MP2P, "" or None
        - video/MP2T, "" or None
    - A made up version with supported MIME type is reported as
      supported.
    - A made up MIME type with supported version is reported as not
      supported.
    - Supported MIME type is supported when well-formedness is not
      checked.
    - Scraping is done also when well-formedness is not checked.
    - For containers that have unacceptable av streams, the extractor returns
      None for well-formedness.
    - For unsupported formats, extractor doesn't return  True for
      well-formedness.
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAP, UNAV
from file_scraper.ffmpeg.ffmpeg_extractor import (FFMpegExtractor,
                                                  FFMpegMetaExtractor)
from tests.common import parse_results
from tests.scrapers.stream_dicts import (
    MXF_CONTAINER,
    MXF_JPEG2000_VIDEO,
    )

NO_METADATA = {0: {'index': 0, 'version': UNAV, 'stream_type': UNAV}}
UNAV_MIME = []


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        (
            "valid__mpeg2_mp3.avi",
            {
                "purpose": "Test valid AVI.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
            },
            "video/avi"
        ),
        (
            "valid__dv_lpcm8.mov",
            {
                "purpose": "Test valid MOV with DV and LPCM8.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/quicktime"
        ),
        (
            "valid__h265_aac.mov",
            {
                "purpose": "Test valid MOV with h265 and AAC.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/quicktime"
        ),
        (
            "valid__pal_lossy.dv",
            {
                "purpose": "Test valid DV.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/dv"
        ),
        (
            "valid_4_ffv1.mkv",
            {
                "purpose": "Test valid MKV.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-matroska"
        ),
        (
            "valid_4_h265.mkv",
            {
                "purpose": "Test valid MKV.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-matroska"
        ),
        (
            "valid_1.m1v",
            {
                "purpose": "Test valid MPEG-1.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mpeg"
        ),
        (
            "valid_2.m2v",
            {
                "purpose": "Test valid MPEG-2.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mpeg"
        ),
        (
            "valid__h264_aac.mp4",
            {
                "purpose": "Test valid mp4.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mp4"
        ),
        (
            "valid__h264_aac_mp42.mp4",
            {
                "purpose": "Test valid mp4.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mp4"
        ),
        (
            "valid__h265_aac.mp4",
            {
                "purpose": "Test valid mp4.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mp4"
        ),

        (
            "valid__too_many_packets_buffered.mp4",
            {
                "purpose": "Test valid mp4.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/mp4"
        ),
        (
            "valid_1.mp3",
            {
                "purpose": "Test valid mp3.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "audio/mpeg"
        ),
        (
            "valid__mpeg2_mp3.ts",
            {
                "purpose": "Test valid MPEG-TS.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/MP2T"
        ),
        (
            "valid__h265_aac.ts",
            {
                "purpose": "Test valid MPEG-TS.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/MP2T"
        ),
        (
            "valid__wav.wav",
            {
                "purpose": "Test valid WAV.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "audio/x-wav"
        ),
        (
            "valid_1.3.aiff",
            {
                "purpose": "Test valid AIFF.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "audio/x-aiff"
        ),
        (
            "valid__wma9.wma",
            {
                "purpose": "Test valid WMA.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-ms-asf"
        ),
        (
            "valid__vc1.wmv",
            {
                "purpose": "Test valid WMV.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-ms-asf"
        ),
        (
            "valid__vc1_wma9.wmv",
            {
                "purpose": "Test valid WMV and WMA.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-ms-asf"
        ),
        (
            "valid__aac.m4a",
            {
                "purpose": "test valid m4a.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "audio/mp4"
        ),
        (
            "valid__flac.flac",
            {
                "purpose": "Test valid FLAC audio file",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "audio/flac"
        )
    ]
)
def test_ffmpeg_valid_simple(filename, result_dict, mimetype,
                             evaluate_extractor):
    """
    Test FFMpegExtractor with valid files when no metadata is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams.update(NO_METADATA)

    extractor = FFMpegExtractor(filename=correct.filename, mimetype=mimetype.lower())
    extractor.scrape_file()

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        # TODO codec_quality testing for both mxf files
        (
            "valid__jpeg2000_lossless-wavelet_lossy-subsampling.mxf",
            {
                "purpose": ("Test valid MXF/JPEG2000 with lossless wavelet "
                            "transform and chroma subsampling."),
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MXF_CONTAINER.copy(),
                            1: dict(MXF_JPEG2000_VIDEO.copy(),
                                    **{"data_rate": "3.683156",
                                       "codec_quality": "lossless"})}
            },
            "application/mxf"
        ),
        (
            "valid__jpeg2000_lossless.mxf",
            {
                "purpose": ("Test valid MXF/JPEG2000 with lossless wavelet "
                            "transform and no chroma subsampling."),
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MXF_CONTAINER.copy(),
                            1: dict(MXF_JPEG2000_VIDEO.copy(),
                                    **{"data_rate": "10.030892",
                                       "sampling": UNAP,
                                       "codec_quality": "lossless"})}
            },
            "application/mxf"
        ),
        (
            "valid__jpeg2000.mxf",
            {
                "purpose": "Test valid MXF.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MXF_CONTAINER.copy(),
                            1: MXF_JPEG2000_VIDEO.copy()}
            },
            "application/mxf"
        ),
        (
            "valid__jpeg2000_grayscale.mxf",
            {
                "purpose": "Test valid MXF.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MXF_CONTAINER.copy(),
                            1: dict(MXF_JPEG2000_VIDEO.copy(),
                                    **{"data_rate": "2.21007",
                                       "color": "Grayscale",
                                       "sampling": UNAP})}
            },
            "application/mxf"
        ),
    ]
)
def test_ffmpeg_extractor_valid(filename, result_dict, mimetype,
                              evaluate_extractor):
    """
    Test FFMpegExtractor and FFMpegMetaExtractor with valid files when metadata
    is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)

    extractor = FFMpegExtractor(filename=Path(correct.filename), mimetype=mimetype)
    extractor.scrape_file()

    evaluate_extractor(extractor, correct)

    correct_meta = parse_results(filename, mimetype, result_dict, False)

    extractor_meta = FFMpegMetaExtractor(filename=correct_meta.filename,
                                       mimetype=mimetype)
    extractor_meta.scrape_file()

    evaluate_extractor(extractor_meta, correct_meta)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        (
            "invalid_4_ffv1_missing_data.mkv",
            {
                "purpose": "Test truncated MKV.",
                "stdout_part": "",
                "stderr_part": "Truncating packet of size"
            },
            "video/x-matroska"
        ),
        (
            "invalid__empty.mkv",
            {
                "purpose": "Test empty MKV.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/x-matroska"
        ),
        (
            "invalid__missing_data.dv",
            {
                "purpose": "Test truncated DV.",
                "stdout_part": "",
                "stderr_part": "AC EOB marker is absent"
            },
            "video/dv"
        ),
        (
            "invalid__empty.dv",
            {
                "purpose": "Test empty DV.",
                "stdout_part": "",
                "stderr_part": "Cannot find DV header"
            },
            "video/dv"
        ),
        (
            "invalid_1_missing_data.m1v",
            {
                "purpose": "Test invalid MPEG-1.",
                "stdout_part": "",
                "stderr_part": "Warning MVs not available"
            },
            "video/mpeg"
        ),
        (
            "invalid_1_empty.m1v",
            {
                "purpose": "Test empty MPEG-1.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/mpeg"
        ),
        (
            "invalid_2_missing_data.m2v",
            {
                "purpose": "Test invalid MPEG-2.",
                "stdout_part": "",
                "stderr_part": "Warning MVs not available"
            },
            "video/mpeg"
        ),
        (
            "invalid_2_empty.m2v",
            {
                "purpose": "Test empty MPEG-2.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/mpeg"
        ),
        (
            "invalid__h264_aac_missing_data.mp4",
            {
                "purpose": "Test invalid MPEG-4.",
                "stdout_part": "",
                "stderr_part": "moov atom not found"
            },
            "video/mp4"
        ),
        (
            "invalid__h265_aac_invalid_data.mp4",
            {
                "purpose": "Test invalid MPEG-4.",
                "stdout_part": "",
                "stderr_part": "offset_len 108 is invalid"
            },
            "video/mp4"
        ),
        (
            "invalid__empty.mp4",
            {
                "purpose": "Test invalid MPEG-4.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/mp4"
        ),
        (
            "invalid_1_missing_header.mp3",
            {
                "purpose": "Test invalid mp3.",
                "stdout_part": "",
                "stderr_part": "Header missing"
            },
            "audio/mpeg"
        ),
        (
            "invalid_1_missing_data.mp3",
            {
                "purpose": "Test invalid mp3.",
                "stdout_part": "",
                "stderr_part": "invalid new backstep"
            },
            "audio/mpeg"
        ),
        (
            "invalid_1_wrong_sampling_rate.mp3",
            {
                "purpose": "Test invalid mp3.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "audio/mpeg"
        ),
        (
            "invalid__empty.mp3",
            {
                "purpose": "Test empty mp3",
                "stdout_part": "",
                "stderr_part": "Failed to read frame size"
            },
            "audio/mpeg"
        ),
        (
            "invalid__missing_data.ts",
            {
                "purpose": "Test invalid MPEG-TS.",
                "stdout_part": "",
                "stderr_part": "invalid new backstep"
            },
            "video/MP2T"
        ),
        (
            "invalid__empty.ts",
            {
                "purpose": "Test empty MPEG-TS.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/MP2T"
        ),
        # In EL9 ffmpeg does not print the "Invalid data" error anymore and
        # extractor considers the file to be valid.
        # TODO Remove this test?
        # (
        #     "invalid__jpeg2000_wrong_signature.mxf",
        #     {
        #         "purpose": "Test MXF with invalid header.",
        #         "stdout_part": "",
        #         "stderr_part": "Invalid data found when processing input"
        #     },
        #     "application/mxf"
        # ),
        (
            "invalid__jpeg2000_truncated.mxf",
            {
                "purpose": "Test truncated MXF.",
                "stdout_part": "",
                "stderr_part": "local tag 0x3c0a with 0 size"
            },
            "application/mxf"
        ),
        (
            "invalid__pcm_alaw_format.wav",
            {
                "purpose": "Test WAV file including A-law PCM.",
                "stdout_part": "",
                "stderr_part": "does not seem to be LPCM"
            },
            "audio/x-wav"
        ),
        (
            "invalid_1.3_data_bytes_missing.aiff",
            {
                "purpose": "Test invalid AIFF.",
                "stdout_part": "",
                "stderr_part": (
                    "Invalid PCM packet, data has size 3 but at least a size "
                    "of 4 was expected")
            },
            "audio/x-aiff"
        ),
        (
            "invalid__vc1_missing_data.wmv",
            {
                "purpose": "Test invalid WMV.",
                "stdout_part": "",
                "stderr_part": (
                    "Application provided invalid, non monotonically "
                    "increasing dts to muxer")
            },
            "video/x-ms-asf"
        ),
        (
            "invalid__empty.m4a",
            {
                "purpose": "Test invalid empty m4a.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "audio/mp4"
        ),
        (
            "invalid__bytes_missing.flac",
            {
                "purpose": "Test truncated FLAC audio file",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "audio/flac"
        ),
        (
            "invalid__header_edited.flac",
            {
                "purpose": "Test FLAC audio file with broken header",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "audio/flac"
        )
    ]
)
def test_ffmpeg_extractor_invalid(filename, result_dict, mimetype,
                                evaluate_extractor):
    """
    Test FFMpegExtractor with invalid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams = {}

    extractor = FFMpegExtractor(filename=correct.filename,
                              mimetype=mimetype)
    extractor.scrape_file()

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filepath", "mimetype"],
    [
        (
            "tests/data/video_x-matroska/invalid_4_ffv1_aac.mkv",
            "video/x-matroska"
        ),
        (
            "tests/data/video_x-matroska/invalid_4_mp1.mkv",
            "video/x-matroska"
        ),
        (
            "tests/data/video_x-ms-asf/invalid__vc1_mp3.wmv",
            "video/x-ms-asf"
        )
    ]
)
def test_ffmpeg_extractor_wellformed_none(filepath, mimetype):
    """
    Test that FFMpegExtractor returns None for well-formedness
    when all the streams are well-formed, but some of the av
    streams are not acceptable inside the container.
    """
    extractor = FFMpegExtractor(filename=Path(filepath), mimetype=mimetype)
    extractor.scrape_file()

    # Ensure that file was validated to avoid false positive
    assert 'The file was analyzed successfully with FFMpeg.' \
        in extractor.messages()

    assert extractor.well_formed is None


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_ffmpeg_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "video/avi"
    path = Path("tests/data", mimetype.replace("/", "_"))
    testfile = path / "valid__mpeg2_mp3.avi"

    extractor = FFMpegExtractor(filename=testfile,
                              mimetype=mimetype)

    extractor.scrape_file()

    assert "FFMpeg returned invalid return code: -1\n" in extractor.errors()


@pytest.mark.parametrize(
    ["mimetype", "version"],
    [
        ("video/avi", ""),
        ("video/mpeg", "1"),
        ("video/mp4", ""),
        ("video/mp2t", ""),
        ("application/mxf", "")
    ]
)
def test_is_supported(mimetype, version):
    """
    Test is_supported method.

    :mime: Predefined mimetype
    :ver: Predefined version
    """
    assert FFMpegExtractor.is_supported(mimetype, version, True)
    assert FFMpegExtractor.is_supported(mimetype, None, True)
    assert not FFMpegExtractor.is_supported(mimetype, version, False)
    assert FFMpegExtractor.is_supported(mimetype, "foo", True)
    assert not FFMpegExtractor.is_supported("foo", version, True)

    assert not FFMpegMetaExtractor.is_supported(mimetype, version, True)

    # Metadata gathering supported only for MXF
    if mimetype == "application/mxf":
        assert FFMpegMetaExtractor.is_supported(mimetype, version, False)
    else:
        assert not FFMpegMetaExtractor.is_supported(mimetype, version, False)


@pytest.mark.parametrize(
    "filename",
    [
        # Unsupported stream in unsupported container
        "tests/data/application_vnd.rn-realmedia/invalid__ac3.ra",
        # Supported stream in unsupported container
        "tests/data/application_vnd.rn-realmedia/invalid__aac.ra"
    ]
)
def test_unsupported_format(filename):
    """Test that unsupported format is not well formed."""
    # Scrape the file. Use some supported mimetype, otherwise the
    # Extractor will refuse to scrape.
    extractor = FFMpegExtractor(filename=Path(filename), mimetype="audio/mp4")
    extractor.scrape_file()

    # Ensure that file was validated to avoid false positive
    assert 'The file was analyzed successfully with FFMpeg.' \
        in extractor.messages()

    assert not extractor.well_formed


def test_tools():
    """
    Test that tools don't return UNAV or None
    """
    # validity or invalidity of the file doesn't matter for tools
    extractor = FFMpegExtractor(filename=Path(""), mimetype="")
    assert extractor.tools()["ffmpeg"]["version"] not in (UNAV, None)
