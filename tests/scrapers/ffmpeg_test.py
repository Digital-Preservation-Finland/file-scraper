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
    - The scraper should give an error if PCM stream is not LPCM. This
      is tested with a WAV file which includes A-law PCM format.
    - For mp3 files with wrong version reported in the header, the file
      is not well-formed and errors should contain "Error while decoding
      stream".
    - The mimetypes tested are:
        - video/quicktime containing dv video and lpcm8 audio stream
        - video/x-matroska containing ffv1 video stream
        - video/dv
        - video/mpeg, with version 1 and 2 separately
        - video/mp4 containing h264 video and aac audio streams
        - video/MP2T file
        - audio/mpeg version 1 file
        - application/mxf
        - audio/x-wav
        - audio/x-aiff
        - video/x-ms-asf
    - Whether well-formed check is performed or not, the scraper reports
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
"""
from __future__ import unicode_literals

import pytest

from file_scraper.defaults import UNAP, UNAV
from file_scraper.ffmpeg.ffmpeg_scraper import (FFMpegScraper,
                                                FFMpegMetaScraper)
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
            "valid__wma_9.wma",
            {
                "purpose": "Test valid WMA.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-ms-asf"
        ),
        (
            "valid__vc_1_wma_9.wmv",
            {
                "purpose": "Test valid WMV and WMA.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": ""
            },
            "video/x-ms-asf"
        ),
    ]
)
def test_ffmpeg_valid_simple(filename, result_dict, mimetype,
                             evaluate_scraper):
    """
    Test FFMpegScraper with valid files when no metadata is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams.update(NO_METADATA)

    scraper = FFMpegScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


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
def test_ffmpeg_scraper_valid(filename, result_dict, mimetype,
                              evaluate_scraper):
    """
    Test FFMpegScraper and FFMpegMetaScraper with valid files when metadata
    is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)

    scraper = FFMpegScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)

    correct_meta = parse_results(filename, mimetype, result_dict, False)

    scraper_meta = FFMpegMetaScraper(filename=correct_meta.filename,
                                     mimetype=mimetype)
    scraper_meta.scrape_file()

    evaluate_scraper(scraper_meta, correct_meta)


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
                "stderr_part": "end mismatch"
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
                "stderr_part": "end mismatch"
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
            "invalid__empty.mp4",
            {
                "purpose": "Test invalid MPEG-4.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "video/mp4"
        ),
        (
            "invalid_1_missing_data.mp3",
            {
                "purpose": "Test invalid mp3.",
                "stdout_part": "",
                "stderr_part": "Header missing"
            },
            "audio/mpeg"
        ),
        (
            "invalid_1_wrong_version.mp3",
            {
                "purpose": "Test invalid mp3.",
                "stdout_part": "",
                "stderr_part": "Error while decoding stream"
            },
            "audio/mpeg"
        ),
        (
            "invalid__empty.mp3",
            {
                "purpose": "Test empty mp3",
                "stdout_part": "",
                "stderr_part": "could not find codec parameters"
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
        (
            "invalid__jpeg2000_wrong_signature.mxf",
            {
                "purpose": "Test MXF with invalid header.",
                "stdout_part": "",
                "stderr_part": "Invalid data found when processing input"
            },
            "application/mxf"
        ),
        (
            "invalid__jpeg2000_truncated.mxf",
            {
                "purpose": "Test truncated MXF.",
                "stdout_part": "",
                "stderr_part": "IndexSID 0 segment at 0 missing"
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
        )
    ]
)
def test_ffmpeg_scraper_invalid(filename, result_dict, mimetype,
                                evaluate_scraper):
    """
    Test FFMpegScraper with invalid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams = {}

    scraper = FFMpegScraper(filename=correct.filename,
                            mimetype=mimetype)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["mimetype", "version"],
    [
        ("video/avi", ""),
        ("video/mpeg", "1"),
        ("video/mp4", ""),
        ("video/MP2T", ""),
        ("application/mxf", "")
    ]
)
def test_is_supported(mimetype, version):
    """
    Test is_supported method.

    :mime: Predefined mimetype
    :ver: Predefined version
    """
    assert FFMpegScraper.is_supported(mimetype, version, True)
    assert FFMpegScraper.is_supported(mimetype, None, True)
    assert not FFMpegScraper.is_supported(mimetype, version, False)
    assert FFMpegScraper.is_supported(mimetype, "foo", True)
    assert not FFMpegScraper.is_supported("foo", version, True)

    assert not FFMpegMetaScraper.is_supported(mimetype, version, True)

    # Metadata gathering supported only for MXF
    if mimetype == "application/mxf":
        assert FFMpegMetaScraper.is_supported(mimetype, version, False)
    else:
        assert not FFMpegMetaScraper.is_supported(mimetype, version, False)
