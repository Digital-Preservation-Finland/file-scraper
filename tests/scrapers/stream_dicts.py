"""
Expected stream results for different AV files
"""
from __future__ import unicode_literals

from file_scraper.defaults import UNAP, UNAV

MOV_CONTAINER = {
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "MPEG-4", "index": 0, "mimetype": "video/quicktime",
    "stream_type": "videocontainer", "version": UNAP}

DV_VIDEO = {
    "bits_per_sample": "8", "codec_creator_app": UNAV,
    "codec_creator_app_version": UNAV, "codec_name": "DV",
    "codec_quality": "lossy", "color": "Color", "dar": "1.778",
    "data_rate": "24.4416", "data_rate_mode": "Fixed", "duration": "PT0.08S",
    "frame_rate": "25", "height": "576", "index": 0, "mimetype": "video/dv",
    "par": "1.422", "sampling": "4:2:0", "signal_format": "PAL",
    "sound": "No", "stream_type": "video", "version": UNAP,
    "width": "720"}

MOV_DV_VIDEO = dict(DV_VIDEO, **{
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101", "sound": "Yes"})

MKV_CONTAINER = {
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "Matroska", "index": 0,
    "mimetype": "video/x-matroska",
    "stream_type": "videocontainer", "version": "4"}

FFV_VIDEO = {
    "bits_per_sample": "8", "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "FFV1", "codec_quality": "lossless",
    "color": "Color", "dar": "1.778", "data_rate": "2.071061",
    "data_rate_mode": "Variable", "duration": "PT1S",
    "frame_rate": "30", "height": "180", "index": 1,
    "mimetype": "video/x-ffv", "par": "1", "sampling": "4:2:0",
    "signal_format": UNAP, "sound": "No", "stream_type": "video",
    "version": "3", "width": "320"}
FFV_VIDEO_TRUNCATED = dict(FFV_VIDEO, **{
    "data_rate": "2.077741", "version": "0"})
FFV_VIDEO_SOUND = dict(FFV_VIDEO, **{
    "data_rate": UNAV, "sound": "Yes"})
FFV_VIDEO_SOUND_DATARATE = dict(FFV_VIDEO_SOUND, **{
    "data_rate": "2.278507"})

WAV_AUDIO = {
    "audio_data_encoding": "PCM", "bits_per_sample": "8",
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "PCM", "codec_quality": "lossless",
    "data_rate": "705.6", "data_rate_mode": "Fixed", "duration": "PT0.86S",
    "index": 0, "mimetype": "audio/x-wav", "num_channels": "2",
    "sampling_frequency": "44.1", "stream_type": "audio"}
LPCM8_AUDIO = dict(WAV_AUDIO, **{
    "mimetype": "audio/L8", "version": UNAP})

FLAC_AUDIO = {
    "audio_data_encoding": "FLAC", "bits_per_sample": "24",
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "FLAC", "codec_quality": "lossless",
    "data_rate": UNAV, "data_rate_mode": "Variable",
    "duration": "PT0.86S", "index": 2, "mimetype": "audio/flac",
    "num_channels": "2", "sampling_frequency": "44.1",
    "stream_type": "audio", "version": "1.2.1"}

AIFF_AUDIO = {
    "audio_data_encoding": "PCM", "bits_per_sample": "16",
    "codec_creator_app": UNAV, "codec_creator_app_version": UNAV,
    "codec_name": "PCM", "codec_quality": "lossless",
    "data_rate": "1411.2", "data_rate_mode": "Fixed",
    "duration": "PT0.86S", "index": 0, "mimetype": "audio/aiff",
    "num_channels": "2", "sampling_frequency": "44.1",
    "stream_type": "audio", "version": "1.3"}

MPEG1_VIDEO = {
    "mimetype": "video/mpeg", "index": 0, "par": "1", "frame_rate": "30",
    "data_rate": "0.171304", "bits_per_sample": "8",
    "data_rate_mode": "Variable", "color": "Color",
    "codec_quality": "lossy", "signal_format": UNAP, "dar": "1.778",
    "height": "180", "sound": "No", "version": "1",
    "codec_name": "MPEG Video",
    "codec_creator_app_version": UNAV,
    "duration": "PT1S", "sampling": "4:2:0", "stream_type": "video",
    "width": "320", "codec_creator_app": UNAV}

MPEG2_VIDEO = dict(MPEG1_VIDEO, **{
    "data_rate": "0.185784", "version": "2"})

MPEG4_VIDEO = dict(MPEG1_VIDEO, **{
    "mimetype": "video/mp4", "index": 1, "data_rate": "0.048704",
    "sound": "Yes", "version": UNAP, "codec_name": "AVC",
    "codec_creator_app_version": "56.40.101",
    "codec_creator_app": "Lavf56.40.101"})

MOV_MPEG4_VIDEO = dict(MPEG4_VIDEO, **{
    "frame_rate": "25", "height": "576", "duration": "PT0.08S",
    "data_rate": "0.5793", "par": "1.422", "width": "720",
    "signal_format": "PAL", "data_rate_mode": "Variable"
    })
MPEGTS_VIDEO = dict(MPEG1_VIDEO, **{
    "data_rate": UNAV, "index": 1, "sound": "Yes", "version": "2"})

MPEG1_AUDIO = {
    "mimetype": "audio/mpeg", "index": 0,
    "audio_data_encoding": "MPEG Audio", "bits_per_sample": UNAV,
    "data_rate_mode": "Fixed", "codec_quality": "lossy", "version": "1",
    "stream_type": "audio", "sampling_frequency": "44.1",
    "num_channels": "2", "codec_name": "MPEG Audio",
    "codec_creator_app_version": UNAV, "duration": "PT0.89S",
    "data_rate": "128", "codec_creator_app": UNAV}

MPEG4_AUDIO = dict(MPEG1_AUDIO, **{
    "mimetype": "audio/mp4", "index": 2, "audio_data_encoding": "AAC",
    "data_rate_mode": "Fixed", "version": UNAP, "codec_name": "AAC",
    "codec_creator_app_version": "56.40.101",
    "duration": "PT0.86S", "data_rate": "135.233",
    "codec_creator_app": "Lavf56.40.101"})

MOV_MPEG4_AUDIO = dict(MPEG4_AUDIO, **{
    "duration": "PT0.91S", "data_rate": "128.298"
    })

MPEGTS_AUDIO = dict(MPEG1_AUDIO, **{
    "data_rate": "128", "data_rate_mode": "Fixed", "duration": "PT0.89S",
    "index": 2})

MPEG4_CONTAINER = {
    "mimetype": "video/mp4", "index": 0, "stream_type": "videocontainer",
    "version": UNAP, "codec_name": "MPEG-4",
    "codec_creator_app_version": "56.40.101",
    "codec_creator_app": "Lavf56.40.101"}

MPEGTS_CONTAINER = {
    "codec_creator_app": UNAV,
    "codec_creator_app_version": UNAV,
    "codec_name": "MPEG-TS", "index": 0, "mimetype": "video/MP2T",
    "stream_type": "videocontainer", "version": UNAP}

BASE_JPEG2000_VIDEO = {
    "index": 1, "mimetype": "video/jpeg2000", "version": UNAP,
    "par": "1",
    "data_rate_mode": "Variable",
    "dar": "1.778",
    "height": "180", "sound": "No", "codec_name": "JPEG 2000",
    "codec_creator_app_version": "56.40.101", "duration": "PT1.03S",
    "sampling": "4:2:0", "stream_type": "video", "width": "320",
    "codec_creator_app": "Lavf56.40.101", "color": "Color",
    "signal_format": UNAP,
    "codec_quality": "lossy",
    "bits_per_sample": "8",
}

MXF_CONTAINER = {
    "index": 0, "mimetype": "video/avi", "version": UNAP,
    "stream_type": "videocontainer",
    "codec_name": "MXF (Material eXchange Format)",
    "codec_creator_app_version": "56.40.101",
    "codec_creator_app": "FFmpeg OP1a Muxer",
    "duration": u"PT1.03S",
}

MXF_JPEG2000_VIDEO = dict(BASE_JPEG2000_VIDEO,
                          **{
                              "data_rate": "1.928916",
                              "bits_per_sample": "8",
                              "frame_rate": "29.97",
                              "codec_creator_app": "FFmpeg OP1a Muxer",
                              "dar": "0",
                              "par": "0",
                              })

MXF_TC = {"mimetype": "application/mxf", "index": 4, "version": UNAV,
          "stream_type": "other"}

AVI_CONTAINER = {
    "index": 0,
    "mimetype": "video/avi",
    "stream_type": "videocontainer",
    "version": "(:unap)",
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "AVI"
}

AVI_VIDEO = {
    "bits_per_sample": "8",
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "MPEG Video",
    "codec_quality": "lossy",
    "color": "Color",
    "dar": "1.778",
    "data_rate": "0.190368",
    "data_rate_mode": "Variable",
    "duration": "PT1S",
    "frame_rate": "60",
    "height": "180",
    "index": 1,
    "mimetype": "video/mpeg",
    "par": "1",
    "sampling": "4:2:0",
    "signal_format": "(:unap)",
    "sound": "Yes",
    "stream_type": "video",
    "version": "2",
    "width": "320"
}

AVI_AUDIO = {
    "audio_data_encoding": "MPEG Audio",
    "bits_per_sample": "(:unav)",
    "codec_creator_app": "Lavf56.40.101",
    "codec_creator_app_version": "56.40.101",
    "codec_name": "MPEG Audio",
    "codec_quality": "lossy",
    "data_rate": "128",
    "data_rate_mode": "Fixed",
    "duration": "PT1.07S",
    "index": 2,
    "mimetype": "audio/mpeg",
    "num_channels": "2",
    "sampling_frequency": "44.1",
    "stream_type": "audio",
    "version": "1"
}
