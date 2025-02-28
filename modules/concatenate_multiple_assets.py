import os
import subprocess

from modules.utils import rename_existing_file


def concatenate_multiple_assets(asset_ids, article_id):
    asset_files = [f"assets/{asset_id}.mp4" for asset_id in asset_ids.split(",")]
    article_image = f"articles/{article_id}.png"
    support_video = "others/support.mp4"

    if (
        not all(os.path.exists(asset) for asset in asset_files)
        or not os.path.exists(article_image)
        or not os.path.exists(support_video)
    ):
        print(
            "Missing assets, article image, or support video. Please add the missing files and press Enter to continue."
        )
        input()
        if (
            not all(os.path.exists(asset) for asset in asset_files)
            or not os.path.exists(article_image)
            or not os.path.exists(support_video)
        ):
            return

    intermediate_output = f"articles/{article_id}_intermediate.mp4"
    final_output = f"articles/{article_id}.mp4"
    rename_existing_file(final_output)

    # Concatenate assets
    with open("filelist.txt", "w") as filelist:
        for asset in asset_files:
            filelist.write(f"file '{asset}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "filelist.txt",
            "-vf",
            "xfade=transition=fadegrays:duration=1:offset=4",
            "-c",
            "copy",
            intermediate_output,
        ]
    )

    os.remove("filelist.txt")

    # Add article image at the beginning
    subprocess.run(
        [
            "ffmpeg",
            "-loop",
            "1",
            "-i",
            article_image,
            "-i",
            intermediate_output,
            "-filter_complex",
            "[0:v]scale=1920:1080[v0];[v0][1:v]xfade=transition=fadegrays:duration=1:offset=4[outv]",
            "-map",
            "[outv]",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            final_output,
        ]
    )

    # Add support video at the end
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            final_output,
            "-i",
            support_video,
            "-filter_complex",
            "[0:v][1:v]xfade=transition=fadegrays:duration=1:offset=4[outv]",
            "-map",
            "[outv]",
            "-map",
            "0:a",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            final_output,
        ]
    )

    os.remove(intermediate_output)
