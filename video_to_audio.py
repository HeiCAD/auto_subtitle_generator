#!/usr/bin/env python3
"""
Video to Audio Extractor

A Python utility to extract audio tracks from multiple video files (MP4)
and save them as WAV files.

Usage Example
-------------
Run from the command line:

    python video_to_audio.py --input /path/to/videos --output /path/to/audios

Author: Ludmila Himmelspach
License: MIT
"""

import datetime
import subprocess
import argparse
from pathlib import Path
from auto_subtitle_generator.FindAllFiles import find_all_files


def extract_audio_from_video(video_file_path, audio_file_path):
    """
    Extract audio from a video file and save it as a WAV file.

    This function uses FFmpeg via a subprocess call to extract the audio track
    from a given video file and store it in WAV format. It supports stereo
    output with 32-bit PCM encoding.

       Parameters
       ----------
       video_file_path : Path or str
           Full path to the input video file (e.g., MP4).
       audio_file_path : Path or str
           Full path to the folder where the extracted audio file will be saved.

       Returns
       -------
       Prints success or failure messages. Does not return a value.

        Notes
        -----
         - Requires FFmpeg to be installed and accessible in the system PATH.
         - Overwrites existing audio files with the same name without warning.
       """
    ffmpeg_command = [
        "ffmpeg",
        "-i", str(video_file_path),
        "-acodec", "pcm_s32le",
        "-ac", "2",
        "-y",
        str(audio_file_path)
    ]

    try:
        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Successfully extracted audio from '{video_file_path.name}'")
    except subprocess.CalledProcessError:
        print(f"Failed to extract audio from '{video_file_path.name}'")


def main():
    parser = argparse.ArgumentParser(
        description="Extract WAV audio from MP4 video files using FFmpeg."
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to the input folder containing MP4 files."
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Path to the output folder where audio files will be saved."
    )

    args = parser.parse_args()
    video_path = args.input
    audio_path = args.output

    # Ensure output folder exists
    audio_path.mkdir(parents=True, exist_ok=True)

    # Find all .mp4 files
    video_file_list = find_all_files(video_path, ending=".mp4")
    if not video_file_list:
        print("No MP4 files found in the input folder.")
        return

    print("Extracting audio files ...")
    start_time = datetime.datetime.now()

    for video_file in video_file_list:
        video_file_path = video_path / video_file
        audio_file_name = video_file_path.stem + "_audio.wav"
        audio_file_path = audio_path / audio_file_name
        extract_audio_from_video(video_file_path, audio_file_path)

    end_time = datetime.datetime.now()
    print("Audio extraction finished.")
    print("Total extraction time:", end_time - start_time)


if __name__ == "__main__":
    main()
