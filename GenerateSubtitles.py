"""
GenerateSubtitles
=================

A module for generating subtitle files (.srt) from audio files using the
Whisper speech recognition model.

This module provides functions for:
- Converting timestamps into subtitle-compatible format
- Transcribing audio files using Whisper
- Detecting sentence boundaries and splitting long subtitles
- Writing formatted subtitles into .srt files

Author: Ludmila Himmelspach
License: MIT
"""

import datetime
import ntpath
import re
from time import strftime, gmtime
from pathlib import Path
from faster_whisper import WhisperModel
from FindAllFiles import find_all_files  # optional if reused internally


# ---------------------------------------------------------------------
# Timestamp conversion
# ---------------------------------------------------------------------
def time_converter(timecode_in_seconds):
    """Convert decimal seconds into HH:MM:SS,mmm format."""
    time_in_seconds = timecode_in_seconds + 3600
    integer_seconds, decimal_seconds = format(time_in_seconds, '.3f').split(".")
    conv_time_code = (strftime("%H:%M:%S", gmtime(int(integer_seconds)))
                      + "," + decimal_seconds)
    return conv_time_code


# ---------------------------------------------------------------------
# Audio transcription
# ---------------------------------------------------------------------
def generate_subtitles(audio_file_path, model_size, device="cpu",
                       compute_type="int8"):
    """Transcribe an audio file into text segments using the Whisper model."""
    # model = WhisperModel(model_size,
    #                      device=device,
    #                      compute_type=compute_type,
    #                      device_index=0)
    if device.lower() == "cuda":
        model = WhisperModel(model_size, device=device, compute_type=compute_type, device_index=0)
    else:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments, info = model.transcribe(audio_file_path,
                                      beam_size=5,
                                      word_timestamps=True,
                                      vad_filter=True,
                                      multilingual=True)
    return segments, info


# ---------------------------------------------------------------------
# Word and sentence processing
# ---------------------------------------------------------------------
def extract_wordlist(segments):
    """Extract all words from the Whisper output segments."""
    word_list = []
    for segment in segments:
        for word in segment.words:
            word_list.append(word)
    return word_list


def sentence_end(word):
    """Determine if a given word marks the end of a sentence."""
    # Ignore abbreviations
    abbreviations = {' z.B.', ' u.a.', ' d.h.', ' bzw.', ' etc.', ' usw.', ' z. B.', ' u. a.', ' d. h.'}
    if word in abbreviations:
        return False
    # Delete quotations or brackets at the end
    cleaned = word.rstrip('”"\'»›)]')
    # Check if the word ends with a punctuation mark
    return bool(re.search(r'[.!?]+$', cleaned))


def generate_list_of_segments_from_words(word_list):
    """Group a list of words into sentence-like segments."""
    segments = []
    current_segment = []
    for i in range(len(word_list)):
        current_segment.append(word_list[i])
        if sentence_end(word_list[i].word):
            segments.append(current_segment)
            current_segment = []
    # If the last word does not contain a punctuation mark
    if current_segment:
        segments.append(current_segment)
    return segments


# ---------------------------------------------------------------------
# Segment manipulation
# ---------------------------------------------------------------------
def number_of_chars(segment):
    """Count total number of characters in a segment."""
    return sum(len(w.word) for w in segment)


def separable_segment(segment, max_std_time, max_lines, max_chars_line):
    """Determine whether a segment is too long and should be split."""
    segment_chars = number_of_chars(segment)
    standing_time = segment[-1].end - segment[0].start
    return (
        standing_time > max_std_time
        and segment_chars > max_chars_line * max_lines
        and len(segment) > 1
    )


def separate_segment(segment, min_std_time, max_std_time, max_lines, max_chars_line):
    """Split a long segment into two shorter ones based on punctuation or duration."""
    first_segment = []
    second_segment = segment.copy()
    punctuation = ".。,，!！?？:：”)]};"
    stop_words = [" oder", " und", " sowie", " als auch", " sondern", " aber", " denn", " doch", " bzw."]

    for i in range(len(segment)):
        first_segment.append(segment[i])
        del second_segment[0]
        if (any(elem in segment[i].word for elem in punctuation)
            and first_segment[-1].end - first_segment[0].start >= min_std_time):
            return first_segment, second_segment
        if (i + 1 < len(segment) and segment[i + 1].word in stop_words
            and first_segment[-1].end - first_segment[0].start >= min_std_time):
            return first_segment, second_segment
        if (number_of_chars(first_segment) >= max_lines * max_chars_line
            and first_segment[-1].end - first_segment[0].start >= min_std_time):
            return first_segment, second_segment
        if (first_segment[-1].end - first_segment[0].start >= max_std_time):
            return first_segment, second_segment
        # If the standing time of the second segment is too short
        if (len(second_segment) > 1 and second_segment[-1].end - second_segment[0].start <= min_std_time):
            return first_segment, second_segment
        if len(second_segment) == 1:
            return first_segment, second_segment


def generate_subtitle_segments(segments, min_std_time, max_std_time, max_lines, max_chars_line):
    """Generate final subtitle segments, splitting long sentences if needed."""
    new_segments = []
    for segment in segments:
        while separable_segment(segment, max_std_time, max_lines, max_chars_line):
            first_segment, second_segment = separate_segment(segment, min_std_time, max_std_time, max_lines, max_chars_line)
            new_segments.append(first_segment)
            segment = second_segment
        new_segments.append(segment)
    return new_segments


def insert_frame(segments, frame_time=0.042):
    """Insert one frame at the beginning of segments to prevent overlap."""
    for i in range(len(segments) - 1):
        if segments[i][-1].end == segments[i + 1][0].start:
            segments[i + 1][0].start = segments[i + 1][0].start + frame_time
    return segments


# ---------------------------------------------------------------------
# Subtitle file generation
# ---------------------------------------------------------------------
def split_subtitle_text(text, max_chars_line):
    """
    Splits a long subtitle text into at most two lines.
    The split occurs roughly in the middle of the text,
    trying not to break words or separate punctuation awkwardly.
    """
    punctuation = ".。,，!！?？:：”)]};"
    # Only split if the text exceeds the maximum allowed characters
    if len(text) > max_chars_line:

        # Step 1: Roughly divide the text in half
        first_part, second_part = text[:len(text)//2], text[len(text)//2:]

        # Step 2: Find the first space in the second half
        # This helps to locate where the next word begins
        second_part_splitted = second_part.partition(' ')
        second_part_before_space = second_part_splitted[0]
        second_part_after_space = second_part_splitted[2]

        # Step 3: Find the last space in the first half
        # This identifies where the previous word ends
        first_part_splitted = first_part.rpartition(' ')
        first_part_before_space = first_part_splitted[0]
        first_part_after_space = first_part_splitted[2]

        # Step 4: Combine the word fragments that were split in half
        middle_word = first_part_after_space + second_part_before_space

        # Step 5: Decide how to balance the two lines
        # If the first line is much shorter, or the split word contains punctuation,
        # keep the combined middle word on the first line.
        if len(first_part_before_space) < len(second_part_after_space) or any(
            elem in middle_word for elem in punctuation
        ):
            first_line = first_part_before_space + ' ' + middle_word
            second_line = second_part_after_space
        else:
            # Otherwise, move the middle word to the second line
            first_line = first_part_before_space
            second_line = middle_word + ' ' + second_part_after_space

        # Step 6: Join both lines with a newline
        text = first_line + "\n" + second_line

    return text


def join_text(segment, max_chars_line):
    """Join words into subtitle lines with automatic line breaks."""
    text = "".join([w.word for w in segment])

    text = ""
    for word in segment:
        # replace the ending "Innen" by "*innen"
        word_string = word.word
        if word_string.endswith("Innen"):
            word_string = word_string[:-5] + "*innen"
        # attach the word to the line
        text = text + word_string

    return split_subtitle_text(text, max_chars_line)


def write_subtitles(srt_file_path, segments, max_chars_line):
    """Write subtitle segments into a .srt file."""
    with open(srt_file_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            srt_file.write(str(i) + "\n")
            srt_file.write("%s --> %s\n%s" % (
                time_converter(segment[0].start),
                time_converter(segment[-1].end),
                join_text(segment, max_chars_line)
            ))
            if i != len(segments):
                srt_file.write("\n\n")


# ---------------------------------------------------------------------
# Main wrapper function
# ---------------------------------------------------------------------
def generate_subtitles_from_file(audio_file_path, srt_file_path,
                                 model_size="large", device="cpu",
                                 compute_type="int8",
                                 max_lines=2,
                                 max_chars_line=40,
                                 min_std_time=2,
                                 max_std_time=5):
    """
    Transcribe an audio file and generate a subtitle file (.srt).

    Parameters
    ----------
    audio_file_path : str or Path
        Path to the input audio file (.wav).
    srt_file_path : str or Path
        Path to the output subtitle file (.srt).
    model_size : str, optional
        Whisper model size (default: 'large').
    device : str, optional
        Hardware used for model execution ("cpu" or "cuda" for GPU)
    compute_type : str, optional
        Precision of numerical calculations (e.g. "float32", "float16", "int8")
    max_lines : int, optional
        Maximum number of lines per subtitle (default: 2).
    max_chars_line : int, optional
        Maximum number of characters per line (default: 40).
    min_std_time : float, optional
        Minimum subtitle duration in seconds (default: 2).
    max_std_time : float, optional
        Maximum subtitle duration in seconds (default: 5).
    """
    print(f"Extracting subtitles for '{ntpath.basename(audio_file_path)}' ...")
    start_time = datetime.datetime.now()

    segments, _ = generate_subtitles(audio_file_path, model_size, device, compute_type)
    segments = list(segments)
    word_list = extract_wordlist(segments)
    sentences_list = generate_list_of_segments_from_words(word_list)
    segments_list = generate_subtitle_segments(sentences_list, min_std_time, max_std_time, max_lines, max_chars_line)
    segments_list = insert_frame(segments_list, frame_time=0.042)
    write_subtitles(srt_file_path, segments_list, max_chars_line)

    end_time = datetime.datetime.now()
    print(f"Finished generating subtitles in {end_time - start_time}.\n")
