"""ffmpeg command builder + execution helpers."""
from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from .hardware import Encoder, resolve_encoder
from .video_scanner import VideoItem


@dataclass
class RenderOptions:
    output_folder: Path
    output_format: str = "mp4"
    overlay_text: str = ""
    show_timer: bool = False
    blur_background: bool = False
    logo_file: Optional[Path] = None
    audio_mode: str = "keep"             # keep | mix | mute | random | mp3
    audio_file: Optional[Path] = None    # used when audio_mode in {mix, mp3}
    audio_pool: Tuple[Path, ...] = ()    # random pool
    encoder: Optional[Encoder] = None    # resolved Encoder (auto-fallback)
    cpu_limit: int = 4
    cut_parts: int = 1                   # >1 means cut-plus
    rename_prefix: str = "video_"
    rename_index: int = 1


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def probe(path: Path) -> dict:
    """Return ffprobe metadata for *path* (best-effort)."""
    if not shutil.which("ffprobe"):
        return {}
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error", "-print_format", "json",
                "-show_format", "-show_streams", str(path),
            ],
            capture_output=True, text=True, timeout=20,
        )
        return json.loads(out.stdout or "{}")
    except Exception:
        return {}


def video_dimensions(path: Path) -> Tuple[int, int]:
    meta = probe(path)
    for s in meta.get("streams", []):
        if s.get("codec_type") == "video":
            return int(s.get("width", 0)), int(s.get("height", 0))
    return 0, 0


def video_duration(path: Path) -> float:
    meta = probe(path)
    try:
        return float(meta.get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# filter graph
# ---------------------------------------------------------------------------

def _escape_drawtext(text: str) -> str:
    # ffmpeg drawtext is picky — escape backslashes, colons and single quotes
    # so the filter parser doesn't choke. We deliberately do NOT escape `%`
    # here: drawtext's text expansion treats a stray `%` as the start of a
    # `%{...}` expansion, and the documented `\%` escape doesn't actually
    # survive expansion in practice. Instead, callers should pass
    # `expansion=none` on the drawtext for user-supplied text — see
    # build_filter_graph.
    return (
        text.replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", r"\'")
    )


def build_filter_graph(opts: RenderOptions, has_logo_input: bool) -> str:
    """Build a -filter_complex graph for the given options.

    Stream layout:
        [0:v]  the source video
        [1:v]  the logo image (only present when has_logo_input is True)
    """
    chain: List[str] = ["[0:v]"]
    if opts.blur_background:
        # vertical 9:16 with blurred background fill
        chain.append(
            "split=2[main][bg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=20:1[bg2];"
            "[main]scale=1080:-2[fg];"
            "[bg2][fg]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        chain.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")

    label_in = "v0"
    chain.append(f"[{label_in}]")
    graph = "".join(chain).replace("[0:v][", "[0:v];[").replace("[v0]", f"[{label_in}]")
    # Cleaner approach: rebuild manually.
    parts: List[str] = []
    cur = "0:v"
    if opts.blur_background:
        parts.append(
            f"[{cur}]split=2[main][bg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=20:1[bg2];"
            "[main]scale=1080:-2[fg];"
            "[bg2][fg]overlay=(W-w)/2:(H-h)/2[vbg]"
        )
        cur = "vbg"
    else:
        parts.append(f"[{cur}]scale=trunc(iw/2)*2:trunc(ih/2)*2[vsc]")
        cur = "vsc"

    if has_logo_input:
        parts.append(f"[{cur}][1:v]overlay=20:20[vl]")
        cur = "vl"

    drawtexts: List[str] = []
    if opts.overlay_text:
        # expansion=none → drawtext treats every char (including `%`) as a
        # literal. Lets users type "Audit Check 100%" without ffmpeg trying
        # to evaluate `%...` as an expression.
        drawtexts.append(
            "drawtext=text='%s':fontcolor=white:fontsize=42:"
            "box=1:boxcolor=black@0.4:boxborderw=10:"
            "expansion=none:"
            "x=(w-text_w)/2:y=h-100" % _escape_drawtext(opts.overlay_text)
        )
    if opts.show_timer:
        # Timer text *is* an expansion expression — keep expansion=normal
        # (the default) so `%{pts\:hms}` resolves to the playback time.
        drawtexts.append(
            "drawtext=text='%{pts\\:hms}':fontcolor=yellow:fontsize=32:"
            "box=1:boxcolor=black@0.4:boxborderw=8:x=20:y=h-60"
        )
    if drawtexts:
        parts.append(f"[{cur}]" + ",".join(drawtexts) + "[vt]")
        cur = "vt"

    parts.append(f"[{cur}]format=yuv420p[vout]")
    return ";".join(parts)


# ---------------------------------------------------------------------------
# command builders
# ---------------------------------------------------------------------------

def _audio_args(opts: RenderOptions, fallback_to_silent: bool = False) -> Tuple[List[str], List[str]]:
    """Return (extra_inputs, mapping_args) for the chosen audio mode."""
    inputs: List[str] = []
    mapping: List[str] = []

    if opts.audio_mode == "mute":
        mapping += ["-an"]
    elif opts.audio_mode == "keep":
        mapping += ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    elif opts.audio_mode in ("mp3", "random") and opts.audio_file:
        inputs += ["-i", str(opts.audio_file)]
        # logo (if present) occupies input slot 1, so audio is the next slot.
        # _build_render_command knows the slot index and patches the map below.
        mapping += ["-map", "AUDIO:a:0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    elif opts.audio_mode == "mix" and opts.audio_file:
        inputs += ["-i", str(opts.audio_file)]
        mapping += [
            "-filter_complex_extra",
            "[0:a][AUDIO:a]amix=inputs=2:duration=shortest[aout]",
            "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
        ]
    else:
        if fallback_to_silent:
            mapping += ["-an"]
        else:
            mapping += ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    return inputs, mapping


def build_render_command(
    src: Path,
    dst: Path,
    opts: RenderOptions,
    *,
    cut_segment: Optional[Tuple[float, float]] = None,
) -> List[str]:
    enc = opts.encoder or resolve_encoder("auto")

    cmd: List[str] = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-threads", str(max(1, int(opts.cpu_limit))),
    ]

    if cut_segment is not None:
        start, dur = cut_segment
        cmd += ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"]

    cmd += ["-i", str(src)]

    has_logo = bool(opts.logo_file and Path(opts.logo_file).is_file())
    if has_logo:
        cmd += ["-i", str(opts.logo_file)]

    audio_slot = 2 if has_logo else 1
    audio_inputs, audio_map = _audio_args(opts)
    # patch the AUDIO placeholder we used above so it points at the real slot
    audio_map = [a.replace("AUDIO", str(audio_slot)) for a in audio_map]
    cmd += audio_inputs

    fg = build_filter_graph(opts, has_logo_input=has_logo)

    # mix mode adds extra audio nodes; pull them out so we can append to -filter_complex
    extra_audio_graph = ""
    cleaned_audio_map: List[str] = []
    skip = False
    for i, tok in enumerate(audio_map):
        if skip:
            skip = False
            continue
        if tok == "-filter_complex_extra":
            extra_audio_graph = audio_map[i + 1]
            skip = True
            continue
        cleaned_audio_map.append(tok)
    audio_map = cleaned_audio_map

    full_graph = fg
    if extra_audio_graph:
        full_graph = fg + ";" + extra_audio_graph

    cmd += ["-filter_complex", full_graph, "-map", "[vout]"]
    cmd += audio_map

    cmd += ["-c:v", enc.ffmpeg_codec, *enc.extra_args, "-pix_fmt", "yuv420p"]
    cmd += ["-movflags", "+faststart"]
    cmd += [str(dst)]
    return cmd


def build_merge_command(
    sources: Sequence[Path],
    dst: Path,
    opts: RenderOptions,
    concat_list_path: Path,
) -> List[str]:
    """Build a concat-demuxer merge command. Caller must write the listing file."""
    enc = opts.encoder or resolve_encoder("auto")
    # ffmpeg concat demuxer with `file '...'` lines: single quotes inside a path
    # must be escaped as `'\''`.
    def _concat_quote(p: Path) -> str:
        return p.as_posix().replace("'", "'\\''")
    concat_list_path.write_text(
        "\n".join(f"file '{_concat_quote(p)}'" for p in sources),
        encoding="utf-8",
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-threads", str(max(1, int(opts.cpu_limit))),
        "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
    ]
    has_logo = bool(opts.logo_file and Path(opts.logo_file).is_file())
    if has_logo:
        cmd += ["-i", str(opts.logo_file)]
    audio_slot = 2 if has_logo else 1
    audio_inputs, audio_map = _audio_args(opts)
    audio_map = [a.replace("AUDIO", str(audio_slot)) for a in audio_map]
    cmd += audio_inputs
    fg = build_filter_graph(opts, has_logo_input=has_logo)

    extra_audio_graph = ""
    cleaned_audio_map: List[str] = []
    skip = False
    for i, tok in enumerate(audio_map):
        if skip:
            skip = False
            continue
        if tok == "-filter_complex_extra":
            extra_audio_graph = audio_map[i + 1]
            skip = True
            continue
        cleaned_audio_map.append(tok)
    audio_map = cleaned_audio_map

    full_graph = fg + (";" + extra_audio_graph if extra_audio_graph else "")
    cmd += ["-filter_complex", full_graph, "-map", "[vout]"]
    cmd += audio_map
    cmd += ["-c:v", enc.ffmpeg_codec, *enc.extra_args, "-pix_fmt", "yuv420p"]
    cmd += ["-movflags", "+faststart", str(dst)]
    return cmd


def humanize_command(cmd: Iterable[str]) -> str:
    return " ".join(shlex.quote(c) for c in cmd)
