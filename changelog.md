## 2025/07/26
### Added
- **Automatic title video cleanup**: Title videos (`_0.mp4`) are now automatically moved to macOS trash after successful asset processing, keeping the `pieces/` directory cleaner
- **Improved CLI output**: Added `--debug` flag for verbose output. Default output is now clean, user-friendly, and concise
- **FFmpeg output suppression**: Verbose FFmpeg output is now hidden by default and only shown with `--debug` flag

### Changed
- **Default output experience**: Console output is now much cleaner and more professional by default
- **Debug mode**: Use `--debug` flag to see all detailed technical output (previous default behavior)

## 2025/05/07
Added an option to use `mpv` for when reveiwing the video from `labs.py` script. For `macOS` only: if you have an env variable `LABS_PLAYER=mpv`, then it uses `mpv` for opening the file.
