import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import requests
import whisper


# --------------------------
# Helper functions for transcript processing
# --------------------------
def group_segments_by_pause(segments, max_gap=0.5):
    """
    Group consecutive transcript segments if the gap between them is less than max_gap seconds.
    A gap of >= max_gap is treated as a boundary.
    """
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
    """
    Process a group (a list of transcript segments) and combine them into full sentences.
    A sentence is ended when:
      - The current segment's text ends with punctuation (. ! ?), or
      - There is a gap of >= pause_threshold seconds to the next segment, or
      - It is the last segment in the group.

    Each sentence is assigned:
      - start: the start time of the first segment in the sentence,
      - end: the end time of the last segment in the sentence,
      - text: the concatenation (with spaces) of all segment texts.
    """
    sentences = []
    current_sentence = []
    for i, seg in enumerate(group):
        current_sentence.append(seg)
        # Determine if we should end the sentence here.
        seg_ends_sentence = False
        text = seg["text"].strip()
        if text and text[-1] in ".!?":
            seg_ends_sentence = True
        # If this is the last segment in the group, end the sentence.
        if i == len(group) - 1:
            seg_ends_sentence = True
        else:
            # Look at the gap to the next segment.
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
# Step 1: Choose video and extract audio
# --------------------------
folder_path = os.path.expanduser("~/obs-recordings")
video_name = input(
    "Enter the video name (or press Enter to use the latest video): "
).strip()

if not video_name:
    mp4_files = sorted(
        glob.glob(os.path.join(folder_path, "*.mp4")),
        key=os.path.getmtime,
        reverse=True,
    )
    if mp4_files:
        video_path = mp4_files[0]
        print(f"Selected latest video: {video_path}")
    else:
        print("No video files found in the folder.")
        sys.exit(1)
else:
    video_path = os.path.join(folder_path, f"{video_name}.mp4")
    if not os.path.exists(video_path):
        print(f"Video file '{video_path}' does not exist.")
        sys.exit(1)

# Extract audio from the video (using ffmpeg)
audio_path = video_path.replace(".mp4", ".mp3")
subprocess.run(
    ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"],
    check=True,
)

# --------------------------
# Step 2: Transcribe audio with Whisper
# --------------------------
model = whisper.load_model("small")
result = model.transcribe(audio_path, language="en", word_timestamps=False)
segments = result["segments"]

# Prepare transcript segments (each with start, end, and text)
transcript_segments = []
for segment in segments:
    transcript_segments.append(
        {
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip(),
        }
    )

# --------------------------
# Step 3: (Optional) Save and edit transcript manually
# --------------------------
temp_dir = tempfile.mkdtemp()
transcript_file = os.path.join(temp_dir, "transcript.json")
with open(transcript_file, "w") as f:
    json.dump(transcript_segments, f, indent=4)

# Open your editor to adjust the transcript if needed.
subprocess.run(["nvim", transcript_file])

with open(transcript_file, "r") as f:
    edited_segments = json.load(f)

# --------------------------
# Step 4: Process transcript into full-sentence clips
# --------------------------
# First, group segments using a 0.5‑second pause threshold.
groups = group_segments_by_pause(edited_segments, max_gap=0.5)

# Then, for each group, split it into sentences using punctuation and pauses (>=2 sec).
final_tts_segments = []
for group in groups:
    sentences = split_group_into_sentences(group, pause_threshold=2.0)
    final_tts_segments.extend(sentences)

# (Optional) Save the final TTS segments for inspection.
final_segments_file = os.path.join(temp_dir, "final_tts_segments.json")
with open(final_segments_file, "w") as f:
    json.dump(final_tts_segments, f, indent=4)

# --------------------------
# Step 5: Generate TTS audio for each final segment (one full sentence per clip)
# --------------------------

api_key = os.environ.get("ELEVEN_LABS_TOKEN")  # Read from environment variable

if not api_key:
    raise ValueError("API_KEY environment variable is not set!")

api_url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"  # UPDATE VOICE ID IF NEEDED

# For each final segment, call ElevenLabs TTS without time-stretching.
tts_audio_clips = []  # List of tuples: (segment_start, tts_clip_path)
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
    # Save the generated TTS audio.
    tts_clip_path = os.path.join(temp_dir, f"tts_{seg['start']:.2f}.mp3")
    with open(tts_clip_path, "wb") as f:
        f.write(response.content)
    # Record the segment start (from our computed timing) along with the clip path.
    tts_audio_clips.append((seg["start"], tts_clip_path))

# --------------------------
# Step 6: Build final audio track by placing each TTS clip at its segment start time
# --------------------------
if not tts_audio_clips:
    print("No TTS clips were generated.")
    sys.exit(1)

# Prepare an ffmpeg command that loads each TTS clip as an input.
ffmpeg_cmd = ["ffmpeg"]
for _, clip_path in tts_audio_clips:
    ffmpeg_cmd.extend(["-i", clip_path])

# For each clip, delay it by its start time (in milliseconds)
filter_complex_parts = []
for i, (seg_start, _) in enumerate(tts_audio_clips):
    delay_ms = int(seg_start * 1000)
    filter_complex_parts.append(f"[{i}:a]adelay={delay_ms}:all=1[a{i}]")

# Mix all delayed streams together (disable normalization for consistent volume)
delayed_streams = "".join(f"[a{i}]" for i in range(len(tts_audio_clips)))
filter_complex_parts.append(
    f"{delayed_streams}amix=inputs={len(tts_audio_clips)}:normalize=0[aout]"
)
filter_complex = ";".join(filter_complex_parts)

final_audio_path = os.path.join(temp_dir, "final_audio.mp3")
ffmpeg_cmd.extend(
    ["-filter_complex", filter_complex, "-map", "[aout]", "-y", final_audio_path]
)
subprocess.run(ffmpeg_cmd, check=True)

# --------------------------
# Step 7: Merge the new TTS audio track with the original video
# --------------------------
final_video_path = os.path.join(folder_path, "labs-" + os.path.basename(video_path))
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

print(f"Final video saved as: {final_video_path}")

# Cleanup temporary files
shutil.rmtree(temp_dir)
