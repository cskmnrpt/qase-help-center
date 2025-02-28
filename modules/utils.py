import os
import subprocess
import time


def get_asset_pieces(asset_id):
    return sorted(
        [
            f"assets/{f}"
            for f in os.listdir("assets")
            if f.startswith(f"{asset_id}_") and f.endswith(".mp4")
        ]
    )


def rename_existing_file(file_path):
    if os.path.exists(file_path):
        timestamp = int(time.time())
        new_name = f"{file_path.split('.')[0]}-{timestamp}.{file_path.split('.')[1]}"
        os.rename(file_path, new_name)


def get_video_duration(video_file):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


def get_audio_duration(audio_file):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            audio_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)
