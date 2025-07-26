import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
# from getch import getch

import requests
import whisper

import sys

# Import debug mode from main
try:
    from main import DEBUG_MODE
except ImportError:
    DEBUG_MODE = False

def debug_print(message):
    """Print message only in debug mode."""
    if DEBUG_MODE:
        print(message)

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
    while True:
        os.system("clear" if os.name != "nt" else "cls")
        print("Select video files (arrows to navigate, space to select, Enter to confirm, q to quit):")
        for idx, file in enumerate(files):
            display_name = os.path.basename(file)
            marker = "[x]" if file in selected_files else "[ ]"
            prefix = "> " if idx == current_row else "  "
            print(f"{prefix}{marker} {display_name}")
        
        # Get single key press
        key = getch().lower()
        
        if key in ("k", "\x1b[A"):  # Up arrow or 'k'
            current_row = max(0, current_row - 1)
        elif key in ("j", "\x1b[B"):  # Down arrow or 'j'
            current_row = min(len(files) - 1, current_row + 1)
        elif key == " ":  # Space to toggle selection
            current_file = files[current_row]
            if current_file in selected_files:
                selected_files.remove(current_file)
            else:
                selected_files.add(current_file)
        elif key in ("\r", "\n"):  # Enter to confirm
            return sorted(list(selected_files), key=os.path.basename)  # Sort by filename
        elif key == "q" or key == "\x1b":  # 'q' or Escape to cancel
            return []


# --------------------------
# Main processing function
# --------------------------
def process_labs(args):
    # Set folder_path to ~/screen-studio
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

    # Create single temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Process each video
    for idx, video_path in enumerate(video_paths, 1):
        print(f"\nProcessing {idx} of {len(video_paths)}: {os.path.basename(video_path)}")
        
        # Transcribe audio directly from video
        model = whisper.load_model("small")
        result = model.transcribe(video_path, language="en", word_timestamps=False)
        segments = result["segments"]

        transcript_segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()}
            for seg in segments
        ]

        # Save and edit transcript
        transcript_file = os.path.join(temp_dir, f"transcript_{idx}.json")
        with open(transcript_file, "w") as f:
            json.dump(transcript_segments, f, indent=4)

        editor = os.environ.get("EDITOR", "nvim")
        subprocess.run([editor, transcript_file])

        while True:
            with open(transcript_file, "r") as f:
                edited_segments = json.load(f)

            # Process transcript
            groups = group_segments_by_pause(edited_segments, max_gap=0.5)
            final_tts_segments = []
            for group in groups:
                sentences = split_group_into_sentences(group, pause_threshold=2.0)
                final_tts_segments.extend(sentences)

            final_segments_file = os.path.join(temp_dir, f"final_tts_segments_{idx}.json")
            with open(final_segments_file, "w") as f:
                json.dump(final_tts_segments, f, indent=4)

            # Generate TTS audio
            api_key = os.environ.get("ELEVEN_LABS_TOKEN")
            if not api_key:
                raise ValueError("ELEVEN_LABS_TOKEN environment variable is not set!")

            api_url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"
            tts_audio_clips = []
            for seg in final_tts_segments:
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json", "xi-api-key": api_key},
                    data=json.dumps(
                        {
                            "voice_settings": {
                                "stability": 0.4,
                                "similarity_boost": 1,
                                "use_speaker_boost": False,
                            },
                            "text": seg["text"],
                            "model_id": "eleven_multilingual_v2",
                        }
                    ),
                )
                if response.status_code != 200:
                    print(
                        f"Error in TTS API call for text: {seg['text']}\nResponse: {response.text}"
                    )
                    sys.exit(1)
                tts_clip_path = os.path.join(temp_dir, f"tts_{idx}_{seg['start']:.2f}.mp3")
                with open(tts_clip_path, "wb") as f:
                    f.write(response.content)
                tts_audio_clips.append((seg["start"], tts_clip_path))

            # Build final audio track
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
            ffmpeg_cmd.extend(
                ["-filter_complex", filter_complex, "-map", "[aout]", "-y", final_audio_path]
            )
            # Suppress FFmpeg output unless in debug mode
            if DEBUG_MODE:
                subprocess.run(ffmpeg_cmd, check=True)
            else:
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Merge with original video
            final_video_path = os.path.join(temp_dir, f"labs_{idx}_" + os.path.basename(video_path))
            ffmpeg_merge_cmd = [
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
            ]
            # Suppress FFmpeg output unless in debug mode
            if DEBUG_MODE:
                subprocess.run(ffmpeg_merge_cmd, check=True)
            else:
                subprocess.run(ffmpeg_merge_cmd, check=True, capture_output=True)

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
                # Re-open transcript for editing
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
