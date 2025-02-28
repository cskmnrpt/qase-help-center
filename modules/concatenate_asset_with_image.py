import os
import subprocess

from modules.utils import rename_existing_file


def concatenate_asset_with_image(asset_ids):
    for asset_id in asset_ids.split(","):
        asset_file = f"assets/{asset_id}.mp4"
        image_file = f"assets/{asset_id}.png"

        if not os.path.exists(asset_file) or not os.path.exists(image_file):
            print(
                f"Missing asset or image for asset {asset_id}. Please add the missing files and press Enter to continue."
            )
            input()
            if not os.path.exists(asset_file) or not os.path.exists(image_file):
                continue

        output_file = f"assets/{asset_id}_with_image.mp4"
        rename_existing_file(output_file)

        subprocess.run(
            [
                "ffmpeg",
                "-loop",
                "1",
                "-i",
                image_file,
                "-i",
                asset_file,
                "-filter_complex",
                "[0:v]scale=1920:1080[v0];[v0][1:v]xfade=transition=radial:duration=1:offset=4[outv]",
                "-map",
                "[outv]",
                "-map",
                "1:a",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                output_file,
            ]
        )
