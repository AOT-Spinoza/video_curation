from pathlib import Path
import ffmpeg
import yaml
import tqdm
import sys
import shutil
import pandas as pd
import numpy as np
import os

original_dir = Path(
    "/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/originals"
)
cut_dir = Path("/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/short_clips")

video_list = [
    "7T_MOVIE1_CC1.mp4",
    "7T_MOVIE3_CC2.mp4",
    "7T_MOVIE2_HO1.mp4",
    "7T_MOVIE4_HO2.mp4",
]

# create the cut_dir for each movie
for video in video_list:
    cut_dir_video = cut_dir / video
    cut_dir_video.mkdir(parents=True, exist_ok=True)


def cut_video_into_short_clips(video, output_dir, gap=1, duration=2.5):
    # cut video into short clips, the gap between the start of each clip is gap, the duration of each clip is duration, there is overlap between clips
    video_path = original_dir / video
    probe = ffmpeg.probe(str(video_path))
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    video_duration = float(video_info["duration"])
    print(video_duration)
    for i in range(int(video_duration // gap)):
        start = i * gap
        output_path = output_dir / f"{video}_{i}.mp4"
        ffmpeg.input(str(video_path), ss=start, t=duration).output(
            str(output_path), loglevel="quiet"
        ).run()


for video in video_list:
    cut_dir_video = cut_dir / video
    cut_video_into_short_clips(video, output_dir=cut_dir_video)
