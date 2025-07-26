import argparse
import os
import json
import time
import subprocess
import shutil
from functools import wraps

import pyperclip
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Import debug mode from main
try:
    from main import DEBUG_MODE
except ImportError:
    DEBUG_MODE = False

def debug_print(message):
    """Print message only in debug mode."""
    if DEBUG_MODE:
        print(message)

# Scopes define the level of access
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Folder ID where the files will be uploaded
FOLDER_ID = "1nCzh_KKRXc7p2k3NHfJTEeG1bjvgdXWD"

# Base and Asset directory for the script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "frappe")
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))  # ~/qh/modules/

def retry_on_failure(max_attempts=3, initial_delay=1):
    """Decorator to retry a function on HttpError with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = initial_delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise Exception(f"Failed after {max_attempts} attempts: {str(e)}")
                    print(f"Error: {str(e)}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
        return wrapper
    return decorator

def authenticate():
    creds = None
    token_path = os.path.join(MODULES_DIR, "token.json")
    client_secrets_path = os.path.join(MODULES_DIR, "credentials.json")

    # Try loading existing credentials
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds.valid:
                debug_print("Using existing valid credentials from token.json")
                return creds
            if creds.expired and creds.refresh_token:
                debug_print("Refreshing expired credentials...")
                creds.refresh(Request())
                # Save refreshed credentials
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                debug_print("Credentials refreshed and saved to token.json")
                return creds
            else:
                debug_print("Credentials invalid or missing refresh_token. Re-authenticating...")
        except Exception as e:
            debug_print(f"Failed to load or refresh credentials from {token_path}: {str(e)}. Re-authenticating...")

    # If credentials are missing or invalid, authenticate
    if not os.path.exists(client_secrets_path):
        raise FileNotFoundError(
            f"Error: {client_secrets_path} not found. Please download it from Google Cloud Console."
        )
    
    debug_print("Initiating new authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save new credentials
    try:
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        debug_print(f"New credentials saved to {token_path}")
    except Exception as e:
        debug_print(f"Warning: Failed to save credentials to {token_path}: {str(e)}")
    
    return creds

def get_file_path(asset_id):
    """Get file path for the provided asset ID."""
    file_path = os.path.join(ASSETS_DIR, f"{asset_id}.mp4")
    file_name = f"{asset_id}.mp4"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    return file_path, file_name

def play_video(file_path):
    """Play the video using mpv, vlc, or the default system player."""
    debug_print(f"Playing video: {file_path}")
    try:
        # Try mpv first
        if shutil.which("mpv"):
            subprocess.run(["mpv", file_path], check=True)
            return True
        # Try vlc
        elif shutil.which("vlc"):
            subprocess.run(["vlc", file_path], check=True)
            return True
        # Fallback to system default
        else:
            if os.name == "nt":  # Windows
                os.startfile(file_path)
            else:  # macOS/Linux
                subprocess.run(["open", file_path], check=True)
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        debug_print(f"Failed to play video: {str(e)}")
        debug_print("Proceeding to upload prompt...")
        return False

@retry_on_failure(max_attempts=3, initial_delay=1)
def upload_file(file_name, file_path, creds):
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype="video/mp4")
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    debug_print(f"Uploaded {file_name} - File ID: {file.get('id')}")
    return file.get("id")

@retry_on_failure(max_attempts=3, initial_delay=1)
def create_shareable_link(file_id, creds):
    service = build("drive", "v3", credentials=creds)
    permission = {
        "role": "reader",
        "type": "anyone",
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    file = service.files().get(fileId=file_id, fields="webViewLink").execute()
    return file.get("webViewLink")

def upload_to_drive(args):
    if not args.assets:
        parser = argparse.ArgumentParser()
        parser.error("--assets must be provided with a single number.")
    try:
        asset_id = int(args.assets)  # Ensure asset_id is a number
    except ValueError:
        raise ValueError("--assets must be a single number (e.g., 1).")
    
    # Get file path
    file_path, file_name = get_file_path(args.assets)
    
    # Play the video
    play_video(file_path)
    
    # Prompt user for upload confirmation
    print("\nPress Enter to upload the video to Google Drive, or 'n' to quit.")
    user_input = input().strip().lower()
    if user_input == 'n':
        print("Upload cancelled. Exiting.")
        return
    
    # Proceed with upload
    creds = authenticate()
    file_id = upload_file(file_name, file_path, creds)
    link = create_shareable_link(file_id, creds)
    debug_print(f"Shareable link for {file_name}: {link}")
    pyperclip.copy(link)
    print("\nShareable link has been copied to the clipboard:")
    print(link)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a single file to Google Drive after preview.")
    parser.add_argument(
        "--assets",
        help="A single asset ID (e.g., 1)",
        required=True,
    )
    args = parser.parse_args()
    upload_to_drive(args)
