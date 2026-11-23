# AI Video Metadata Cleaner

## Platform and stack
Windows desktop, Python 3.12+, PySide6, FFmpeg/FFprobe, PyInstaller.

## Product purpose
Offline batch video transcoding. Original files remain untouched. Each row has an editable output basename. Successful outputs can be saved together as ZIP.

## Confirmed constraints
Vietnamese interface; modern minimal desktop layout; dark mode; responsive background processing; cancellation; no overwriting; original resolution and frame timing; H.264/AAC MP4; CRF 18/20/23/26. No watermark-removal or AI-detection-evasion promise.

## Assumptions
Application name confirmed by user: AI Video Metadata Cleaner. Default working directories live in the user's LocalAppData to support non-administrator installs.

## Surface
Operate mode. The user's explicit five-area layout is binding: import queue, editable names, conversion settings, batch progress, results and ZIP.
