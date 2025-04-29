# Qase Help Center Video Production

## Overview

This repository contains a Python-based video processing pipeline designed to streamline the creation of help videos for the Qase Help Center and Academy. The scripts in the `modules` directory handle distinct steps in the video production process, enabling modular and efficient workflows. The pipeline supports creating short, self-contained video assets and combining them into comprehensive article videos.

### Key Modules
- **AI Voiceover Generation**: `labs.py` – Transcribes video audio, allows transcript editing, and generates AI voiceovers using Eleven Labs.
- **Video Concatenation**: `merge.py` – Combines multiple video pieces into a single asset or article video, ensuring uniform resolution and frame rate.
- **Title Slide Generation**: `title.py` – Converts PNG title images into short video clips for assets and articles.
- **Background Music Addition**: `bg.py` – Adds background music to videos with customizable volume and fade effects.
- **Google Drive Upload**: `drive.py` – Uploads final videos to a designated Google Drive folder and generates shareable links.

## Project Structure

```
./
├── modules/
│   ├── bg.py               # Adds background music to videos
│   ├── credentials.json    # Google API credentials for Drive access
│   ├── drive.py            # Uploads videos to Google Drive
│   ├── labs.py             # Handles AI voiceover generation
│   ├── merge.py            # Concatenates video pieces
│   ├── title.py            # Generates title slide videos from PNGs
│   ├── token.json          # Stores Google Drive authentication token
│   ├── *.py.~1~            # Backup files for modules (can be ignored)
├── main.py                 # Orchestrates the full pipeline or runs labs independently
├── requirements.txt        # Python dependencies
```

### Directory Usage
- **~/screen-studio/**: Store raw video recordings (1080p, 60fps) for processing by `labs.py`.
- **./pieces/**: Store video pieces (e.g., `<asset_id>_0.mp4`, `<asset_id>_1.mp4`) and title PNGs (in `./pieces/title/`).
- **./assets/**: Store compiled asset videos (e.g., `<asset_id>.mp4`) after merging.
- **./bg/**: Store background music file (`default.mp3`) for `bg.py`.
- **./articles/**: Store article videos (e.g., `<article_id>.mp4`) and title PNGs (in `./articles/title/`).
- **./frappe/**: Output directory for videos with background music from `bg.py`.
- **./pieces/trash/**: Temporary directory for normalized video files during merging.

## The Complete Flow

### Video Production Concept
Videos are organized into **assets** and **articles**:
- **Assets**: Short (ideally <2 minutes), self-contained videos covering a specific topic or feature. Each asset must be understandable independently and reusable across contexts. Assets are recorded in smaller pieces (e.g., one per screen or segment) to simplify recording and editing.
- **Articles**: Comprehensive videos that explain a feature in full, created by combining an intro, a title slide, _multiple assets_, and an outro.

To reduce friction in production:
- Assets are broken into smaller pieces (e.g., `<asset_id>_0.mp4` for title, `<asset_id>_1.mp4`, etc.) for easier recording.
- The pipeline automates normalization, concatenation, background track addition, and uploading.

### Workflow Steps
1. **Record Pieces**: Record raw video pieces in `~/screen-studio/` (1080p, 60fps).
2. **AI Voiceover (Optional)**: Use `labs.py` to transcribe audio, edit transcripts, and generate AI voiceovers, saving the result in `~/qh/pieces/`.
3. **Create Title Slides**: Use `title.py` to convert PNGs in `./pieces/title/` or `./articles/title/` into 2-second title videos.
4. **Merge Videos**: Use `merge.py` to combine pieces into assets (in `./assets/`) or articles (in `./articles/`), including intro and outro for articles.
5. **Add Background Music**: Use `bg.py` to add music to assets (output to `./frappe/`) or articles (overwrites original with backup).
6. **Upload to Drive**: Use `drive.py` to upload assets to Google Drive and copy shareable links to the clipboard.

## Installation

### Prerequisites
- **Python 3.9.x**: Required for compatibility with dependencies.
- **FFmpeg**: Required for video processing (install via `brew install ffmpeg` on macOS or equivalent for your system).
- **Google Cloud Project**: Set up a project with the Drive API enabled and download `credentials.json` to `./modules/`.
- **Eleven Labs API Key**: Set the `ELEVEN_LABS_TOKEN` environment variable for AI voiceovers.

### Setup
1. **Install Python 3.9**:
   ```sh
   brew install python@3.9
   brew link --force --overwrite python@3.9
   python3.9 --version  # Verify installation
   ```

2. **Create Virtual Environment**:
   ```sh
   python3.9 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Google Drive**:
   - Place `credentials.json` in `./modules/`. [`credentials.json` will be shared in the DMs, it's not in this repository]
   - Run `drive.py` once to authenticate and generate `token.json`.

5. **Set Eleven Labs API Key**:
   ```sh
   export ELEVEN_LABS_TOKEN="your-eleven-labs-api-key"
   ```
For [5], consider adding this variable to your shell config file (.bashrc / .zshrc etc)


## Usage

### Directory Preparation
Before running the scripts, ensure the following:
- **Raw Videos**: Place recorded videos in `~/screen-studio/` (1080p, 60fps).
- **Title PNGs**:
  - For assets: Place `<asset_id>.png` in `./pieces/title/`.
  - For articles: Place `<article_id>.png` in `./articles/title/`.
- **Background Music**: Place `default.mp3` in `./bg/`.
- **Intro/Outro**: Place `intro.mp4` and `outro.mp4` in `./articles/intro/` and `./articles/outro/`, respectively (for articles).

### Running the AI Voiceover Module
The `labs.py` module is run independently to process raw videos with AI voiceovers:
```sh
python3.9 main.py --labs -i
```
- **--labs**: Runs only `labs.py`.
- **-i**: Enables an interactive file picker for selecting videos from `~/screen-studio/`. Without `-i`, enter the video name (without `.mp4`) or press Enter for the latest video.

**Process**:
1. Transcribes audio using OpenAI Whisper.
2. Saves transcript as JSON in a temporary directory and opens it in your editor (defaults to `nvim`; **set `EDITOR` environment variable to change**).
3. Edit the transcript as needed.
4. Generates AI voiceovers via Eleven Labs API, aligning audio clips with video timestamps.
5. Merges voiceovers with the original video and plays it for review.
6. Press Enter to save (prompts for a filename) or `n` to re-edit the transcript.
7. Saves the final video to `~/qh/pieces/` (e.g., `<asset_id>_<part_number>.mp4`).

### Running the Full Pipeline
The full pipeline processes assets or articles through all steps (title, merge, background music, upload). Run from the root directory:

#### For an Asset
```sh
python3.9 main.py --assets=<asset_id>   # accepts only one id per run
```
- **<asset_id>**: A single number (e.g., `45`).
- **Requirements**:
  - Title PNG: `./pieces/title/<asset_id>.png`.
  - Video pieces: `./pieces/<asset_id>_0.mp4`, `<asset_id>_1.mp4`, etc.
- **Steps**:
  1. **Title**: Converts `<asset_id>.png` to `<asset_id>_0.mp4` in `./pieces/` (skips if exists).
  2. **Merge**: Combines pieces into `./assets/<asset_id>.mp4`, normalizing resolution (1920x1080), frame rate (60fps), and audio (stereo, 44.1kHz).
  3. **Background Music**: Adds music from `./bg/default.mp3` to the asset, saving to `./frappe/<asset_id>.mp4`.
  4. **Upload**: Uploads `./frappe/<asset_id>.mp4` to Google Drive and copies the shareable link to the clipboard.

#### For an Article
```sh
python3.9 main.py --articles=<article_id>,<asset_id1>,<asset_id2>,...
```
- **<article_id>**: The article ID (e.g., `34`).
- **<asset_id1>,<asset_id2>,...**: Comma-separated asset IDs (e.g., `23,45,56`).
- **Requirements**:
  - Title PNG: `./articles/title/<article_id>.png`.
  - Asset videos: `./assets/<asset_id1>.mp4`, `./assets/<asset_id2>.mp4`, etc.
  - Intro/Outro (optional): `./articles/intro/intro.mp4`, `./articles/outro/outro.mp4`.
- **Steps**:
  1. **Title**: Converts `<article_id>.png` to `<article_id>_0.mp4` in `./articles/` (skips if exists).
  2. **Merge**: Combines intro, `<article_id>_0.mp4`, asset videos, and outro into `./articles/<article_id>.mp4`. If an asset video is missing, it generates it from `./pieces/<asset_id>_*.mp4`.
  3. **Background Music**: Adds music to `./articles/<article_id>.mp4`, overwriting the original with a backup in `./articles/backup/`.
  4. **Upload**: Skipped for articles (only assets are uploaded).

### Example Commands
- Process a single asset (ID 45):
  ```sh
  python3.9 main.py --assets=45
  ```
- Process an article (ID 34, using assets 23, 45, 56):
  ```sh
  python3.9 main.py --articles=34,23,45,56
  ```
- Run AI voiceover with interactive file picker:
  ```sh
  python3.9 main.py --labs -i
  ```

## Notes
- **Error Handling**: The scripts log errors to `video_processing.log` and the console. Check logs for debugging.
- **File Naming**:
  - Asset pieces: `<asset_id>_<index>.mp4` (e.g., `45_1.mp4`).
  - Title videos: `<id>_0.mp4` (e.g., `45_0.mp4` for assets, `34_0.mp4` for articles).
  - Final assets: `<asset_id>.mp4` in `./assets/`.
  - Final articles: `<article_id>.mp4` in `./articles/`.
- **Backups**: For articles, `bg.py` backs up the original video to `./articles/backup/` before overwriting.
- **Temporary Files**: `labs.py` and `merge.py` use temporary directories (`./pieces/trash/` for merging), cleaned up after processing.
- **Google Drive**: Ensure `FOLDER_ID` in `drive.py` matches your target folder. Re-authenticate if `token.json` expires.

## Troubleshooting
- **Missing Files**: Ensure title PNGs, video pieces, and background music are in the correct directories.
- **FFmpeg Errors**: Verify FFmpeg is installed and accessible in your PATH.
- **Drive Authentication**: If `token.json` is invalid, delete it and re-run `drive.py` to re-authenticate.
- **Eleven Labs API**: Check that `ELEVEN_LABS_TOKEN` is set and valid.
- **Python Version**: Use Python 3.9 to avoid dependency issues.
