from pathlib import Path
import ffmpeg
import yaml
import tqdm
import sys
import shutil
import pandas as pd
import numpy as np
import os

original_dir = Path('/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/originals')
cut_dir = Path('/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/clips')

video_list = ["7T_MOVIE1_CC1.mp4","7T_MOVIE3_CC2.mp4","7T_MOVIE2_HO1.mp4","7T_MOVIE4_HO2.mp4"]


blanks_durations_list = [
    [
        (0.04, 20.00),
        (264.12, 284.08),
        (505.79, 525.75),
        (713.83, 733.79),
        (797.62, 817.58)
    ],
    [
        (0.04, 20.00),
        (200.62, 220.58),
        (405.17, 425.12),
        (629.29, 649.25),
        (791.83, 811.79)
    ],
    [
        (0.04 , 20.00),
        (246.79 , 266.75),
        (525.42 , 545.38),
        (794.67 , 814.62)
    ],
    [
        (0.04 , 20.00),
        (252.38 , 272.33),
        (502.25 , 522.21),
        (777.46 , 797.42)
    ]
]

cllips_durarions_list = []
for durationlsit in blanks_durations_list:
    cllips_durarions_list.append([(durationlsit[i][1], durationlsit[i+1][0]) for i in range(len(durationlsit)-1)])
print(cllips_durarions_list)

video_total_durations = []
for video in video_list:
    video_path = original_dir / video
    probe = ffmpeg.probe(str(video_path))
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    video_duration = float(video_info["duration"])
    video_total_durations.append(video_duration)
print(video_total_durations)

endclips_durations_list = []
for i, video in enumerate(video_list):
    endclips_durations_list.append([(blanks_durations_list[i][-1][1], video_total_durations[i])])

def cut_clips(video_path, clip_durations, output_dir,suffix="clip"):
    os.system("module load shared")
    os.system("module load 2023")
    os.system("module load FFmpeg/6.0-GCCcore-12.3.0")
    for i, (start, end) in enumerate(clip_durations):
        output_path = output_dir / f"{video_path.stem}_{suffix}_{i}.mp4"
        #os.makedirs(output_path.parent, exist_ok=True)
        os.system(f"ffmpeg -i {video_path} -ss {start} -to {end} -c copy {output_path}")

def cut_all():
    for i, video in enumerate(video_list):
        video_path = original_dir / video
        clip_durations = cllips_durarions_list[i]
        cut_clips(video_path, clip_durations, cut_dir, suffix="clip")

    for i, video in enumerate(video_list):
        video_path = original_dir / video
        blank_durations = blanks_durations_list[i]
        cut_clips(video_path, blank_durations, cut_dir, suffix="blank")

    for i, video in enumerate(video_list):
        video_path = original_dir / video
        endclip_durations = endclips_durations_list[i]
        cut_clips(video_path, endclip_durations, cut_dir, suffix="endclip")

if __name__ == "__main__":
    cut_all()
