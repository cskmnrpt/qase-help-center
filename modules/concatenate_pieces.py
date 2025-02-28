import os
import subprocess

from modules.utils import get_asset_pieces, rename_existing_file


def concatenate_pieces(asset_ids):
    for asset_id in asset_ids.split(","):
        pieces = get_asset_pieces(asset_id)
        if not pieces:
            print(
                f"No pieces found for asset {asset_id}. Please add the missing pieces and press Enter to continue."
            )
            input()
            pieces = get_asset_pieces(asset_id)
            if not pieces:
                continue

        output_file = f"assets/{asset_id}.mp4"
        rename_existing_file(output_file)

        with open("filelist.txt", "w") as filelist:
            for piece in pieces:
                filelist.write(f"file '{piece}'\n")

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
                "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1",
                "-c",
                "copy",
                output_file,
            ]
        )

        os.remove("filelist.txt")
