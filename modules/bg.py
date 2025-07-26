import argparse
import os
import shutil
import sys
import ffmpeg
import subprocess

# Import debug mode from main
try:
    from main import DEBUG_MODE
except ImportError:
    DEBUG_MODE = False

def debug_print(message):
    """Print message only in debug mode."""
    if DEBUG_MODE:
        print(message)

def validate_video_integrity(file_path):
    """
    Check if the video can be read by FFmpeg.
    Returns (success, message).
    """
    try:
        # Probe the video to check if it can be read
        ffmpeg.probe(file_path)
        return True, "Video integrity check passed"
    except ffmpeg.Error as e:
        return False, f"Video integrity check failed: {str(e)}. The input video may be corrupted."

def process_media(file_path, bg_path, volume=0.07, fade_duration=5):
    """Process a video file by adding background music with fade effects using FFmpeg."""
    try:
        # Validate video integrity
        success, message = validate_video_integrity(file_path)
        if not success:
            debug_print(f"Error: {message}")
            input("Press Enter to continue or Ctrl+C to exit...")
            return False, message

        # Check if background audio exists
        if not os.path.exists(bg_path):
            debug_print(f"Error: Background audio file not found: {bg_path}")
            input("Press Enter to continue or Ctrl+C to exit...")
            return False, f"Missing background audio: {bg_path}"

        # Get video duration using FFmpeg probe
        probe = ffmpeg.probe(file_path)
        video_duration = float(probe['format']['duration'])

        # Prepare output path and backup logic
        if "assets" in file_path:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), "frappe")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(file_path))
        else:
            backup_dir = os.path.join(os.path.dirname(file_path), "backup")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            try:
                shutil.copy2(file_path, backup_path)
            except (shutil.Error, OSError) as e:
                return False, f"Failed to back up {file_path} to {backup_path}: {str(e)}"
            output_path = file_path

        # Build FFmpeg command
        # Input streams: video and background audio
        input_video = ffmpeg.input(file_path)
        input_audio = ffmpeg.input(bg_path)

        # Trim or loop background audio to match video duration
        audio = input_audio.audio.filter('atrim', duration=video_duration)
        if audio_duration := float(ffmpeg.probe(bg_path)['format']['duration']) < video_duration:
            audio = audio.filter('aloop', loop=-1, size=2**31-1).filter('atrim', duration=video_duration)

        # Apply fade effects and volume
        audio = audio.filter('afade', type='in', start_time=0, duration=fade_duration)
        audio = audio.filter('afade', type='out', start_time=video_duration-fade_duration, duration=fade_duration)
        audio = audio.filter('volume', volume)

        # Mix original audio (if exists) with background audio
        try:
            # Check if video has audio
            ffmpeg.probe(file_path, select_streams='a')
            final_audio = ffmpeg.filter([input_video.audio, audio], 'amix', inputs=2, duration='longest')
        except ffmpeg.Error:
            # No original audio, use background audio only
            final_audio = audio

        # Combine video and audio, write output
        output = ffmpeg.output(
            input_video.video, final_audio, output_path,
            vcodec='libx264', acodec='aac',
            **{'strict': 'experimental'}
        )
        
        # Suppress FFmpeg output unless in debug mode
        if DEBUG_MODE:
            ffmpeg.run(output, overwrite_output=True)
        else:
            ffmpeg.run(output, overwrite_output=True, quiet=True)

        return True, output_path
    except ffmpeg.Error as e:
        return False, f"FFmpeg error: {str(e)}"
    except Exception as e:
        return False, str(e)

def add_background_music(args):
    # Define paths relative to root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_path = os.path.join(base_dir, "bg", "default.mp3")

    # Process assets (single ID)
    if args.assets:
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
        debug_print(f"Asset {asset_id}: {'Processed as ' + result if success else 'Failed - ' + result}")
    else:
        debug_print(f"Error: Asset file not found: {file_path}")
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
        debug_print(f"Article {article_id}: {'Processed as ' + result if success else 'Failed - ' + result}")
    else:
        debug_print(f"Error: Article file not found: {file_path}")
        input("Press Enter to continue or Ctrl+C to exit...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add background music to videos")
    parser.add_argument("--assets", type=str, help="Single asset ID (e.g., 1)")
    parser.add_argument("--articles", type=str, help="Comma-separated article IDs, only first used (e.g., 11,24,55,65)")
    args = parser.parse_args()
    add_background_music(args)
