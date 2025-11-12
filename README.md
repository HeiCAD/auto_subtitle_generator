# Auto Subtitle Generator

A Python-based toolchain for automatically generating subtitle files (`.srt`) from video files.
The project extracts audio tracks from video files, transcribes speech using **OpenAI Whisper** (via [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)), and automatically formats subtitles with configurable limits for **maximum line length** and **subtitle duration**.

---

## Project Structure
```plaintext
auto_subtitle_generator/
├── FindAllFiles.py # Utility to list all files with a given extension
├── video_to_audio.py # Extracts audio (.wav) from video (.mp4) using FFmpeg
├── GenerateSubtitles.py # Transcribes audio into subtitles using Whisper
└── generate_subtitles_main.py # Command-line interface for batch subtitle generation
```
---

## Features

- **Video-to-audio extraction** using FFmpeg
- **Speech recognition** with Faster-Whisper (OpenAI Whisper backend)
- **Automatic subtitle segmentation** with sentence detection and line splitting
- **Smart subtitle formatting** — automatically limits characters per line and lines per segment for better readability
- **Timestamp formatting** for `.srt` files
- **CLI support** for single or batch processing
- **Lightweight modular design** (each step reusable as a standalone script)

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/auto-subtitle-generator.git
cd auto-subtitle-generator
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
#### Required Packages

To run this project, make sure the following dependencies are installed:

#### Python Packages
- [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper)

You can install it with:
```bash
pip install faster-whisper
```

#### System Requirements
- **FFmpeg** — must be installed and accessible in your system PATH.

Install FFmpeg using one of the following methods:

#### macOS:
```bash
brew install ffmpeg
```
#### Ubuntu/Debian:
```bash
sudo apt install ffmpeg
```
#### Windows:
Download and install from the official website: https://ffmpeg.org/download.html

#### Standard Python Modules

The following modules are included with Python and require no additional installation:

argparse, pathlib, datetime, subprocess, os, re, time

## Usage

### 1. Extract Audio from Video

Convert all .mp4 videos in a folder to .wav audio files:
```bash
python video_to_audio.py --input ./videos --output ./audios
```
### 2. Generate Subtitles from Audio

Generate .srt subtitle files from .wav audio files:
```bash
python generate_subtitles_main.py --audio ./audios --output ./subtitles
```
#### Example with GPU (CUDA)
```bash
python generate_subtitles_main.py --audio ./audios --output ./subtitles \
    --model_size large --device cuda --compute_type float16
```
## Command-Line Options

| Argument           | Description                                                     | Default      |
| ------------------ | --------------------------------------------------------------- | ------------ |
| `--audio`          | Path to a `.wav` file or folder                                 | **Required** |
| `--output`         | Output folder for subtitles                                     | `subtitles`  |
| `--model_size`     | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) | `large`      |
| `--device`         | Hardware for inference (`cpu` or `cuda`)                        | `cpu`        |
| `--compute_type`   | Precision (`int8`, `float16`, `float32`)                        | `int8`       |
| `--max_lines`      | Max lines per subtitle                                          | `2`          |
| `--max_chars_line` | Max characters per line                                         | `40`         |
| `--min_std_time`   | Min subtitle duration (seconds)                                 | `2`          |
| `--max_std_time`   | Max subtitle duration (seconds)                                 | `5`          |


## Example Workflow

# 1. Convert all MP4s to WAVs
```bash
python video_to_audio.py --input ./videos --output ./audios
```
# 2. Generate subtitles for all WAVs
```bash
python generate_subtitles_main.py --audio ./audios --output ./subtitles --max_chars_line 40
```
The generated .srt files will be stored in the output directory with the same filenames as the original audio files.

### Output Example
```plaintext
1
00:00:01,200 --> 00:00:03,500
 Hello everyone, welcome back!

2
00:00:03,800 --> 00:00:05,900
 Today we’re going to test
the subtitle generator.
```

## Dependencies Overview

| Module                       | Purpose                                             |
|------------------------------| --------------------------------------------------- |
| `FindAllFiles.py`            | Utility function to list files by extension         |
| `video_to_audio.py`          | Extracts `.wav` from `.mp4` via FFmpeg              |
| `GenerateSubtitles.py`       | Handles Whisper transcription and `.srt` formatting |
| `generate_subtitles_main.py` | CLI for batch subtitle generation                   |


## Technology

- **OpenAI Whisper** – robust multilingual speech recognition
- **Faster-Whisper** – optimized inference for Whisper
- **FFmpeg** – audio/video processing
- **Python 3.9+**

## License

This project is licensed under the MIT License.

## Author

Developed by Ludmila Himmelspach.

## Acknowledgments

- **OpenAI Whisper**
- **Faster-Whisper by SYSTRAN**
- **FFmpeg**



