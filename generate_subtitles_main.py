"""
main_generate_subtitles.py
==========================
Generate Subtitles from Audio using Whisper

A command-line tool to generate .srt subtitle files from one or more .wav audio files
using OpenAI Whisper (via faster-whisper).

Usage Example
-------------
# Generate subtitles for a single file
python generate_subtitles.py --audio /path/to/audio.wav --output /path/to/subtitles

# Generate subtitles for all .wav files in a folder
python generate_subtitles.py --audio /path/to/audio/folder --output /path/to/subtitles

Arguments
---------
--audio        Path to a single audio file (.wav) or a folder with multiple audio files.
--output       Output directory for the generated .srt files. (Default: "subtitles")
--model_size   Whisper model size (tiny, base, small, medium, large). (Default: large)
--device       Device to use ("cpu" or "cuda"). (Default: cpu)
--compute_type Precision for computations ("int8", "float16", "float32"). (Default: int8)
--max_lines    Maximum lines per subtitle (Default: 2)
--max_chars_line Maximum characters per subtitle line (Default: 40)
--min_std_time Minimum subtitle duration in seconds (Default: 2)
--max_std_time Maximum subtitle duration in seconds (Default: 5)

References
----------
- OpenAI Whisper:
  https://github.com/openai/whisper
  Original speech recognition model by OpenAI.

- Faster-Whisper:
  https://github.com/SYSTRAN/faster-whisper
  A highly optimized CTranslate2-based reimplementation of OpenAI Whisper,
  providing faster inference and reduced memory usage.

Notes
-----
- Requires FFmpeg and Whisper to be installed and accessible.
- Overwrites existing subtitle files without warning.

Author: Ludmila Himmelspach
License: MIT
"""

import argparse
from pathlib import Path
from datetime import datetime

from auto_subtitle_generator.GenerateSubtitles import generate_subtitles_from_file


def main():
    """Parse command-line arguments and generate subtitles accordingly."""

    # --- Argument Parser ---
    parser = argparse.ArgumentParser(
        description="Generate subtitles (.srt) from audio files using Whisper."
    )

    parser.add_argument("--audio", type=str, required=True,
                        help="Path to an audio file (.wav) or a folder containing multiple audio files.")
    parser.add_argument("--output", type=str, default="subtitles",
                        help="Output folder where subtitles (.srt) will be saved.")
    parser.add_argument("--model_size", type=str, default="large",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size to use (default: 'large').")
    parser.add_argument("--device", type=str, default="cpu",
                        choices=["cpu", "cuda"],
                        help="Hardware used for model execution (default: 'cpu' or 'cuda' for GPU).")
    parser.add_argument("--compute_type", type=str, default="int8",
                        choices=["int8", "float16", "float32"],
                        help="Precision of numerical calculations (e.g. 'float16', 'float32', 'int8' (default))")
    parser.add_argument("--max_lines", type=int, default=2,
                        help="Max number of lines per subtitle (default: 2).")
    parser.add_argument("--max_chars_line", type=int, default=40,
                        help="Max characters per subtitle line (default: 40).")
    parser.add_argument("--min_std_time", type=int, default=2,
                        help="Minimum subtitle duration in seconds (default: 2).")
    parser.add_argument("--max_std_time", type=int, default=5,
                        help="Maximum subtitle duration in seconds (default: 5).")

    args = parser.parse_args()

    # --- Setup ---
    audio_path = Path(args.audio)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Subtitle Generation with Whisper")
    print("=" * 60)
    print(f" Input path:   {audio_path}")
    print(f" Output path:  {output_path}")
    print(f" Model:        {args.model_size}")
    print(f"️ Device:     {args.device}")
    print(f"️ Precision:     {args.compute_type}")
    print("-" * 60)

    start_time = datetime.now()

    # --- Single File ---
    if audio_path.is_file():
        print(f"Processing single file: {audio_path.name}")
        # srt_name = audio_path.stem.replace("_audio", "") + ".srt"
        srt_name = audio_path.stem + ".srt"
        srt_file_path = output_path / srt_name

        generate_subtitles_from_file(
            audio_file_path=audio_path,
            srt_file_path=srt_file_path,
            model_size=args.model_size,
            device=args.device,
            compute_type=args.compute_type,
            max_lines=args.max_lines,
            max_chars_line=args.max_chars_line,
            min_std_time=args.min_std_time,
            max_std_time=args.max_std_time
        )
        print(f"   → Saved to {srt_file_path}")

    # --- Folder with multiple files ---
    elif audio_path.is_dir():
        audio_files = [f for f in audio_path.iterdir() if f.suffix.lower() == ".wav"]

        if not audio_files:
            print("No .wav files found in this folder.")
            return

        print(f" Found {len(audio_files)} file(s):")
        for f in audio_files:
            print(f"   - {f.name}")

        for i, audio_file in enumerate(audio_files, start=1):
            print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
            # srt_name = audio_file.stem.replace("_audio", "") + ".srt"
            srt_name = audio_file.stem + ".srt"
            srt_file_path = output_path / srt_name

            generate_subtitles_from_file(
                audio_file_path=audio_file,
                srt_file_path=srt_file_path,
                model_size=args.model_size,
                device=args.device,
                compute_type=args.compute_type,
                max_lines=args.max_lines,
                max_chars_line=args.max_chars_line,
                min_std_time=args.min_std_time,
                max_std_time=args.max_std_time
            )
            print(f"   → Saved to {srt_file_path}")

    else:
        print("Invalid input path. Please provide a valid file or folder.")
        return

    duration = datetime.now() - start_time
    print("=" * 60)
    print(f"Subtitle generation completed in {duration}.")
    print(f"Subtitles saved in: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
