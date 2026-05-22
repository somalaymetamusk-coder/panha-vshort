"""core module — settings, scanner, hardware, ffmpeg pipeline, trial."""

from .settings_store import SettingsStore
from .trial import Trial
from .video_scanner import scan_folder, ScanResult, VideoItem
from .hardware import available_encoders, resolve_encoder, ffmpeg_available, Encoder

__all__ = [
    "SettingsStore", "Trial",
    "scan_folder", "ScanResult", "VideoItem",
    "available_encoders", "resolve_encoder", "ffmpeg_available", "Encoder",
]
