"""Hardware/encoder detection — figures out which ffmpeg encoder to use."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Encoder:
    key: str          # auto | nvenc | amf | cpu
    label: str
    ffmpeg_codec: str  # value passed to -c:v
    extra_args: tuple[str, ...] = ()


CPU_X264 = Encoder("cpu", "CPU (x264)", "libx264", ("-preset", "veryfast"))
NVENC = Encoder("nvenc", "Nvidia (NVENC)", "h264_nvenc", ("-preset", "p4"))
AMF = Encoder("amf", "AMD (AMF)", "h264_amf", ())


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _list_encoders() -> List[str]:
    if not ffmpeg_available():
        return []
    try:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return []
    names: List[str] = []
    for line in out.stdout.splitlines():
        parts = line.strip().split()
        # encoder rows look like:  " V..... libx264 ..."
        if len(parts) >= 2 and parts[0].startswith("V"):
            names.append(parts[1])
    return names


def available_encoders() -> List[Encoder]:
    names = set(_list_encoders())
    result: List[Encoder] = []
    if NVENC.ffmpeg_codec in names:
        result.append(NVENC)
    if AMF.ffmpeg_codec in names:
        result.append(AMF)
    # CPU is always available (libx264 is in nearly every ffmpeg build)
    result.append(CPU_X264)
    return result


def resolve_encoder(preference: str) -> Encoder:
    """Resolve a user preference (auto|nvenc|amf|cpu) to a concrete Encoder."""
    enc = available_encoders()
    by_key = {e.key: e for e in enc}
    if preference == "auto":
        # prefer GPU when available
        for k in ("nvenc", "amf", "cpu"):
            if k in by_key:
                return by_key[k]
        return CPU_X264
    return by_key.get(preference, CPU_X264)
