import os
import aot
import yaml
from pathlib import Path
import ffmpeg
import random

explode_path = Path(
    "/tank/shared/2024/visual/AOT/derivatives/stimuli/rescaled_final_explodes"
)

source_path = Path("/tank/shared/2024/visual/AOT/derivatives/stimuli/rescaled_final")

def index_to_filename(index, direction="fw"):  # or rv
    # 4 pad the index with zeros
    index = str(index).zfill(4)
    name = f"{index}_{direction}.mp4"
    full_path = str(source_path / name)
    return full_path


def explode_videos(video_path, explode_path):
    video_name = os.path.basename(video_path)
    video_name = video_name.split(".")[0]
    explode_folder = os.path.join(explode_path, video_name)
    os.makedirs(explode_folder, exist_ok=True)
    # explode video into frames
    os.system(
        f"ffmpeg -i {video_path} -vf fps=25 {explode_folder}/frame_%04d.png"
    )

def explode_based_on_index(index):
    video_filepath_fw = index_to_filename(index, direction="fw")
    video_filepath_rv = index_to_filename(index, direction="rv")
    explode_videos(video_filepath_fw, explode_path)
    explode_videos(video_filepath_rv, explode_path)


if __name__ == "__main__":
    #randomly select 100 videos to explode
    index_list = random.sample(range(1, 2000), 100)
    for index in index_list:
        explode_based_on_index(index)
