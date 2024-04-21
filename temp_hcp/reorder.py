from pathlib import Path
import ffmpeg
import yaml
import tqdm
import sys
import shutil
import pandas as pd
import numpy as np
import os
import glob
import copy
import random

run_time_limit = 10*60 #10 minutes

original_dir = Path(
    "/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/originals"
)
cut_dir = Path("/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/clips")

final_videos_dir = Path("/tank/shared/2024/visual/AOT/derivatives/stimuli/HCPmovies/finals")

video_list = [
    "7T_MOVIE1_CC1.mp4",
    "7T_MOVIE3_CC2.mp4",
    "7T_MOVIE2_HO1.mp4",
    "7T_MOVIE4_HO2.mp4",
]

# get mp4 files from cut dir
block_files_list = glob.glob(str(cut_dir) + '/*.mp4')
print(block_files_list)
print(len(block_files_list))

block_names_list = []
for block_file in block_files_list:
    block_name = block_file.split('/')[-1]
    block_names_list.append(block_name)
print(block_names_list)

# make a block duration dict:
block_durarion_dict = {}
for block_file in block_files_list:
    probe = ffmpeg.probe(block_file)
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    video_duration = float(video_info["duration"])
    block_name = block_file.split('/')[-1]
    block_durarion_dict[block_name] = video_duration

print(block_durarion_dict)

clip_names = []
for block_name in block_names_list:
    if block_name == "blank.mp4":
        pass
    elif block_name == "endclip.mp4":
        pass
    else:
        clip_names.append(block_name)
print(clip_names)

def count_run_total_durarion(run):
    total_duration = 0
    for block in run:
        total_duration += block_durarion_dict[block]
    return total_duration


def clip_names_to_run_arrangement_and_duration(run_clip_names):
    clip_names_arrangement = ["blank.mp4"]
    for clip_name in run_clip_names:
        clip_names_arrangement.append(clip_name)
        clip_names_arrangement.append("blank.mp4")
    clip_names_arrangement.append("endclip.mp4")
    run_duraion = count_run_total_durarion(clip_names_arrangement)
    return clip_names_arrangement, run_duraion


def devide_clips_into_runs(total_clip_names):
    total_clip_names = copy.deepcopy(total_clip_names)
    random.shuffle(total_clip_names)
    runs = []
    while len(total_clip_names) > 0:
        run_clip_names = []
        run_arrangement = []
        while True:
            if len(total_clip_names) == 0:
                break
            run_clip_names.append(total_clip_names[0])
            new_run_arrangement,duration = clip_names_to_run_arrangement_and_duration(run_clip_names)
            if duration < run_time_limit:
                run_arrangement = new_run_arrangement
                total_clip_names.pop(0)
            else:
                break
        runs.append(run_arrangement)
    return runs

def get_best_runs():
    potential_runs = []
    for i in range(100000):
        runs = devide_clips_into_runs(clip_names)
        durations = [count_run_total_durarion(run) for run in runs]
        if len(runs) == 8:
            potential_runs.append((runs, durations))
            #print(len(runs))
            #print(durations)
            #calculate the std of the durations
            #print(np.std(durations))

    sorted_potential_runs = sorted(potential_runs, key=lambda x: np.std(x[1]))

    '''
    for i, (runs, durations) in enumerate(sorted_potential_runs):
        print(i)
        print(durations)
        print(np.std(durations))
        print(runs)
        print("")
    '''

    #print the best run and the duration and the std

    best_runs = sorted_potential_runs[0][0]  
    best_run_durations = sorted_potential_runs[0][1]
    print(best_runs)
    print(best_run_durations)
    print(np.std(best_run_durations))

    #save the best run to a file
    save_file = final_videos_dir / "best_run.txt"
    best_run_file = open(save_file, "w")
    best_run_file.write(str(best_runs))
    best_run_file.write("\n")
    best_run_file.write(str(best_run_durations))
    best_run_file.write("\n")
    best_run_file.write(str(np.std(best_run_durations)))
    best_run_file.close()

    return best_runs

best_runs = get_best_runs()

def run_clips_to_final_video(run_clips, run_index):
    run_file_name = "run_" + str(run_index).zfill(2)+".mp4"
    run_file_path = final_videos_dir / run_file_name
    #concatenate the clips
    input_files = []
    for clip in run_clips:
        clip_file = cut_dir / clip
        input_files.append(clip_file)
    
    #use ffmpeg to concatenate the clips files into a single video file
    input_files_str = ""
    for input_file in input_files:
        input_files_str += " -i " + str(input_file)
    
    command = "ffmpeg" + input_files_str + " -filter_complex '"
    for i in range(len(input_files)):
        command += "["+str(i)+":v:0]"
    command += "concat=n=" + str(len(input_files)) + ":v=1:a=0[outv]' -map '[outv]' " + str(run_file_path)
    print(command)
    os.system(command)


for i, run_clips in enumerate(best_runs):
    run_clips_to_final_video(run_clips, i+1)    


    

