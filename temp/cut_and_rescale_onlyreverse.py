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


def cut_and_rescale_video(
    video_filepath,
    tmin,
    tmax,
    ffmpeg_settings,
    reverse=False,
    hflip=False,
    cut_output_filepath=None,
    rescaled_output_filepath=None,
):

    pts = ffmpeg_settings["video_duration"] / (tmax - tmin)
    # cutting first
    try:
        pipeline = (
            ffmpeg.input(video_filepath)
            .trim(start=tmin, end=tmax)
            .setpts(f"PTS-{tmin}/TB")
        )
        if reverse:
            pipeline = pipeline.filter("reverse")
        if hflip:
            pipeline = pipeline.hflip()
        pipeline = pipeline.output(filename=cut_output_filepath)
        pipeline.run(overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e
    # then rescaling
    try:
        pipeline = (
            ffmpeg.input(cut_output_filepath)
            .setpts(f"PTS*{pts}")
            .filter("fps", fps=ffmpeg_settings["framerate"], round="up")
            .filter(
                "scale",
                size=ffmpeg_settings["size"],
                force_original_aspect_ratio="increase",
            )
        )
        pipeline = pipeline.output(
            filename=rescaled_output_filepath,
            s=ffmpeg_settings["size"],
            codec=ffmpeg_settings["codec"],
            pix_fmt=ffmpeg_settings["pix_fmt"],
            preset=ffmpeg_settings["preset"],
            crf=ffmpeg_settings["crf"],
            format=ffmpeg_settings["format"],
            framerate=ffmpeg_settings["framerate"],
        )
        # pipeline.view(filename=output_filepath.replace('.mp4', '.png'))
        pipeline.run(overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e

if __name__ == "__main__":
    db_df = pd.read_csv('edited_video_db_final.tsv', sep='\t')

    for direction, dir_label in zip([True], ['rv']): 
        Parallel(n_jobs=settings['preferred_n_jobs_transcode'], backend="multiprocessing")(delayed(cut_and_rescale_video)(
                    video_filepath=Path(settings['raw_video_directory']) / row['file_name'],
                    tmin=row['tmin'],
                    tmax=row['tmax'],
                    ffmpeg_settings=settings['ffmpeg_settings'],
                    reverse=direction,
                    hflip=bool(row['horizontal_flip']),
                    cut_output_filepath=Path(settings['cut_stimulus_video_directory']) / f'{str(row["v_index"]).zfill(4)}_{dir_label}.mp4',
                    rescaled_output_filepath=Path(settings['rescaled_stimulus_video_directory']) / f'{str(row["v_index"]).zfill(4)}_{dir_label}.mp4')
                        for i, row in tqdm.tqdm(db_df.iterrows()))