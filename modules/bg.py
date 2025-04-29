import argparse
import os
import shutil
import sys
from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoFileClip


def validate_video_integrity(file_path):
    """
    Check if the video can be fully read by moviepy to detect corruption.
    Returns (success, message).
    """
    try:
        # Load video and attempt to access its duration and frame count
        video = VideoFileClip(file_path)
        duration = video.duration  # Force reading metadata
        frame_count = video.reader.nframes  # Force reading frame count
        video.close()  # Close to free resources
        return True, "Video integrity check passed"
    except Exception as e:
        return False, f"Video integrity check failed: {str(e)}. The input video may be corrupted."


def process_media(file_path, bg_path, volume=0.07, fade_duration=5):
    """Process a video file by adding background music with fade effects."""
    try:
        # Validate video integrity before processing
        success, message = validate_video_integrity(file_path)
        if not success:
            print(f"Error: {message}")
            input("Press Enter to continue or Ctrl+C to exit...")
            return False, message

        # Check if background audio exists
        if not os.path.exists(bg_path):
            print(f"Error: Background audio file not found: {bg_path}")
            input("Press Enter to continue or Ctrl+C to exit...")
            return False, f"Missing background audio: {bg_path}"

        # Load video and background audio
        video = VideoFileClip(file_path)
        bg_audio = AudioFileClip(bg_path)

        # Adjust background audio duration to match video
        if bg_audio.duration > video.duration:
            bg_audio = bg_audio.subclip(0, video.duration)
        elif bg_audio.duration < video.duration:
            bg_audio = bg_audio.set_duration(video.duration)

        # Apply fade effects and volume
        bg_audio = bg_audio.audio_fadein(fade_duration).audio_fadeout(fade_duration)
        bg_audio = bg_audio.volumex(volume)

        # Combine original audio (if exists) with background
        if video.audio:
            final_audio = CompositeAudioClip([video.audio, bg_audio])
        else:
            final_audio = bg_audio

        # Determine output path and backup logic based on file path
        if "assets" in file_path:
            # For assets, save to ./frappe/ and skip backup/overwriting
            output_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), "frappe")
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                return False, f"Failed to create output directory {output_dir}: {str(e)}"
            output_path = os.path.join(output_dir, os.path.basename(file_path))
        else:
            # For articles, back up and overwrite original
            backup_dir = os.path.join(os.path.dirname(file_path), "backup")
            try:
                os.makedirs(backup_dir, exist_ok=True)
            except OSError as e:
                return False, f"Failed to create backup directory {backup_dir}: {str(e)}"
            
            # Construct backup file path
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            # Copy original file to backup
            try:
                shutil.copy2(file_path, backup_path)
            except (shutil.Error, OSError) as e:
                return False, f"Failed to back up {file_path} to {backup_path}: {str(e)}"
            output_path = file_path

        # Set audio to video and write output
        final_video = video.set_audio(final_audio)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return True, output_path
    except Exception as e:
        return False, str(e)


def add_background_music(args):
    # Define paths relative to root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_path = os.path.join(base_dir, "bg", "default.mp3")

    # Process assets (single ID)
    if args.assets:
        # Check for commas and warn if multiple IDs are provided
        asset_ids = args.assets.split(",")
        if len(asset_ids) > 1:
            print(f"Warning: --assets accepts only one ID; ignoring additional IDs: {asset_ids[1:]}")
        asset_id = asset_ids[0].strip()
        if not asset_id:
            print("Error: --assets ID is empty")
            return

        assets_dir = os.path.join(base_dir, "assets")
        file_path = os.path.join(assets_dir, f"{asset_id}.mp4")
        if os.path.exists(file_path):
            success, result = process_media(file_path, bg_path)
            print(f"Asset {asset_id}: {'Processed as ' + result if success else 'Failed - ' + result}")
        else:
            print(f"Error: Asset file not found: {file_path}")
            input("Press Enter to continue or Ctrl+C to exit...")

    # Process articles (first ID only)
    if args.articles:
        article_ids = args.articles.split(",")
        article_id = article_ids[0].strip()
        if not article_id:
            print("Error: --articles first ID is empty")
            return

        articles_dir = os.path.join(base_dir, "articles")
        file_path = os.path.join(articles_dir, f"{article_id}.mp4")
        if os.path.exists(file_path):
            success, result = process_media(file_path, bg_path)
            print(f"Article {article_id}: {'Processed as ' + result if success else 'Failed - ' + result}")
        else:
            print(f"Error: Article file not found: {file_path}")
            input("Press Enter to continue or Ctrl+C to exit...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add background music to videos")
    parser.add_argument(
        "--assets", type=str, help="Single asset ID (e.g., 1)"
    )
    parser.add_argument(
        "--articles", type=str, help="Comma-separated article and asset IDs, only first used for processing (e.g., 11,24,55,65)"
    )
    args = parser.parse_args()
    add_background_music(args)
