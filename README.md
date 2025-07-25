# Qase Help Center Video Production Pipeline

## Overview

This repository contains a Python-based video processing pipeline designed to streamline the creation of help videos for the Qase Help Center and Academy. The scripts in the `modules` directory handle distinct steps in the video production process, enabling modular and efficient workflows. The pipeline supports creating short, self-contained video assets and combining them into comprehensive article videos.

### Prerequisites
- **Python 3.9+** and **FFmpeg**
- **Google Cloud Project** with Drive API enabled
- **Eleven Labs API Key** (for AI voiceovers)

### Installation
```bash
# Clone and setup
mkdir -p ~/qh && git clone https://github.com/cskmnrpt/qase-help-center.git ~/qh
mkdir -p ~/screen-studio
cd ~/qh

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Google Drive (place credentials.json in modules/)
# Set environment variable
export ELEVEN_LABS_TOKEN="your-api-key"
```

### Basic Usage
```bash
# Process a single asset
python main.py --assets=45

# Process an article with multiple assets
python main.py --articles=34,23,45,56

# Generate AI voiceover for raw video
python main.py --labs -i
```

## 📁 Project Structure

```
qh/
├── modules/                 # Core processing modules
│   ├── labs.py             # AI voiceover generation
│   ├── title.py            # Title slide video creation
│   ├── merge.py            # Video concatenation
│   ├── bg.py               # Background music addition
│   ├── drive.py            # Google Drive upload
│   ├── credentials.json    # Google API credentials
│   └── token.json          # Authentication token
├── pieces/                 # Video pieces and titles
│   ├── title/              # PNG title images
│   ├── trash/              # Temporary files
│   └── *.mp4               # Individual video pieces
├── assets/                 # Compiled asset videos
├── articles/               # Article videos and components
│   ├── title/              # Article title images
│   ├── intro/              # Intro videos
│   ├── outro/              # Outro videos
│   └── backup/             # Backup files
├── frappe/                 # Videos with background music
├── bg/                     # Background music files
└── main.py                 # Main orchestration script
```

## Core Concepts

### Assets vs Articles
- **Assets**: Short, self-contained videos (<2 minutes) covering specific topics
- **Articles**: Comprehensive videos combining multiple assets with intro/outro

### Video Production Flow
1. **Record** → Raw videos in `~/screen-studio/`
2. **Voiceover** → AI transcription and voice generation (optional)
3. **Title** → Convert PNGs to video slides
4. **Merge** → Combine pieces into final videos
5. **Music** → Add background audio
6. **Upload** → Share to Google Drive

## Detailed Usage

### 1. AI Voiceover Generation (`labs.py`)

Process raw recordings with AI-generated voiceovers:

```bash
# Interactive file picker
python main.py --labs -i

# Manual file selection
python main.py --labs
```

**Process:**
1. Transcribes audio using OpenAI Whisper
2. Opens transcript in your editor for review/editing
3. Generates AI voiceover via Eleven Labs
4. Merges with original video
5. Saves to `pieces/` directory

**Requirements:**
- Raw videos in `~/screen-studio/`
- `ELEVEN_LABS_TOKEN` environment variable
- Text editor (set via `EDITOR` env var)

### 2. Full Pipeline Processing

#### Asset Processing
```bash
python main.py --assets=45
```

**Requirements:**
- `pieces/title/45.png` - Title image
- `pieces/45_0.mp4`, `pieces/45_1.mp4`, etc. - Video pieces
- `bg/default.mp3` - Background music

**Output:**
- `assets/45.mp4` - Merged video
- `frappe/45.mp4` - Video with background music
- Google Drive upload with shareable link

#### Article Processing
```bash
python main.py --articles=34,23,45,56
```

**Requirements:**
- `articles/title/34.png` - Article title image
- `assets/23.mp4`, `assets/45.mp4`, `assets/56.mp4` - Asset videos
- `articles/intro/intro.mp4` - Intro video (optional)
- `articles/outro/outro.mp4` - Outro video (optional)

**Output:**
- `articles/34.mp4` - Complete article video with background music
- `articles/backup/34.mp4` - Original backup

### 3. Individual Module Usage

Each module can be run independently:

```bash
# Title generation only
python -m modules.title --assets=45

# Video merging only
python -m modules.merge --assets=45

# Background music only
python -m modules.bg --assets=45

# Drive upload only
python -m modules.drive --assets=45
```

## 📋 File Naming Conventions

### Video Pieces
- **Asset pieces**: `<asset_id>_<index>.mp4` (e.g., `45_1.mp4`)
- **Title videos**: `<id>_0.mp4` (e.g., `45_0.mp4`)
- **Final assets**: `<asset_id>.mp4` in `assets/`
- **Final articles**: `<article_id>.mp4` in `articles/`

### Images
- **Asset titles**: `pieces/title/<asset_id>.png`
- **Article titles**: `articles/title/<article_id>.png`

## ⚙️ Configuration

### Environment Variables
```bash
# Required for AI voiceovers
export ELEVEN_LABS_TOKEN="your-eleven-labs-api-key"

# Optional: Set default text editor
export EDITOR="nvim"  # or "vim", "code", etc.

# Optional: Set video player for labs
export LABS_PLAYER="mpv"  # or "vlc"
```

### Google Drive Setup
1. Create a Google Cloud Project
2. Enable the Drive API
3. Create credentials and download `credentials.json`
4. Place in `modules/` directory
5. Run any drive operation to authenticate

### Video Specifications
- **Resolution**: 1920x1080 (automatically scaled)
- **Frame Rate**: 60fps
- **Audio**: Stereo AAC, 44.1kHz
- **Codec**: H.264 video, AAC audio

## 🛠️ Troubleshooting

### Common Issues

**Missing Files**
```bash
# Check if title image exists
ls pieces/title/45.png

# Check if video pieces exist
ls pieces/45_*.mp4

# Check if background music exists
ls bg/default.mp3
```

**FFmpeg Errors**
```bash
# Verify FFmpeg installation
ffmpeg -version

# Check PATH
which ffmpeg
```

**Google Drive Authentication**
```bash
# Remove expired token
rm modules/token.json

# Re-authenticate
python -m modules.drive --assets=1
```

**Eleven Labs API Issues**
```bash
# Verify API key
echo $ELEVEN_LABS_TOKEN

# Test API connection
curl -H "xi-api-key: $ELEVEN_LABS_TOKEN" \
     https://api.elevenlabs.io/v1/voices
```

### Log Files
- **Main logs**: `video_processing.log`
- **Module logs**: Console output with timestamps
- **Temporary files**: `pieces/trash/` (auto-cleaned)

## Examples

### Complete Asset Workflow
```bash
# 1. Generate AI voiceover for raw video
python main.py --labs -i

# 2. Process complete asset
python main.py --assets=45

# 3. Check results
ls assets/45.mp4
ls frappe/45.mp4
```

### Complete Article Workflow
```bash
# 1. Process individual assets first
python main.py --assets=23
python main.py --assets=45
python main.py --assets=56

# 2. Create article combining assets
python main.py --articles=34,23,45,56

# 3. Check results
ls articles/34.mp4
```

### Batch Processing
```bash
# Process multiple assets
for id in 23 45 56 67; do
    python main.py --assets=$id
done

# Process multiple articles
python main.py --articles=34,23,45,56
python main.py --articles=35,67,89,12
```

## Advanced Features

### Custom Video Settings
Edit module files to customize:
- **Duration**: `DURATION = 2` in `title.py`
- **Resolution**: `WIDTH = 1920, HEIGHT = 1080`
- **Frame Rate**: `FPS = 60`
- **Audio Volume**: `volume=0.07` in `bg.py`

### Backup and Recovery
- Articles are automatically backed up before music addition
- Temporary files are cleaned up after processing
- Failed operations can be retried safely

### Error Recovery
- Scripts skip existing files to avoid reprocessing
- Detailed error messages guide troubleshooting
- Log files preserve operation history

**Need Help?** Check the troubleshooting section or review the log files for detailed error information.
