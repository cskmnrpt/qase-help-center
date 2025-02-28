import os
import subprocess

from modules.utils import get_audio_duration, get_video_duration, rename_existing_file


def add_background_music(article_id, bg_id=None):
    video_file = f"articles/{article_id}.mp4"
    bg_files = [f for f in os.listdir("bg") if f.endswith(".mp3")]

    if not os.path.exists(video_file):
        print(
            f"Video file {video_file} not found. Please add the missing file and press Enter to continue."
        )
        input()
        if not os.path.exists(video_file):
            return

    video_duration = get_video_duration(video_file)

    if bg_id:
        bg_file = f"bg/{bg_id}.mp3"
        if not os.path.exists(bg_file):
            print(
                f"Background music file {bg_file} not found. Please add the missing file and press Enter to continue."
            )
            input()
            if not os.path.exists(bg_file):
                return

        bg_duration = get_audio_duration(bg_file)
        if bg_duration < video_duration:
            print(
                f"Background music {bg_file} is shorter than the video. Please provide another ID."
            )
            return
    else:
        # Find the nearest next track
        bg_file = None
        min_diff = float("inf")
        for file in bg_files:
            duration = get_audio_duration(f"bg/{file}")
            if duration >= video_duration and (duration - video_duration) < min_diff:
                min_diff = duration - video_duration
                bg_file = f"bg/{file}"

        if not bg_file:
            print(
                "No suitable background music found. Please add longer tracks and try again."
            )
            return

    output_file = f"articles/{article_id}_with_bg.mp4"
    rename_existing_file(output_file)

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_file,
            "-i",
            bg_file,
            "-filter_complex",
            "[0:a]volume=1[a0];[1:a]afade=t=in:st=0:d=2,afade=t=out:st={video_duration-2}:d=2[a1];[a0][a1]amix=inputs=2[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            output_file,
        ]
    )
