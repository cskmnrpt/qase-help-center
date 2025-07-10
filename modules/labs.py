import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
import base64
import mimetypes
import re
import struct
from google import genai
from google.genai import types
import whisper
from typing import Union, Dict
import warnings

import sys

# Suppress FutureWarning from torch.load
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")

if sys.platform.startswith('win'):
    import msvcrt

    def getch():
        return msvcrt.getch().decode()
else:
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# --------------------------
# Helper functions for Gemini TTS
# --------------------------
def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    return file_name

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> Dict[str, Union[int, None]]:
    """Parses bits per sample and rate from an audio MIME type string."""
    bits_per_sample = 16
    rate = 24000
    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}

# --------------------------
# Helper function to get audio duration using FFmpeg
# --------------------------
def get_audio_duration(file_path: str) -> float:
    """Get the duration of an audio file in seconds using FFmpeg."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", file_path],
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result.stderr)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = float(duration_match.group(3))
            return hours * 3600 + minutes * 60 + seconds
        else:
            print(f"Warning: Could not extract duration for {file_path}")
            return 0.0
    except Exception as e:
        print(f"Error getting duration for {file_path}: {str(e)}")
        return 0.0

# --------------------------
# Helper functions for transcript processing
# --------------------------
def group_segments_by_pause(segments, max_gap=0.5):
    if not segments:
        return []
    groups = []
    current_group = [segments[0]]
    for seg in segments[1:]:
        if seg["start"] - current_group[-1]["end"] < max_gap:
            current_group.append(seg)
        else:
            groups.append(current_group)
            current_group = [seg]
    if current_group:
        groups.append(current_group)
    return groups

def split_group_into_sentences(group, pause_threshold=2.0):
    sentences = []
    current_sentence = []
    for i, seg in enumerate(group):
        current_sentence.append(seg)
        seg_ends_sentence = False
        text = seg["text"].strip()
        if text and text[-1] in ".!?":
            seg_ends_sentence = True
        if i == len(group) - 1:
            seg_ends_sentence = True
        else:
            gap = group[i + 1]["start"] - seg["end"]
            if gap >= pause_threshold:
                seg_ends_sentence = True
        if seg_ends_sentence:
            sentence_text = " ".join(s["text"].strip() for s in current_sentence)
            sentence_start = current_sentence[0]["start"]
            sentence_end = current_sentence[-1]["end"]
            sentences.append(
                {"start": sentence_start, "end": sentence_end, "text": sentence_text}
            )
            current_sentence = []
    return sentences

# --------------------------
# File picker function (terminal-based)
# --------------------------
def file_picker(files):
    current_row = 0
    selected_files = set()
    display_height = 10
    start_idx = 0

    while True:
        os.system("clear" if os.name != "nt" else "cls")
        print("Select video files (arrows to navigate, space to select, Enter to confirm, q to quit):")
        end_idx = min(start_idx + display_height, len(files))
        for idx in range(start_idx, end_idx):
            file = files[idx]
            display_name = os.path.basename(file)
            marker = "[x]" if file in selected_files else "[ ]"
            prefix = "> " if idx == current_row else "  "
            print(f"{prefix}{marker} {display_name}")
        
        key = getch().lower()
        
        if key in ("k", "\x1b[A"):
            if current_row > 0:
                current_row -= 1
                if current_row < start_idx:
                    start_idx -= 1
            elif start_idx > 0:
                start_idx -= 1
                current_row = start_idx
        elif key in ("j", "\x1b[B"):
            if current_row < len(files) - 1:
                current_row += 1
                if current_row >= start_idx + display_height:
                    start_idx += 1
            elif current_row == len(files) - 1 and start_idx + display_height < len(files):
                start_idx += 1
                current_row = min(current_row, start_idx + display_height - 1)
        elif key == " ":
            current_file = files[current_row]
            if current_file in selected_files:
                selected_files.remove(current_file)
            else:
                selected_files.add(current_file)
        elif key in ("\r", "\n"):
            return sorted(list(selected_files), key=os.path.basename)
        elif key == "q" or key == "\x1b":
            return []

# --------------------------
# Main processing function
# --------------------------
def process_labs(args):
    folder_path = os.path.expanduser("~/screen-studio")
    mp4_files = sorted(
        glob.glob(os.path.join(folder_path, "*.mp4")),
        key=os.path.getmtime,
        reverse=True,
    )

    if not mp4_files:
        print("No video files found in the folder.")
        sys.exit(1)

    video_paths = []
    if args.i:
        video_paths = file_picker(mp4_files)
        if not video_paths:
            print("No files selected.")
            sys.exit(1)
        print(f"Selected videos: {', '.join(os.path.basename(p) for p in video_paths)}")
    else:
        video_name = input(
            "Enter the video name (or press Enter to use the latest video): "
        ).strip()
        if not video_name:
            video_paths = [mp4_files[0]]
            print(f"Selected latest video: {video_paths[0]}")
        else:
            video_path = os.path.join(folder_path, f"{video_name}.mp4")
            if not os.path.exists(video_path):
                print(f"Video file '{video_path}' does not exist.")
                sys.exit(1)
            video_paths = [video_path]

    temp_dir = tempfile.mkdtemp()
    
    for idx, video_path in enumerate(video_paths, 1):
        print(f"\nProcessing {idx} of {len(video_paths)}: {os.path.basename(video_path)}")
        
        model = whisper.load_model("small")
        result = model.transcribe(video_path, language="en", word_timestamps=False)
        segments = result["segments"]

        transcript_segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()}
            for seg in segments
        ]

        transcript_file = os.path.join(temp_dir, f"transcript_{idx}.json")
        with open(transcript_file, "w") as f:
            json.dump(transcript_segments, f, indent=4)

        editor = os.environ.get("EDITOR", "nvim")
        subprocess.run([editor, transcript_file])

        while True:
            with open(transcript_file, "r") as f:
                edited_segments = json.load(f)

            groups = group_segments_by_pause(edited_segments, max_gap=0.5)
            final_tts_segments = []
            last_end = 0.0
            for group in groups:
                sentences = split_group_into_sentences(group, pause_threshold=2.0)
                for sentence in sentences:
                    sentence_start = max(sentence["start"], last_end + 0.2)  # Add 0.2s buffer
                    sentence_end = sentence["end"] + (sentence_start - sentence["start"])  # Adjust end time
                    final_tts_segments.append({
                        "start": sentence_start,
                        "end": sentence_end,
                        "text": sentence["text"]
                    })
                    last_end = sentence_end
                    print(f"Expected segment: start={sentence_start:.2f}, end={sentence_end:.2f}, text='{sentence['text']}'")

            final_segments_file = os.path.join(temp_dir, f"final_tts_segments_{idx}.json")
            with open(final_segments_file, "w") as f:
                json.dump(final_tts_segments, f, indent=4)

            # Generate TTS audio using Gemini
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set!")

            client = genai.Client(api_key=api_key)
            model = "gemini-2.5-flash-preview-tts"
            style_prompt = (
                "Use natural language, adjust the pace based on the content. "
                "Don't read like you're reading to kids!"
            )
            generate_content_config = types.GenerateContentConfig(
                temperature=0.6,  # Increased to avoid potential garbled audio
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                ),
            )

            tts_audio_clips = []
            last_audio_end = 0.0
            total_tokens = 0
            for seg in final_tts_segments:
                styled_text = style_prompt + seg["text"]
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=styled_text)],
                    ),
                ]
                # Count tokens for this request
                try:
                    token_response = client.models.count_tokens(model=model, contents=contents)
                    tokens = token_response.total_tokens
                    total_tokens += tokens
                    print(f"Tokens for segment '{seg['text']}': {tokens}")
                except Exception as e:
                    print(f"Token counting failed for segment '{seg['text']}': {str(e)}")

                tts_clip_path = os.path.join(temp_dir, f"tts_{idx}_{seg['start']:.2f}.wav")
                file_index = 0
                try:
                    for chunk in client.models.generate_content_stream(
                        model=model,
                        contents=contents,
                        config=generate_content_config,
                    ):
                        if (
                            chunk.candidates is None
                            or chunk.candidates[0].content is None
                            or chunk.candidates[0].content.parts is None
                        ):
                            continue
                        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                            inline_data = chunk.candidates[0].content.parts[0].inline_data
                            data_buffer = inline_data.data
                            file_extension = mimetypes.guess_extension(inline_data.mime_type)
                            if file_extension is None:
                                file_extension = ".wav"
                                data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                            save_binary_file(tts_clip_path, data_buffer)
                            # Get actual audio duration
                            audio_duration = get_audio_duration(tts_clip_path)
                            print(f"Actual audio duration for {tts_clip_path}: {audio_duration:.2f}s, "
                                  f"expected duration: {(seg['end'] - seg['start']):.2f}s")
                            # Adjust segment start time based on actual audio duration
                            adjusted_start = max(seg["start"], last_audio_end)
                            tts_audio_clips.append((adjusted_start, tts_clip_path))
                            last_audio_end = adjusted_start + audio_duration + 0.2  # Add 0.2s buffer
                            file_index += 1
                            break
                        else:
                            print(f"Error in TTS generation for text: {seg['text']}")
                except Exception as e:
                    print(f"TTS generation failed for text '{seg['text']}': {str(e)}")
                    continue

            print(f"Total tokens used for video {idx}: {total_tokens}")
            if not tts_audio_clips:
                print("No TTS clips were generated.")
                sys.exit(1)

            ffmpeg_cmd = ["ffmpeg"]
            for _, clip_path in tts_audio_clips:
                ffmpeg_cmd.extend(["-i", clip_path])

            filter_complex_parts = []
            for i, (seg_start, _) in enumerate(tts_audio_clips):
                delay_ms = int(seg_start * 1000)
                filter_complex_parts.append(f"[{i}:a]adelay={delay_ms}:all=1[a{i}]")

            delayed_streams = "".join(f"[a{i}]" for i in range(len(tts_audio_clips)))
            filter_complex_parts.append(
                f"{delayed_streams}amix=inputs={len(tts_audio_clips)}:normalize=0[aout]"
            )
            filter_complex = ";".join(filter_complex_parts)

            final_audio_path = os.path.join(temp_dir, f"final_audio_{idx}.mp3")
            try:
                subprocess.run(ffmpeg_cmd + ["-filter_complex", filter_complex, "-map", "[aout]", "-y", final_audio_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg audio merging failed: {str(e)}")
                sys.exit(1)

            # Merge with original video
            final_video_path = os.path.join(temp_dir, f"labs_{idx}_" + os.path.basename(video_path))
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        video_path,
                        "-i",
                        final_audio_path,
                        "-c:v",
                        "copy",
                        "-map",
                        "0:v",
                        "-map",
                        "1:a",
                        final_video_path,
                        "-y",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg video merging failed: {str(e)}")
                sys.exit(1)

            # Play the video for review
            try:
                if sys.platform == "darwin":
                    if os.environ.get("LABS_PLAYER") == "mpv":
                        subprocess.run(["mpv", final_video_path], check=True)
                    else:
                        subprocess.run(["open", final_video_path], check=True)
                elif sys.platform == "linux" or sys.platform == "linux2":
                    subprocess.run(["xdg-open", final_video_path], check=True)
                elif sys.platform == "win32":
                    subprocess.run(["start", final_video_path], shell=True, check=True)
                else:
                    print("Unsupported platform for video playback.")
                    sys.exit(1)
            except subprocess.CalledProcessError:
                print("Failed to open video player. Please check your system configuration.")
                sys.exit(1)

            # Prompt user to approve or re-edit
            user_input = input(
                "Video playback complete. Press Enter to proceed with saving, or 'n' to edit the transcript again: "
            ).strip().lower()
            if user_input == "n":
                subprocess.run([editor, transcript_file])
                continue
            break

        # Save final file
        output_folder = os.path.expanduser("~/qh/pieces")
        os.makedirs(output_folder, exist_ok=True)
        default_name = os.path.basename(video_path)
        print(
            f"\nFinal video generated. Press Enter to save as '{default_name}' in {output_folder}, or type a new name (without extension):"
        )
        new_name = input().strip()
        if not new_name:
            new_name = default_name
        else:
            new_name = f"{new_name}.mp4"

        final_output_path = os.path.join(output_folder, new_name)
        shutil.move(final_video_path, final_output_path)
        print(f"Final video saved as: {final_output_path}")

    # Cleanup
    shutil.rmtree(temp_dir)

# --------------------------
# Entry point for standalone execution
# --------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", action="store_true", help="Show interactive file picker")
    args = parser.parse_args()
    process_labs(args)
