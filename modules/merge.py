import argparse
import json
import os
import shutil
import subprocess
import logging


def get_file_info(input_file):
    """
    Get detailed info about a file using ffprobe (duration, video frame rate, audio sample rate).
    """
    command = [
        "ffprobe",
        "-i",
        input_file,
        "-show_entries",
        "format=duration:stream=codec_type,r_frame_rate,sample_rate,channels",
        "-v",
        "quiet",
        "-of",
        "json",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        duration = float(data["format"].get("duration", 0.0))
        video_fps = None
        audio_rate = None
        audio_channels = None
        for stream in data.get("streams", []):
            if stream["codec_type"] == "video":
                num, denom = stream["r_frame_rate"].split("/")
                video_fps = float(num) / float(denom)
            elif stream["codec_type"] == "audio":
                audio_rate = int(stream.get("sample_rate", 0))
                audio_channels = int(stream.get("channels", 0))
        return {
            "duration": duration,
            "fps": video_fps,
            "audio_rate": audio_rate,
            "channels": audio_channels,
        }
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"⚠️ Error parsing ffprobe output for {input_file}: {e}")
        return {"duration": 0.0, "fps": None, "audio_rate": None, "channels": None}


def get_sorted_video_files(directory, asset_id=None, article_ids=None):
    """
    Get a list of video files for an asset or article sequence.
    For assets: Collect all files matching the asset ID (e.g., 45_0.mp4, 45_1.mp4).
    For articles: Collect files for each asset ID (e.g., 23.mp4).
    """
    if asset_id:
        # For assets: Collect all files like <asset_id>_<index>.mp4
        files = [f for f in os.listdir(directory) if f.startswith(f"{asset_id}_") and f.endswith(".mp4")]
        if not files:
            print(f"❌ No files found for asset ID {asset_id} in {directory}")
            return []
        files.sort()  # Sort by index (e.g., 45_0.mp4, 45_1.mp4)
        return [os.path.abspath(os.path.join(directory, f)) for f in files]
    
    if article_ids:
        # For articles: Collect single files like <asset_id>.mp4
        video_files = []
        for asset_id in article_ids:
            asset_file = os.path.abspath(os.path.join(directory, f"{asset_id}.mp4"))
            if not os.path.exists(asset_file):
                print(f"⚠️ Asset video {asset_file} not found. Generating from ./pieces/")
                # Generate the asset video using asset logic
                asset_videos = get_sorted_video_files("./pieces", asset_id=asset_id)
                if not asset_videos:
                    print(f"❌ Failed to generate asset video {asset_file}: No source files found")
                    continue
                # Normalize and concatenate to create the asset video
                temp_output = asset_file  # Directly create ./assets/<asset_id>.mp4
                normalized_files = normalize_and_collect(asset_videos, asset_id, "./pieces/trash")
                if not normalized_files:
                    print(f"❌ Failed to normalize files for asset {asset_id}")
                    continue
                concatenate_videos(normalized_files, temp_output, asset_id)
                if not os.path.exists(asset_file):
                    print(f"❌ Failed to generate asset video {asset_file}")
                    continue
                print(f"✅ Successfully generated asset video {asset_file}")
            video_files.append(asset_file)
        return video_files
    
    print("❌ Invalid call to get_sorted_video_files: No asset_id or article_ids provided")
    return []


def check_audio_stream(input_file):
    """
    Check if the input video has an audio stream.
    """
    command = [
        "ffprobe",
        "-i",
        input_file,
        "-show_streams",
        "-select_streams",
        "a",
        "-loglevel",
        "error",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return bool(result.stdout.strip())


def normalize_video(input_file, output_file):
    """
    Normalize video to 1920x1080, 60fps, H.264, with stereo AAC audio at 44.1kHz.
    """
    has_audio = check_audio_stream(input_file)
    info = get_file_info(input_file)
    print(
        f"📋 Input {os.path.basename(input_file)}: Duration={info['duration']:.2f}s, FPS={info['fps']}, Audio Rate={info['audio_rate']}, Channels={info['channels']}"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vf",
        "scale=1920:1080,fps=60,setpts=PTS-STARTPTS",
        "-c:v",
        "libx264",
        "-r",
        "60",
        "-pix_fmt",
        "yuv420p",
    ]

    if has_audio:
        command.extend(
            [
                "-af",
                "aresample=44100,asetpts=PTS-STARTPTS",
                "-c:a",
                "aac",
                "-ac",
                "2",
                "-ar",
                "44100",
            ]
        )
    else:
        command.extend(
            [
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-c:a",
                "aac",
                "-ac",
                "2",
                "-ar",
                "44100",
                "-af",
                "asetpts=PTS-STARTPTS",
            ]
        )

    command.append(output_file)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg Error while normalizing {input_file}:\n{result.stderr}")
    else:
        norm_info = get_file_info(output_file)
        print(
            f"✅ Normalized: {input_file} -> {output_file} (Duration={norm_info['duration']:.2f}s, Channels={norm_info['channels']})"
        )


def normalize_and_collect(video_files, base_id, trash_dir):
    """
    Helper function to normalize a list of video files and collect them in the trash directory.
    """
    os.makedirs(trash_dir, exist_ok=True)
    normalized_files = []
    for i, video in enumerate(video_files):
        norm_file = os.path.abspath(
            os.path.join(trash_dir, f"normalized_{base_id}_{i}.mp4")
        )
        if not os.path.exists(norm_file):
            normalize_video(video, norm_file)
        if os.path.exists(norm_file):
            normalized_files.append(norm_file)
        else:
            print(f"❌ Failed to normalize {video}. Skipping.")
    return normalized_files


def concatenate_videos(normalized_files, output_file, base_id):
    """
    Helper function to concatenate normalized files into a single output.
    """
    if os.path.exists(output_file):
        os.remove(output_file)

    if len(normalized_files) < 1:
        print(f"❌ No valid files to concatenate for {base_id}")
        return
    elif len(normalized_files) == 1:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            normalized_files[0],
            "-c",
            "copy",
            output_file,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Single file copied: {output_file}")
        else:
            print(f"❌ Error copying single file {base_id}:\n{result.stderr}")
        return

    # Use concat filter for precise merging
    command = ["ffmpeg", "-y"]
    for norm_file in normalized_files:
        command.extend(["-i", norm_file])
    command.extend(
        [
            "-filter_complex",
            f"[0:v][0:a][1:v][1:a]concat=n={len(normalized_files)}:v=1:a=1[v][a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-r",
            "60",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ac",
            "2",
            "-ar",
            "44100",
            output_file,
        ]
    )
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        final_info = get_file_info(output_file)
        print(
            f"✅ Merged: {output_file} (Duration={final_info['duration']:.2f}s, Channels={final_info['channels']})"
        )
    else:
        print(f"❌ FFmpeg Error while merging {base_id}:\n{result.stderr}")


def cleanup_title_video(asset_id, logger=None):
    """
    Move the title video (_0.mp4) to trash after successful asset merging.
    Only called for assets, not articles.
    """
    title_video_path = os.path.abspath(os.path.join("./pieces", f"{asset_id}_0.mp4"))
    
    # Check if title video exists
    if not os.path.exists(title_video_path):
        if logger:
            logger.warning(f"Title video {title_video_path} not found for cleanup")
        return False
    
    # Check if final asset was successfully created
    final_asset_path = os.path.abspath(os.path.join("./assets", f"{asset_id}.mp4"))
    if not os.path.exists(final_asset_path):
        if logger:
            logger.warning(f"Final asset {final_asset_path} not found, skipping title cleanup")
        return False
    
    try:
        # Use macOS trash command
        import platform
        if os.name == 'posix' and platform.system() == 'Darwin':
            # macOS - use 'mv' to trash with expanded path
            home_dir = os.path.expanduser("~")
            trash_dir = os.path.join(home_dir, ".Trash")
            trash_result = subprocess.run(
                ["mv", title_video_path, trash_dir],
                capture_output=True,
                text=True
            )
            if trash_result.returncode == 0:
                if logger:
                    logger.info(f"Moved title video {title_video_path} to trash")
                else:
                    print(f"🗑️ Moved title video {os.path.basename(title_video_path)} to trash")
                return True
            else:
                if logger:
                    logger.error(f"Failed to move title video to trash: {trash_result.stderr}")
                else:
                    print(f"❌ Failed to move title video to trash: {trash_result.stderr}")
                return False
        else:
            # Non-macOS - use shutil.move to a local trash directory
            trash_dir = os.path.abspath("./pieces/trash")
            os.makedirs(trash_dir, exist_ok=True)
            trash_path = os.path.join(trash_dir, f"{asset_id}_0.mp4")
            shutil.move(title_video_path, trash_path)
            if logger:
                logger.info(f"Moved title video {title_video_path} to {trash_path}")
            else:
                print(f"🗑️ Moved title video {os.path.basename(title_video_path)} to trash")
            return True
            
    except Exception as e:
        if logger:
            logger.error(f"Error during title video cleanup: {e}")
        else:
            print(f"❌ Error during title video cleanup: {e}")
        return False


def process_and_concatenate_videos(
    input_directory, output_directory, asset_id=None, article_ids=None
):
    """
    Process and concatenate video files for an asset or article.
    Returns True if successful, False otherwise.
    """
    os.makedirs(output_directory, exist_ok=True)
    trash_dir = os.path.join("./pieces", "trash")  # Always use ./pieces/trash/
    os.makedirs(trash_dir, exist_ok=True)

    video_files = []
    output_file = None

    if asset_id:
        # Handle --assets
        video_files = get_sorted_video_files(input_directory, asset_id=asset_id)
        if not video_files:
            print(f"❌ No valid files to process for asset ID {asset_id}")
            return False
        output_file = os.path.abspath(os.path.join(output_directory, f"{asset_id}.mp4"))
    
    elif article_ids:
        # Handle --articles
        article_id = article_ids[0]  # First ID is the article ID
        asset_ids = article_ids[1:]  # Remaining IDs are asset IDs
        output_file = os.path.abspath(os.path.join(output_directory, f"{article_id}.mp4"))

        # Add intro
        intro_file = os.path.abspath("./articles/intro/intro.mp4")
        if os.path.exists(intro_file):
            video_files.append(intro_file)
        else:
            print(f"⚠️ Intro file {intro_file} not found. Proceeding without intro.")

        # Add title video
        title_file = os.path.abspath(os.path.join("./articles", f"{article_id}_0.mp4"))
        if os.path.exists(title_file):
            video_files.append(title_file)
        else:
            print(f"❌ Title video {title_file} not found. Cannot proceed with article {article_id}.")
            return False

        # Add asset videos
        video_files.extend(get_sorted_video_files("./assets", article_ids=asset_ids))

        # Add outro
        outro_file = os.path.abspath("./articles/outro/outro.mp4")
        if os.path.exists(outro_file):
            video_files.append(outro_file)
        else:
            print(f"⚠️ Outro file {outro_file} not found. Proceeding without outro.")

        if len(video_files) < 2:  # At least title + one other video
            print(f"❌ Insufficient valid files to process for article {article_id}")
            return False

    # Normalize and concatenate
    normalized_files = normalize_and_collect(video_files, asset_id or article_ids[0], trash_dir)
    concatenate_videos(normalized_files, output_file, asset_id or article_ids[0])

    # Check if the final output file was created successfully
    if not os.path.exists(output_file):
        print(f"❌ Final output file {output_file} was not created")
        return False

    # Clean up trash directory after processing
    shutil.rmtree(trash_dir)
    os.makedirs(trash_dir)  # Recreate empty trash directory
    
    return True


def merge_videos(args):
    """
    Main function to handle --assets or --articles processing.
    Returns True if successful, False otherwise.
    """
    if args.assets and args.articles:
        print("❌ Error: Cannot use both --assets and --articles flags simultaneously.")
        return False
    
    if args.assets:
        # Validate --assets: Only one ID allowed
        try:
            asset_id = args.assets.strip()
            if "," in asset_id:
                print("❌ Error: --assets accepts only one ID (e.g., --assets=45).")
                return False
            int(asset_id)  # Ensure it's a valid number
        except ValueError:
            print(f"❌ Error: Invalid asset ID '{args.assets}'. Must be a number.")
            return False
        
        # Check if final output video already exists
        output_file = os.path.abspath(os.path.join("./assets", f"{asset_id}.mp4"))
        if os.path.exists(output_file):
            print(f"✅ Final video {output_file} already exists. Skipping merge for asset {asset_id}.")
            return True
        
        input_directory = "./pieces/"
        output_directory = "./assets/"
        success = process_and_concatenate_videos(input_directory, output_directory, asset_id=asset_id)
        return success
    
    elif args.articles:
        # Validate --articles: At least one ID, no duplicate asset IDs (except article ID)
        try:
            article_ids = [id.strip() for id in args.articles.split(",")]
            if not article_ids:
                print("❌ Error: --articles requires at least one ID (e.g., --articles=34,23,45).")
                return False
            for id in article_ids:
                int(id)  # Ensure all IDs are valid numbers
            # Check for duplicate asset IDs (excluding the article ID)
            asset_ids = article_ids[1:]
            if len(asset_ids) != len(set(asset_ids)):
                print(f"❌ Error: Duplicate asset IDs found in '{args.articles}'. Asset IDs (after the first) must be unique.")
                return False
        except ValueError:
            print(f"❌ Error: Invalid article IDs '{args.articles}'. All IDs must be numbers.")
            return False
        
        # Check if final output video already exists
        article_id = article_ids[0]
        output_file = os.path.abspath(os.path.join("./articles", f"{article_id}.mp4"))
        if os.path.exists(output_file):
            print(f"✅ Final video {output_file} already exists. Skipping merge for article {article_id}.")
            return True
        
        input_directory = "./assets/"  # For asset videos
        output_directory = "./articles/"
        success = process_and_concatenate_videos(input_directory, output_directory, article_ids=article_ids)
        return success
    
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and concatenate video files.")
    parser.add_argument(
        "--assets",
        type=str,
        help="Single asset ID to process (e.g., 45)",
    )
    parser.add_argument(
        "--articles",
        type=str,
        help="Comma-separated list of article and asset IDs (e.g., 34,23,45,56,67)",
    )
    args = parser.parse_args()
    
    if not args.assets and not args.articles:
        print("❌ Error: Must provide either --assets or --articles flag.")
    else:
        merge_videos(args)
