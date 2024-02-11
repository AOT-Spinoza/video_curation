from pathlib import Path
import ffmpeg
import yaml
import tqdm
import sys
import shutil
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile

from simple_file_checksum import get_checksum
from joblib import Parallel, delayed

settings = yaml.load(open("settings.yaml"), Loader=yaml.FullLoader)

# working_dir = Path("/tank/shared/2022/arrow_of_time/derivatives/stimuli/rescaled_old")
working_dir = Path(settings["rescaled_stimulus_video_directory"])
test_output_dir = Path("/tank/zhangs/AOT_code_repos/video_curation/temp/test")

def index_to_filename(index,direction = "fw"): #or rv
    #4 pad the index with zeros
    index = str(index).zfill(4)
    name = f"{index}_{direction}.mp4"
    full_path = str(working_dir / name)
    return full_path

def reverse_video_based_on_index(index):
    video_filepath = index_to_filename(index, direction = "fw")
    reversed_video_filepath = index_to_filename(index, direction = "rv")
    try:
        pipeline = ffmpeg.input(video_filepath).filter("reverse").output(reversed_video_filepath)
        pipeline.run(overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e

def test():
    index_list = list(range(1, 150))
    for index in index_list:
        reverse_video_based_on_index(index)

test()
