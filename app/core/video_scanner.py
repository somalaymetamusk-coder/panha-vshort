"""Scan a folder for video / audio / logo files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv"}
AUDIO_EXTS = {".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class VideoItem:
    index: int
    path: Path
    audio: Optional[Path] = None
    logo: Optional[Path] = None
    status: str = "ready"          # ready | queued | running | done | error
    status_detail: str = ""
    progress: int = 0              # 0..100

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class ScanResult:
    videos: List[VideoItem] = field(default_factory=list)
    audios: List[Path] = field(default_factory=list)
    logo: Optional[Path] = None

    @property
    def video_count(self) -> int:
        return len(self.videos)

    @property
    def audio_count(self) -> int:
        return len(self.audios)

    @property
    def logo_count(self) -> int:
        return 1 if self.logo else 0


def scan_folder(folder: str | Path, logo_file: str = "", audio_folder: str = "") -> ScanResult:
    """Walk *folder* once and return a ScanResult.

    * If a ``logo_file`` path is supplied (and exists) it is used directly.
    * If ``audio_folder`` is supplied (and exists) MP3-style files are collected
      from there. Otherwise audio files discovered inside *folder* are used.
    """
    result = ScanResult()
    root = Path(folder) if folder else None
    if root and root.is_dir():
        items = sorted(p for p in root.iterdir() if p.is_file())
        idx = 1
        for p in items:
            ext = p.suffix.lower()
            if ext in VIDEO_EXTS:
                result.videos.append(VideoItem(index=idx, path=p))
                idx += 1
            elif ext in AUDIO_EXTS and not audio_folder:
                result.audios.append(p)
            elif ext in IMAGE_EXTS and not logo_file and result.logo is None:
                # auto-pick first image as logo if none specified
                result.logo = p

    if audio_folder:
        ap = Path(audio_folder)
        if ap.is_dir():
            for p in sorted(ap.iterdir()):
                if p.is_file() and p.suffix.lower() in AUDIO_EXTS:
                    result.audios.append(p)

    if logo_file:
        lp = Path(logo_file)
        if lp.is_file():
            result.logo = lp

    return result
