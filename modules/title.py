#!/usr/bin/env python3

import argparse
import os
import subprocess
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

# Video settings
DURATION = 2  # seconds, easily changeable
FPS = 60
WIDTH = 1920
HEIGHT = 1080


def parse_args():
    parser = argparse.ArgumentParser(description="Convert PNGs to videos using FFmpeg")
    parser.add_argument(
        "--assets", type=str, help="Single asset ID (e.g., 1)"
    )
    parser.add_argument(
        "--articles", type=str, help="Comma-separated article and asset IDs (e.g., 11,24,55,65)"
    )
    return parser.parse_args()


def validate_id(id_str):
    try:
        id_val = int(id_str)
        return id_val > 0
    except ValueError:
        return False


def check_and_get_input_path(base_dir, id_str):
    file_path = os.path.join(base_dir, "title", f"{id_str}.png")
    while not os.path.exists(file_path):
        debug_print(f"Error: {file_path} not found")
        response = (
            input("Add the PNG file and press Enter to retry, or type 'skip' to skip: ")
            .strip()
            .lower()
        )
        if response == "skip":
            return None
    return file_path


def create_video(input_path, output_path):
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        input_path,
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v",
        "libx264",
        "-t",
        str(DURATION),
        "-r",
        str(FPS),
        "-vf",
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:-1:-1:color=black",
        "-c:a",
        "aac",
        "-shortest",
        "-y",  # Overwrite output without asking
        output_path,
    ]

    try:
        subprocess.run(
            ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        debug_print(f"Successfully created {output_path}")
    except subprocess.CalledProcessError as e:
        debug_print(f"Error creating {output_path}: {e.stderr.decode()}")


def process_items(items, input_base, output_base):
    if not items:
        return

    # Treat items as a single ID
    item_list = [items]

    for item in item_list:
        if not validate_id(item):
            debug_print(f"Invalid ID: {item} - must be a positive integer")
            continue

        # Check if output video already exists
        output_path = os.path.join(output_base, f"{item}_0.mp4")
        if os.path.exists(output_path):
            debug_print(f"✅ Title video {output_path} already exists. Skipping {input_base.split('/')[-1]} {item}.")
            continue

        input_path = check_and_get_input_path(input_base, item)
        if input_path is None:
            debug_print(f"Skipping {item}")
            continue

        create_video(input_path, output_path)


def convert_titles(args):
    if args.assets:
        process_items(args.assets, "./pieces", "./pieces")
    if args.articles:
        # Split articles into article ID (first) and asset IDs (rest)
        article_ids = args.articles.split(",")
        if article_ids and article_ids[0]:
            # Process article ID (output to ./articles/)
            process_items(article_ids[0], "./articles", "./articles")
            # Process asset IDs (output to ./pieces/)
            for asset_id in article_ids[1:]:
                if asset_id:
                    process_items(asset_id, "./pieces", "./pieces")


if __name__ == "__main__":
    args = parse_args()
    convert_titles(args)
