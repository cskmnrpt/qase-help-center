import argparse
import logging
import sys
from modules.bg import add_background_music
from modules.drive import upload_to_drive
from modules.labs import process_labs
from modules.merge import merge_videos, cleanup_title_video
from modules.title import convert_titles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("video_processing.log")
    ]
)
logger = logging.getLogger(__name__)

def validate_id(id_string):
    """Validate that the ID is a positive integer or comma-separated positive integers."""
    if not id_string:
        return None
    try:
        ids = id_string.split(",")
        for id_val in ids:
            id_value = int(id_val)
            if id_value <= 0:
                raise ValueError("IDs must be positive integers.")
        return id_string  # Return as string
    except ValueError as e:
        raise ValueError(f"Invalid ID format: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Run video processing scripts in sequence or labs only."
    )
    parser.add_argument(
        "--assets", type=str, help="Single asset ID (e.g., 1)"
    )
    parser.add_argument(
        "--articles", type=str, help="Comma-separated article and asset IDs (e.g., 11,24,55,65)"
    )
    parser.add_argument(
        "--labs", action="store_true", help="Run only the labs script"
    )
    parser.add_argument(
        "-i", action="store_true", help="Show interactive file picker (for labs)"
    )

    args = parser.parse_args()

    try:
        # Validate IDs
        args.assets = validate_id(args.assets) if args.assets else None
        args.articles = validate_id(args.articles) if args.articles else None

        if args.labs:
            logger.info("Running labs script only...")
            try:
                process_labs(args)
                logger.info("Labs script completed successfully.")
            except Exception as e:
                logger.error(f"Labs script failed: {e}")
                sys.exit(1)
        else:
            logger.info("Starting video processing pipeline: title -> merge -> bg -> drive")

            # Step 1: Convert titles
            if args.assets or args.articles:
                logger.info("Step 1: Converting titles...")
                try:
                    convert_titles(args)
                    logger.info("Title conversion completed successfully.")
                except FileNotFoundError as e:
                    logger.error(f"Title conversion failed: Missing file - {e}")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Title conversion failed: {e}")
                    sys.exit(1)
            else:
                logger.warning("Step 1: Skipping titles (no assets or articles provided)")

            # Step 2: Merge videos
            if args.assets or args.articles:
                logger.info("Step 2: Merging videos...")
                try:
                    merge_success = merge_videos(args)
                    if merge_success:
                        logger.info("Video merging completed successfully.")
                        
                        # Clean up title video for assets only
                        if args.assets:
                            logger.info("Cleaning up title video...")
                            cleanup_success = cleanup_title_video(args.assets, logger)
                            if cleanup_success:
                                logger.info("Title video cleanup completed successfully.")
                            else:
                                logger.warning("Title video cleanup failed or was skipped.")
                    else:
                        logger.error("Video merging failed.")
                        sys.exit(1)
                except FileNotFoundError as e:
                    logger.error(f"Video merging failed: Missing file - {e}")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Video merging failed: {e}")
                    sys.exit(1)
            else:
                logger.warning("Step 2: Skipping merge (no assets or articles provided)")

            # Step 3: Add background music
            if args.assets or args.articles:
                logger.info("Step 3: Adding background music...")
                try:
                    add_background_music(args)
                    logger.info("Background music added successfully.")
                except FileNotFoundError as e:
                    logger.error(f"Background music addition failed: Missing file - {e}")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Background music addition failed: {e}")
                    sys.exit(1)
            else:
                logger.warning("Step 3: Skipping background music (no assets or articles provided)")

            # Step 4: Upload to Google Drive
            if args.assets:
                logger.info("Step 4: Uploading to Google Drive...")
                try:
                    upload_to_drive(args)
                    logger.info("Upload to Google Drive completed successfully.")
                except FileNotFoundError as e:
                    logger.error(f"Upload failed: Missing file - {e}")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Upload failed: {e}")
                    sys.exit(1)
            else:
                logger.warning("Step 4: Skipping upload (no assets provided)")

            logger.info("All steps completed successfully.")

    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
