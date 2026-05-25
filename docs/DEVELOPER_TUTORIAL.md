# Pnnha V-Short — Developer Tutorial / មេរៀនសម្រាប់អ្នកអភិវឌ្ឍន៍

> A step-by-step guide for building, running, packaging, and shipping
> **Pnnha V-Short** from an empty folder to a deliverable customers can use.
>
> ឯកសារនេះណែនាំជំហានដោយជំហានសម្រាប់បង្កើត ដំណើរការ ខ្ចប់ និងបញ្ជូន
> **Pnnha V-Short** ពីថតទទេមួយ ទៅជាកម្មវិធីដែល End user អាចប្រើប្រាស់បាន។

---

## មាតិកា / Table of contents

0. [Introduction / សេចក្តីផ្តើម](#0-introduction--សេចក្តីផ្តើម)
1. [Prerequisites / លក្ខខណ្ឌតម្រូវ](#1-prerequisites--លក្ខខណ្ឌតម្រូវ)
2. [Project bootstrap / បង្កើតគម្រោងពីដំបូង](#2-project-bootstrap--បង្កើតគម្រោងពីដំបូង)
3. [Module: i18n (English ↔ ខ្មែរ)](#3-module-i18n)
4. [Module: SettingsStore (JSON persistence)](#4-module-settingsstore)
5. [Module: Trial (30-day counter)](#5-module-trial)
6. [Module: Hardware (ffmpeg encoder detection)](#6-module-hardware)
7. [Module: VideoScanner](#7-module-videoscanner)
8. [Module: FFmpegRunner (filter graph + commands)](#8-module-ffmpegrunner)
9. [Module: RenderWorker (QThread + pool)](#9-module-renderworker)
10. [Module: Preview (PIL + OpenCV)](#10-module-preview)
11. [Module: Licensing (Ed25519, offline)](#11-module-licensing)
12. [UI: QSS styles](#12-ui-qss-styles)
13. [UI: VideoTable (model + filter)](#13-ui-videotable)
14. [UI: ActivateDialog](#14-ui-activatedialog)
15. [UI: SettingsDialog](#15-ui-settingsdialog)
16. [UI: MainWindow (wiring everything)](#16-ui-mainwindow)
17. [Admin CLI: `tools/generate_key.py`](#17-admin-cli-toolsgenerate_keypy)
18. [Running in development / ដំណើរការក្នុង Dev mode](#18-running-in-development--ដំណើរការក្នុង-dev-mode)
19. [Packaging a Windows `.exe` with PyInstaller](#19-packaging-a-windows-exe-with-pyinstaller)
20. [Distributing to customers / បញ្ជូនទៅអតិថិជន](#20-distributing-to-customers--បញ្ជូនទៅអតិថិជន)
21. [Troubleshooting / ដោះស្រាយបញ្ហា](#21-troubleshooting--ដោះស្រាយបញ្ហា)
22. [Audit lessons / មេរៀនពី Audit](#22-audit-lessons--មេរៀនពី-audit)

---

## 0. Introduction / សេចក្តីផ្តើម

**Pnnha V-Short** is a desktop application written in **Python 3** with
**PyQt6** that wraps **FFmpeg** to perform batch video processing for short-form
content (TikTok / YouTube Shorts / Reels). It can:

- Merge multiple clips into one
- Cut each clip into N equal parts (**Cut-plus**)
- Rename outputs with a prefix + zero-padded index (**Rename-plus**)
- Overlay a logo image, a custom text, and an HMS timer
- Generate a vertical 9:16 video with a blurred background
- Replace, mix, mute, or randomise the audio track
- Use Nvidia NVENC, AMD AMF, or CPU (x264) for encoding
- Throttle CPU usage and run several jobs in parallel
- Toggle the UI between **English** and **ខ្មែរ**
- Run a 30-day **free trial**, then require an **Ed25519-signed license key**

**ខ្មែរ៖** Pnnha V-Short គឺជា Desktop Application សរសេរដោយ Python 3 + PyQt6
ដែលប្រើ FFmpeg ខាងក្នុង។ វាអាច Merge, Cut, Rename, បន្ថែម Logo/Text/Timer,
ធ្វើ Blur Background, ប្តូរ Audio (Mix/Mute/Random/MP3), ជ្រើសរើស Encoder
(NVENC / AMF / CPU), កំណត់ CPU & Threads, ប្តូរភាសា EN ↔ KH, និងមាន
ប្រព័ន្ធ Free Trial + License Key Ed25519។

---

## 1. Prerequisites / លក្ខខណ្ឌតម្រូវ

| Tool | Minimum version | Why |
|------|-----------------|-----|
| Python | 3.10 | f-strings, `match`, modern typing |
| pip | latest | install dependencies |
| FFmpeg | 4.4 | filter graph + drawtext expansion behaviour we rely on |
| Git | 2.30 | clone, branch, commit |
| (optional) Visual Studio Build Tools 2022 | latest | only if PyQt6 wheels are unavailable on your CPU |

### Installing the toolchain

**Windows**

1. Install Python from <https://www.python.org/downloads/windows/>. Tick **Add
   Python to PATH** in the installer.
2. Install FFmpeg: download a release build from
   <https://www.gyan.dev/ffmpeg/builds/>, extract it (e.g. `C:\ffmpeg`), and
   add `C:\ffmpeg\bin` to your **System PATH**.
3. Install Git from <https://git-scm.com/download/win>.
4. Verify in a fresh PowerShell:
   ```powershell
   python --version
   ffmpeg -version
   git --version
   ```

**Ubuntu / Debian Linux**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg git \
                    fonts-noto-core fonts-dejavu \
                    libxcb-cursor0 libxkbcommon-x11-0
```

The Khmer font is shipped through `fonts-noto-core`. The `libxcb-cursor0` and
`libxkbcommon-x11-0` packages are required by PyQt6 on Linux.

**macOS** (untested but should work)

```bash
brew install python ffmpeg git
brew tap homebrew/cask-fonts && brew install --cask font-noto-sans-khmer
```

---

## 2. Project bootstrap / បង្កើតគម្រោងពីដំបូង

### 2.1 Final folder layout

```
pnnha_vshort/
├── main.py                       # 1. entry point
├── requirements.txt              # 2. pinned Python deps
├── README.md
├── .gitignore                    # excludes data/, keys/, keys-issued/, .venv/
├── app/
│   ├── __init__.py               # APP_NAME, APP_AUTHOR, APP_YEAR, __version__
│   ├── i18n/
│   │   └── __init__.py           # English + Khmer string tables
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ffmpeg_runner.py      # filter graph + command builders
│   │   ├── hardware.py           # encoder detection
│   │   ├── licensing.py          # Ed25519 sign/verify + hardware fingerprint
│   │   ├── preview.py            # first-frame + PIL effects
│   │   ├── render_worker.py      # QThread + ThreadPoolExecutor
│   │   ├── settings_store.py     # data/settings.json
│   │   ├── trial.py              # data/trial.json
│   │   └── video_scanner.py      # scan_folder()
│   └── ui/
│       ├── __init__.py
│       ├── activate_dialog.py    # paste a license key
│       ├── main_window.py        # the V-Short 3.2 layout
│       ├── settings_dialog.py    # tabbed Settings
│       ├── styles.py             # QSS dark-mode stylesheet
│       └── video_table.py        # QAbstractTableModel + filter proxy
├── tools/
│   ├── __init__.py
│   └── generate_key.py           # admin CLI: --init, mint, verify
├── docs/                         # this file lives here
├── keys/                         # admin_private.pem + admin_public.txt (gitignored)
└── data/                         # settings.json / trial.json / license.json (gitignored)
```

### 2.2 Create the project

```bash
mkdir pnnha_vshort && cd pnnha_vshort
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2.3 `requirements.txt`

```text
PyQt6>=6.6
opencv-python-headless>=4.8
Pillow>=10.0
numpy>=1.26
cryptography>=41.0
```

> Use `opencv-python-headless` — not `opencv-python` — to avoid pulling in
> Qt5 underneath. The headless build shares Qt with PyQt6 cleanly.

Install:

```bash
pip install -U pip wheel
pip install -r requirements.txt
```

### 2.4 `app/__init__.py`

```python
"""Pnnha V-Short — application package."""

__version__ = "1.0.0"
APP_NAME = "Pnnha V-Short"
APP_AUTHOR = "HORN LYHENG (Admin-Kh)"
APP_YEAR = 2026
```

### 2.5 `main.py`

The entry point keeps `if __name__ == "__main__"` thin and delegates to a
`main()` function so we can also call it from PyInstaller's launcher later.

```python
"""Entry point — `python main.py`."""
from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from app import APP_NAME
from app.core.licensing import LicenseManager
from app.core.settings_store import SettingsStore
from app.core.trial import Trial
from app.i18n import set_language
from app.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Admin-Kh")

    store = SettingsStore()
    trial = Trial()
    license_manager = LicenseManager(trial=trial)
    set_language(store.get("language", "en"))

    w = MainWindow(store, trial, license_manager)
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

The bootstrap order matters:

1. `QApplication` first (Qt requires it before any widget).
2. Load **settings** (persisted user preferences).
3. Load **trial** (creates the 30-day window on first launch).
4. Build the **LicenseManager** — it reads `data/license.json` if present and
   re-verifies the embedded signature.
5. Apply the saved language **before** instantiating the window so every
   widget picks up the right translation on its first paint.

---

## 3. Module: i18n

**File:** `app/i18n/__init__.py`

### 3.1 Design

Two dictionaries — one for `"en"`, one for `"km"` — keyed by **stable
identifiers** like `start`, `settings_tab_media`, `msg_no_output_folder`. The
public API is:

```python
def tr(key: str, **kwargs) -> str        # translate
def set_language(code: str) -> None      # switch language at runtime
def get_language() -> str                # currently active language
def available_languages() -> list[tuple[str, str]]   # [("en","English"), ("km","ខ្មែរ")]
def subscribe(callback) -> None          # call back when language changes
def unsubscribe(callback) -> None
```

### 3.2 Why a subscribe/unsubscribe API?

When the user toggles the language inside **Settings**, *every* widget that
shows text needs to repaint with the new translation. We solve this by having
each widget call `subscribe(self._retranslate)` in `__init__` and
`unsubscribe(self._retranslate)` in its `closeEvent`. The i18n module fires the
list of callbacks whenever `set_language()` is called.

> **Audit fix:** the **main window** previously forgot to `unsubscribe` in
> `closeEvent`, leaving a dangling reference that prevented garbage collection
> on app shutdown. See [§22](#22-audit-lessons--មេរៀនពី-audit).

### 3.3 Qt mnemonic gotcha — escape `&` as `&&`

Qt interprets `&` in a label as the start of a **keyboard mnemonic** (`Alt+X`).
So `"Audio & Encoder"` would render as `"Audio _Encoder"` with the `&` swallowed
and the `E` underlined. To show a literal `&` you must double it:

```python
"settings_tab_media": "Audio && Encoder",        # English
"settings_tab_media": "សំឡេង && Encoder",          # Khmer
```

### 3.4 Skeleton

```python
"""English + Khmer string tables."""
from __future__ import annotations
from typing import Callable, Dict, List, Tuple

_STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "home": "HOME",
        "settings": "Settings",
        "start": "START",
        "stop": "STOP",
        "reload": "Reload",
        "settings_tab_general": "General",
        "settings_tab_effects": "Effects",
        "settings_tab_media": "Audio && Encoder",
        "msg_no_output_folder": "No output folder set. Pick one in Settings first.",
        # ... lots more ...
    },
    "km": {
        "home": "ទំព័រដើម",
        "settings": "ការកំណត់",
        "start": "ចាប់ផ្ដើម",
        "stop": "ឈប់",
        "reload": "ផ្ទុកឡើងវិញ",
        "settings_tab_general": "ទូទៅ",
        "settings_tab_effects": "បែបផែន",
        "settings_tab_media": "សំឡេង && Encoder",
        "msg_no_output_folder": "មិនបានកំណត់ Folder ខាងក្រៅ — សូមជ្រើសរើសក្នុង Settings ជាមុនសិន។",
        # ... lots more ...
    },
}

_LANG = "en"
_SUBS: List[Callable[[], None]] = []


def tr(key: str, **kwargs) -> str:
    s = _STRINGS.get(_LANG, {}).get(key) or _STRINGS["en"].get(key, key)
    return s.format(**kwargs) if kwargs else s


def set_language(code: str) -> None:
    global _LANG
    if code in _STRINGS:
        _LANG = code
        for cb in list(_SUBS):
            try:
                cb()
            except Exception:
                pass


def get_language() -> str:
    return _LANG


def available_languages() -> List[Tuple[str, str]]:
    return [("en", "English"), ("km", "ខ្មែរ")]


def subscribe(cb: Callable[[], None]) -> None:
    if cb not in _SUBS:
        _SUBS.append(cb)


def unsubscribe(cb: Callable[[], None]) -> None:
    if cb in _SUBS:
        _SUBS.remove(cb)
```

---

## 4. Module: SettingsStore

**File:** `app/core/settings_store.py`

### 4.1 What it does

Wraps a JSON file at `data/settings.json` and presents a **typed dictionary**
with **defaults**. Unknown keys from disk are silently dropped — so changing
the schema is non-fatal for old user installs.

### 4.2 Atomic writes — `tmp + os.replace`

Never write JSON in place. A `Ctrl+C` during `json.dump()` leaves a half-written
file that fails to parse on the next launch, losing the user's settings.

```python
def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)   # POSIX: atomic; Windows: best-effort but durable
```

### 4.3 Public API

| Method | What it does |
|--------|--------------|
| `load()` | called from `__init__`, merges file with defaults |
| `save()` | atomic write of current dictionary |
| `get(key, default=None)` | returns value or default (falls back to `DEFAULTS[key]`) |
| `set(key, value)` | only sets in memory — call `save()` to persist |
| `update(mapping)` | bulk update, ignoring unknown keys |
| `all()` | snapshot copy of the dictionary |

### 4.4 Defaults

The complete default dictionary in `DEFAULTS` doubles as **schema
documentation**. It enumerates every option the app understands:

```python
DEFAULTS = {
    "language": "en",
    "input_folder": "",
    "output_folder": str(Path.home() / "Desktop" / "Done"),
    "audio_folder": "",
    "logo_file": "",
    "overlay_text": "",
    "show_timer": False,
    "blur_background": False,
    "merge": False,
    "cut_plus": False,
    "cut_parts": 2,
    "rename_prefix": "video_",
    "rename_start": 1,
    "audio_mode": "keep",   # keep | mix | mute | random | mp3
    "audio_file": "",
    "encoder": "auto",      # auto | nvenc | amf | cpu
    "cpu_limit": 4,
    "threads_render": 3,
    "output_format": "mp4",
}
```

---

## 5. Module: Trial

**File:** `app/core/trial.py`

Tracks **first launch date** in `data/trial.json` and exposes `days_remaining()`
and `is_expired()`. The trial cannot be reset by deleting the file — well, it
*can*, but that's the user's problem; the License Manager is what blocks
features when the trial dies.

```python
TRIAL_DAYS = 30

class Trial:
    def __init__(self, path: Path = TRIAL_FILE, days: int = TRIAL_DAYS) -> None:
        self.path = path; self.days = days
        self.start_date = date.today()
        self._load_or_init()

    def days_remaining(self) -> int:
        used = (date.today() - self.start_date).days
        return max(0, self.days - used)

    def is_expired(self) -> bool:
        return self.days_remaining() <= 0
```

Same `_atomic_write_text` helper as `SettingsStore` — the audit consolidated
this pattern across all three persistence modules.

---

## 6. Module: Hardware

**File:** `app/core/hardware.py`

Detects which **video encoders** the local FFmpeg build advertises by parsing
the output of `ffmpeg -hide_banner -encoders`. We look for three specific
codec names:

| Encoder | ffmpeg codec | extra args |
|---------|--------------|-----------|
| **NVIDIA NVENC** | `h264_nvenc` | `-preset p4` |
| **AMD AMF** | `h264_amf` | – |
| **CPU x264** | `libx264` | `-preset veryfast` |

```python
@dataclass(frozen=True)
class Encoder:
    key: str                          # auto | nvenc | amf | cpu
    label: str                        # human label
    ffmpeg_codec: str                 # -c:v value
    extra_args: tuple[str, ...] = ()
```

The user picks one of `auto | nvenc | amf | cpu` in Settings; `resolve_encoder`
turns that preference into a concrete `Encoder`:

```python
def resolve_encoder(preference: str) -> Encoder:
    enc = available_encoders()
    by_key = {e.key: e for e in enc}
    if preference == "auto":
        for k in ("nvenc", "amf", "cpu"):
            if k in by_key:
                return by_key[k]
        return CPU_X264
    return by_key.get(preference, CPU_X264)
```

`auto` is intentionally **GPU-first**. CPU is always available (`libx264` is in
every mainstream FFmpeg build).

---

## 7. Module: VideoScanner

**File:** `app/core/video_scanner.py`

Walks a folder **once** and groups files into videos, audios, and an optional
logo image. The result is a **`ScanResult` dataclass** that the UI table reads
directly.

```python
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv"}
AUDIO_EXTS = {".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class VideoItem:
    index: int
    path: Path
    audio: Optional[Path] = None
    logo: Optional[Path] = None
    status: str = "ready"   # ready | queued | running | done | error
    status_detail: str = ""
    progress: int = 0
```

`scan_folder(folder, logo_file, audio_folder)` rules:

1. Videos are collected from `folder`, sorted alphabetically, and indexed
   starting at 1.
2. If `logo_file` is given and exists, it overrides any auto-picked logo.
3. If `audio_folder` is given, only audio files from *there* are collected;
   otherwise audio files inside `folder` are used.
4. If no explicit `logo_file`, the **first** image found in `folder` is used.

---

## 8. Module: FFmpegRunner

**File:** `app/core/ffmpeg_runner.py`

This is the heart of the app. It translates UI options into FFmpeg CLI
filter graphs and full command arrays.

### 8.1 `RenderOptions` dataclass

```python
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
    encoder: Optional[Encoder] = None
    cpu_limit: int = 4
    cut_parts: int = 1                   # >1 means cut-plus
    rename_prefix: str = "video_"
    rename_index: int = 1
```

### 8.2 ffprobe wrappers

```python
def probe(path: Path) -> dict: ...                     # full JSON dict
def video_dimensions(path: Path) -> Tuple[int, int]: ...
def video_duration(path: Path) -> float: ...
```

Cut-plus relies on `video_duration` to know how to slice each clip into N
equal chunks.

### 8.3 Filter graph construction — the **important** part

`build_filter_graph(opts, has_logo_input)` builds a `-filter_complex` string
with **named labels** for every intermediate stream. The final label is always
`[vout]`.

Pipeline:

```
[0:v]                              raw input video
  └─ optional: blur-background (9:16 fill)
        ├─ [main] foreground scaled to 1080x?
        └─ [bg]   blurred copy scaled to 1080×1920
              [bg2][fg]overlay=(W-w)/2:(H-h)/2[vbg]
  └─ else: scale to even pixel size  [vsc]
[vbg|vsc]                          working video stream
  └─ optional: logo overlay  [vl]
[vl|vbg|vsc]
  └─ optional: drawtext for overlay text (expansion=none)
  └─ optional: drawtext for HMS timer (default expansion)
                            [vt]
[vt|vl|vbg|vsc]
  └─ format=yuv420p          [vout]
```

### 8.4 drawtext — the `%` trap (audit fix)

FFmpeg's `drawtext` filter has a built-in **text-expansion** mode. With the
default `expansion=normal`, any `%` character is treated as the **start of an
expression** (`%{pts\:hms}`, `%{n}`, ...). So if the user types
`"Audit Check 100%"`, FFmpeg sees the trailing `%` and tries to parse an
expression, fails, prints `Stray %`, and **drops the entire overlay**.

The documented escape `\%` does not actually survive expansion in practice. The
correct fix is to set **`expansion=none`** on any drawtext whose text is
user-supplied:

```python
if opts.overlay_text:
    drawtexts.append(
        "drawtext=text='%s':fontcolor=white:fontsize=42:"
        "box=1:boxcolor=black@0.4:boxborderw=10:"
        "expansion=none:"                          # ← the fix
        "x=(w-text_w)/2:y=h-100" % _escape_drawtext(opts.overlay_text)
    )
if opts.show_timer:
    drawtexts.append(
        "drawtext=text='%{pts\\:hms}':fontcolor=yellow:fontsize=32:"
        "box=1:boxcolor=black@0.4:boxborderw=8:x=20:y=h-60"
        # NO expansion=none here — we WANT the %{pts\:hms} to evaluate.
    )
```

`_escape_drawtext()` still escapes backslashes, colons, and single quotes
(the three characters that break the filter parser regardless of expansion
mode):

```python
def _escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", r"\'")
    )
```

### 8.5 `build_render_command(src, dst, opts, *, cut_segment=None)`

Returns the full `ffmpeg ...` array. Key invariants:

- Always passes `-hide_banner -loglevel error -stats -y` so we get a quiet,
  parseable output stream.
- Honours `cpu_limit` via `-threads`.
- For cut-plus, `cut_segment=(start, dur)` adds `-ss start -t dur` **before**
  `-i src` so FFmpeg seeks at demuxer level (faster than output seeking).
- Logo, if any, is the second `-i` input; audio (if mode is mp3/random/mix) is
  the next slot. The renderer rewrites the `AUDIO` placeholder used inside
  `_audio_args` to whichever stream slot is correct.
- Output is `-c:v <encoder> -pix_fmt yuv420p -movflags +faststart` — the
  `+faststart` makes the file viewable while still downloading from a server.

### 8.6 `build_merge_command(sources, dst, opts, concat_list_path)`

Uses the **concat demuxer** (lossless, no re-encode of trailing chunks). The
list file contains lines like:

```
file '/abs/path/clip01.mp4'
file '/abs/path/clip02.mp4'
```

**Apostrophe trap (audit fix):** if any path contains a single quote, the
naive serialiser produces broken syntax. The escape is the classic shell
trick:

```python
def _concat_quote(p: Path) -> str:
    return p.as_posix().replace("'", "'\\''")    # close, escape, reopen
```

Verified test: `Path("/tmp/a's clip.mp4")` → `file '/tmp/a'\''s clip.mp4'`.

### 8.7 Audio modes

| mode | semantic | inputs added | mapping |
|------|----------|--------------|---------|
| `keep` | use source audio | – | `-map 0:a? -c:a aac -b:a 192k` |
| `mute` | drop audio | – | `-an` |
| `mp3` | replace with one MP3 | `-i opts.audio_file` | `-map N:a:0 -c:a aac -b:a 192k -shortest` |
| `random` | replace with one MP3 randomly chosen per item | same as `mp3` (resolved per item in RenderWorker) | same |
| `mix` | mix source audio + given MP3 | `-i opts.audio_file` | filter graph: `[0:a][N:a]amix=inputs=2:duration=shortest[aout]`; map `[aout]` |

---

## 9. Module: RenderWorker

**File:** `app/core/render_worker.py`

A **`QThread` subclass** that owns a `ThreadPoolExecutor` so it can run several
FFmpeg processes in parallel without blocking the Qt GUI thread.

### 9.1 Signals

```python
item_started     = pyqtSignal(int)              # row index
item_progress    = pyqtSignal(int, int)         # row, 0..100
item_finished    = pyqtSignal(int, bool, str)   # row, ok, message
overall_progress = pyqtSignal(int)              # 0..100 across queue
finished_all     = pyqtSignal()
log              = pyqtSignal(str)
```

These are how the **main window** repaints the table and progress bars without
ever touching the worker thread directly.

### 9.2 Lifecycle and abort

`stop()` sets a `threading.Event` and `terminate()`s every live `subprocess.Popen`
under a lock. The `_run_one()` reader loop polls the event each iteration and
breaks out cleanly when it's set. After all subprocesses are dead the worker
emits `finished_all`.

### 9.3 Pre-flight checks (audit fix)

Before launching anything the worker rejects three error conditions with a
clear log line and an early `finished_all`:

```python
if not have_ffmpeg():
    self.log.emit("ffmpeg not found"); self.finished_all.emit(); return
if not self.items:
    self.log.emit("no items to render"); self.finished_all.emit(); return

out_dir_str = str(self.opts.output_folder or "").strip()
if not out_dir_str:
    self.log.emit("output folder is not configured"); ...
```

This is the second layer of defence. The first layer is in the **main window**:
clicking `START` with an empty output folder pops a `tr("msg_no_output_folder")`
dialog and never starts the worker.

### 9.4 Cut-plus loop

For `cut_parts > 1`, the worker calls `video_duration(item.path)` once, then
loops `p in range(cut_parts)`:

```python
piece = duration / self.cut_parts
for p in range(self.cut_parts):
    if self._abort.is_set(): ...
    start = p * piece
    dst = out_dir / f"{base_name}_part{p+1:02d}{ext}"
    ok, msg = self._run_one(row, item, dst, opts, segment=(start, piece))
```

### 9.5 Random-audio picking

The audio mode `random` is resolved **per item, not per worker run**, so each
clip in the queue can get a different MP3:

```python
def _audio_choice(self, item):
    if self.opts.audio_mode == "random" and self.opts.audio_pool:
        return Path(random.choice(self.opts.audio_pool))
    if self.opts.audio_mode in ("mix", "mp3") and self.opts.audio_file:
        return Path(self.opts.audio_file)
    ...
```

The chosen path is stuffed into a per-item `RenderOptions` copy so the global
options dataclass isn't mutated across threads.

---

## 10. Module: Preview

**File:** `app/core/preview.py`

Renders a static **preview image** (≈360×640) the user sees on the left side
of the main window. It mirrors every effect the renderer applies, so the user
can iterate on settings without burning a full render.

### 10.1 First frame via OpenCV

```python
def first_frame(path: Path) -> Optional[Image.Image]:
    cap = cv2.VideoCapture(str(path))
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total > 30:
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(30, total // 4))
        ok, frame = cap.read()
        if not ok or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, frame = cap.read()
        if not ok or frame is None: return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    finally:
        cap.release()
```

We deliberately seek past the first 30 frames because many recorders start
with a black slate; sampling at `min(30, total // 4)` gives a representative
frame in nearly every file.

### 10.2 Effects via Pillow

```python
def apply_preview_effects(img, *, blur_background, overlay_text,
                          show_timer, logo_path,
                          target_w=360, target_h=640) -> Image.Image:
    # 1. compose 9:16 canvas (with blur background or fitted letterbox)
    # 2. paste logo at (10, 10)
    # 3. draw overlay_text near the bottom inside a translucent box
    # 4. draw "00:00:01" timer in the bottom-left
```

### 10.3 Font fallback (audit fix)

Pillow ≥ 10 added a `size=` argument to `ImageFont.load_default()`. On older
Pillows the call would crash with `TypeError`. The compatible loader:

```python
def _try_load_font(size: int):
    for c in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, size)
            except Exception: continue
    try:    return ImageFont.load_default(size=size)
    except TypeError: return ImageFont.load_default()
```

`_font_height()` similarly handles the difference between Pillow's `font.size`
attribute (modern) and the `getbbox()` fallback (older).

### 10.4 `pil_to_qpixmap`

The main window paints a `QLabel.setPixmap(...)`. We convert Pillow ↔ Qt via
RGBA bytes + `QImage(QImage.Format.Format_RGBA8888)` to avoid a dependency on
`PIL.ImageQt`, which is not always packaged with Pillow.

---

## 11. Module: Licensing

**File:** `app/core/licensing.py`

### 11.1 Key format

A license key is a UTF-8 string of three dot-separated parts:

```
PNNHA1.<base64url(payload_json)>.<base64url(ed25519_signature)>
```

The `payload_json` is a sorted-keys JSON object:

```json
{
    "kid": "abcd1234",
    "name": "Customer Name",
    "email": "buyer@example.com",
    "type": "pro",
    "issued_at": "2026-05-22",
    "expires": "2027-05-22",
    "max_machines": 1,
    "features": ["merge","cut_plus", ...]
}
```

The signature is over the **exact bytes** of `payload_json` (we use
`json.dumps(..., sort_keys=True, separators=(",", ":"))` so re-encoding is
deterministic on both sides).

### 11.2 Why Ed25519?

- **32-byte public key** — easy to embed as a base64url string in the source.
- **64-byte signatures** — short keys.
- **Deterministic** — no extra entropy needed at signing time.
- **Offline** — no server. Perfect for desktop apps.

### 11.3 Embedded public key

```python
PUBLIC_KEY_B64URL = "Ywcs-gcEhVLNAXVdKGfngPiJQExWhZ6WgLt-9Hwb9R4"
```

This value is **rewritten on the dev's machine** by
`tools/generate_key.py --init`. The placeholder shipped in source control is
intentionally a known dev key — anyone could mint a key against it, but the
admin's first action is to rotate it.

```python
_PLACEHOLDER_PK = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

def is_placeholder_public_key() -> bool:
    return PUBLIC_KEY_B64URL == _PLACEHOLDER_PK
```

The main window checks this on startup and refuses to validate any license if
the placeholder is in place (so an unbuilt project can't accidentally
"license" everyone).

### 11.4 Hardware fingerprint

```python
def hardware_id() -> str:
    parts = [
        str(uuid.getnode()),           # 48-bit MAC
        socket.gethostname(),
        platform.system(),
        platform.machine(),
    ]
    # Linux: /etc/machine-id is rock-stable across reboots
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            parts.append(Path(p).read_text(encoding="utf-8").strip())
            break
        except Exception:
            continue
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
```

16 hex chars (~64 bits) is plenty of entropy for hardware binding without
shouting the user's raw MAC at them. The hex prefix is also user-friendly to
display in the Activate dialog ("`Hardware ID: 751f5bf4bc7bc12d`").

### 11.5 Verify

```python
def verify_key(key: str, public_key=None) -> LicenseInfo:
    payload, payload_bytes, sig = parse_key(key)
    pk = public_key or _public_key()
    try:
        pk.verify(sig, payload_bytes)
    except InvalidSignature as e:
        raise ValueError("invalid signature") from e
    info = LicenseInfo.from_dict(payload)
    if info.type not in LICENSE_TYPES:
        raise ValueError(f"unknown license type: {info.type}")
    return info
```

We deliberately **don't** check expiry inside `verify_key` so callers can
choose to *show* an expired license in the UI as "Expired".

### 11.6 LicenseManager

```python
class LicenseManager:
    def __init__(self, trial=None) -> None:
        self.path = LICENSE_FILE
        self.trial = trial or Trial()
        self.info: Optional[LicenseInfo] = None
        ...
        self.load()

    def activate(self, key: str) -> ActivationResult: ...
    def deactivate(self) -> None: ...
    def display_status(self) -> Dict[str, str]: ...
    def can_render(self) -> bool: ...
```

`activate()` runs `verify_key`, then atomically writes `data/license.json`
with `{ "key": ..., "payload": ..., "hardware_id": ..., "activated_at": ... }`.

`can_render()` returns `True` if either:

- A valid, non-expired license is loaded, or
- The trial hasn't expired yet.

`display_status()` produces a tuple `(state, label)` like
`("licensed", "Sok Dara • Pro")` or `("trial", "Trial: 27 Day")` that the top
bar badge consumes verbatim.

---

## 12. UI: QSS styles

**File:** `app/ui/styles.py`

A single multi-line `QSS = """..."""` string applied to the main window via
`self.setStyleSheet(QSS)`. It defines the dark colour palette, button shapes,
table row colours, table header look, scrollbar slimming, and the green
**START** button.

Putting all styles in one place makes it easy to retheme the entire app.

---

## 13. UI: VideoTable

**File:** `app/ui/video_table.py`

### 13.1 `VideoTableModel`

A `QAbstractTableModel` over a `list[VideoItem]`. Five columns:
`#`, `Name`, `Audio`, `Logo`, `Status`. The cell colour for the Status column
comes from `_STATUS_COLORS`:

```python
_STATUS_COLORS = {
    "ready":   QColor("#e7ecf3"),
    "queued":  QColor("#cbd5e1"),
    "running": QColor("#38bdf8"),
    "done":    QColor("#22c55e"),
    "error":   QColor("#ef4444"),
}
```

`set_status(row, status, detail)` emits `dataChanged` for the status cell only
— this keeps repaints cheap when 100+ items are queued.

### 13.2 `VideoFilterProxy`

A `QSortFilterProxyModel` that combines:

- a **name filter** (case-insensitive substring on the `Name` column), and
- a **status filter** (`all`, `ready`, `running`, `done`, `error`).

The two combobox + textbox in the main window each control one of those
filters.

---

## 14. UI: ActivateDialog

**File:** `app/ui/activate_dialog.py`

A `QDialog` with a `QPlainTextEdit` for the key, the **current** activation
status, the user's hardware ID (selectable for copy-paste), and two buttons:
`Activate` and `Deactivate`.

`_on_activate` calls `manager.activate(key)`, then shows either:

- `lic_activated_ok` ("Activated for {name}.") on success, or
- `lic_activate_failed` ("Activation failed: {err}") with the underlying
  `ValueError` message ("invalid signature", "malformed license key", ...).

---

## 15. UI: SettingsDialog

**File:** `app/ui/settings_dialog.py`

A `QTabWidget` with three tabs:

| Tab key | Tab title (EN) | Tab title (KH) | Contents |
|---------|----------------|----------------|----------|
| `settings_tab_general` | General | ទូទៅ | language, input/output/audio folders, logo file |
| `settings_tab_effects` | Effects | បែបផែន | overlay text, timer, blur, merge, cut-plus, rename prefix/start |
| `settings_tab_media`   | Audio && Encoder | សំឡេង && Encoder | audio mode + file, encoder, cpu_limit, threads_render |

The **audio mode combobox** uses `userData=code` so the persisted value is
the stable key (`keep`/`mix`/`mute`/`random`/`mp3`) regardless of language.
The **encoder combobox** is populated by `available_encoders()` so users only
see encoders that actually exist in their FFmpeg build.

Saving:

```python
def accept(self):
    self.store.update({...all controls...})
    self.store.save()
    set_language(self.lang_combo.currentData())   # fires i18n subscribers
    super().accept()
```

---

## 16. UI: MainWindow

**File:** `app/ui/main_window.py`

This is the largest file (≈580 lines) and the glue everything else hangs off.

### 16.1 Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ HOME   Settings   Help                            ⏱ Trial: 30 Day │  ← top bar
├──────────────┬───────────────────────────────────────────────────┤
│              │ Detected Videos : 2                Output: …      │
│              │ [filter name…]                  [status filter ▾] │
│   live       │ ┌───┬───────────┬───────┬──────┬──────────────┐   │
│   preview    │ │ # │ Name      │ Audio │ Logo │ Status       │   │
│   (PIL→Qt)   │ ├───┼───────────┼───────┼──────┼──────────────┤   │
│              │ │ 1 │ clip01.mp4│ -     │ -    │ Ready        │   │
│              │ │ 2 │ clip02.mp4│ -     │ -    │ Ready        │   │
│              │ └───┴───────────┴───────┴──────┴──────────────┘   │
│              │ 2 video(s), 0 audio file(s), 0 logo file          │
│              │ ────────────────────────  per-item progress  ──── │
│              │ ────────────────────────  overall progress    ─── │
│              │ Threads Render [2 ▾]              [START][STOP][Reload] │
├──────────────┴───────────────────────────────────────────────────┤
│           © All rights reserved by HORN LYHENG (Admin-Kh) 2026   │  ← footer
└──────────────────────────────────────────────────────────────────┘
```

### 16.2 Wiring

The main window owns:

- `self.store` — `SettingsStore` instance
- `self.trial` — `Trial` instance
- `self.license_manager` — `LicenseManager`
- `self.scan` — last `ScanResult`
- `self.worker` — optional `RenderWorker`

It subscribes to i18n changes (`subscribe(self._retranslate)`), reads the
saved language, and calls `self._retranslate()` on every label after the
language switches.

### 16.3 `_on_start_clicked` (audit fix)

The Start button validates **before** instantiating the worker:

```python
def _on_start_clicked(self):
    if not self.license_manager.can_render():
        QMessageBox.warning(self, ..., tr("msg_trial_expired"))
        return

    out = self.store.get("output_folder", "").strip()
    if not out:
        QMessageBox.warning(self, ..., tr("msg_no_output_folder"))
        return

    # ... build RenderOptions, instantiate RenderWorker, connect signals
    self.worker = RenderWorker(items=..., opts=..., threads_render=..., ...)
    self.worker.item_started.connect(self._on_item_started)
    self.worker.item_progress.connect(self._on_item_progress)
    self.worker.item_finished.connect(self._on_item_finished)
    self.worker.overall_progress.connect(self._on_overall_progress)
    self.worker.finished_all.connect(self._on_finished_all)
    self.worker.log.connect(self._append_log)
    self.worker.start()
```

### 16.4 `closeEvent` (audit fix — the big one)

When you close the window while a render is running, the worker thread is
still alive. Its last `finished_all` would arrive at `_on_finished_all`,
which calls `QMessageBox.information(...)` — on a window that is in the
middle of being destroyed. The result is a stray **"All jobs finished"**
popup appearing in the void.

The fix is to **disconnect every worker signal before stopping the worker**:

```python
def closeEvent(self, event) -> None:
    try:
        unsubscribe(self._retranslate)
    except Exception:
        pass
    if self.worker and self.worker.isRunning():
        for sig in (
            self.worker.finished_all,
            self.worker.item_started,
            self.worker.item_progress,
            self.worker.item_finished,
            self.worker.overall_progress,
            self.worker.log,
        ):
            try:
                sig.disconnect()
            except (TypeError, RuntimeError):
                pass
        self.worker.stop()
        self.worker.wait(5000)          # bounded — don't freeze the UI
    super().closeEvent(event)
```

The signal-disconnect loop is wrapped in `try/except (TypeError, RuntimeError)`
because PyQt6 raises both depending on whether the signal had any slots in
the first place.

---

## 17. Admin CLI: `tools/generate_key.py`

The CLI has three subcommands:

| Command | Purpose |
|---------|---------|
| `--init` | (one-time) generate the keypair, write `keys/admin_private.pem`, `keys/admin_public.txt`, and patch `app/core/licensing.py`'s `PUBLIC_KEY_B64URL` to the new value. |
| `mint`   | sign a payload with the private key and print the resulting license. Also writes a copy to `keys-issued/<kid>.txt` and appends a JSONL audit row. |
| `verify` | parse a key, check the signature against the embedded public key, and print the decoded payload as JSON. Useful for sanity checks. |

### 17.1 First-time setup

```bash
python tools/generate_key.py --init
git add app/core/licensing.py keys/admin_public.txt
git commit -m "Rotate license signing keypair"
```

> **Never** commit `keys/admin_private.pem` — `.gitignore` already excludes it.
> If you ever lose it, every key you ever minted becomes unverifiable and you
> must re-init + re-issue to every customer.

### 17.2 Minting

```bash
# perpetual Pro license
python tools/generate_key.py mint \
    --name "Sok Dara" --email dara@example.com \
    --type pro --max-machines 3

# 1-year Standard license
python tools/generate_key.py mint \
    --name "Lim Chenda" --email chenda@example.com \
    --type standard --expires 2027-05-22 --max-machines 1

# feature-restricted license (no GPU, no mix audio)
python tools/generate_key.py mint \
    --name "Test" --email t@example.com --type standard \
    --feature merge --feature cut_plus --feature text
```

### 17.3 Verifying (three input modes — audit fix)

```bash
# 1. positional argument
python tools/generate_key.py verify "PNNHA1.eyJ..."

# 2. stdin (great for piping out of curl / cat)
echo "PNNHA1.eyJ..." | python tools/generate_key.py verify -

# 3. path to a file containing the key
python tools/generate_key.py verify /path/to/key.txt
```

All three modes exit `0` on success and print the decoded JSON. Exit `1` for a
valid format with a bad signature; exit `2` for a malformed input.

---

## 18. Running in development / ដំណើរការក្នុង Dev mode

```bash
# clone
git clone https://github.com/somalaymetamusk-coder/panha-vshort.git
cd panha-vshort

# virtualenv
python -m venv .venv
source .venv/bin/activate    # Windows: .\.venv\Scripts\activate

# deps
pip install -r requirements.txt

# (admin only) rotate the signing keypair
python tools/generate_key.py --init

# run
python main.py
```

Typical dev loop:

1. Edit a module (e.g. `app/ui/main_window.py`).
2. `Ctrl+C` the running app (or close the window).
3. Re-run `python main.py`.

For **debugging the FFmpeg pipeline** specifically, set
`logging.basicConfig(level=logging.DEBUG)` in `main.py`, or just run with
`PYTHONUNBUFFERED=1 python main.py | tee app.log` and inspect the streamed
FFmpeg stderr — every spawned command is logged verbatim via the worker's
`log` signal.

---

## 19. Packaging a Windows `.exe` with PyInstaller

### 19.1 Install

```powershell
pip install pyinstaller
```

### 19.2 Spec file (`pnnha_vshort.spec`)

```python
# pnnha_vshort.spec — one-file Windows build
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/i18n', 'app/i18n'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'cv2', 'PIL.ImageDraw', 'PIL.ImageFilter', 'PIL.ImageFont',
        'cryptography.hazmat.primitives.asymmetric.ed25519',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='PnnhaVShort',
    debug=False, bootloader_ignore_signals=False, strip=False,
    upx=True, runtime_tmpdir=None, console=False,
    icon='assets/app.ico',
)
```

### 19.3 Build

```powershell
pyinstaller --clean pnnha_vshort.spec
dir dist\
# dist\PnnhaVShort.exe ← deliverable
```

### 19.4 Bundle FFmpeg

PyInstaller bundles only Python code. FFmpeg is a **separate executable**, so:

**Option A: require user to install ffmpeg + PATH** (smaller download, the
README explains it). The app already calls `shutil.which("ffmpeg")` and shows
a clear error if not found.

**Option B: ship ffmpeg alongside `PnnhaVShort.exe`** (larger but turnkey):

1. Download ffmpeg `essentials_build` from gyan.dev.
2. Copy `ffmpeg.exe` and `ffprobe.exe` into `dist\`.
3. Patch `app/core/hardware.py` so `ffmpeg_available()` and
   `shutil.which("ffmpeg")` look next to `sys.executable` first:

   ```python
   def _exe_dir() -> Path:
       return Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

   def ffmpeg_available() -> bool:
       local = _exe_dir() / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
       if local.is_file(): return True
       return shutil.which("ffmpeg") is not None
   ```

### 19.5 Custom icon

Drop a `.ico` (256×256, multi-resolution) at `assets/app.ico` and reference it
in the spec (`icon='assets/app.ico'`). Use ImageMagick if you only have a
PNG:

```bash
convert app.png -define icon:auto-resize=16,32,48,64,128,256 app.ico
```

---

## 20. Distributing to customers / បញ្ជូនទៅអតិថិជន

### 20.1 What the customer receives

A single ZIP containing:

1. `PnnhaVShort.exe` (and `ffmpeg.exe` / `ffprobe.exe` if you went with Option B)
2. `README-customer.md` — how to install, where the data folder lives, how to
   request a license, how to renew.
3. (Optional) a sample license key file `LICENSE.txt`.

### 20.2 Selling and delivering keys

1. Customer pays / agrees to terms.
2. You run:
   ```bash
   python tools/generate_key.py mint \
       --name "Sok Dara" --email dara@example.com \
       --type pro --expires 2027-05-22 --max-machines 2
   ```
3. Copy the resulting `PNNHA1.eyJ…` string.
4. Send it to the customer (email, Telegram, etc.).
5. They paste it into **Activate License**. Done.

The `keys-issued/log.jsonl` file is your record. Each line:

```json
{"issued_at":"2026-05-25T09:00:00","kid":"a1b2c3d4","name":"Sok Dara","email":"dara@example.com","type":"pro","expires":"2027-05-22","max_machines":2}
```

### 20.3 Renewals

Mint a fresh key with a new `--expires`. The customer pastes it; the new key
overwrites `data/license.json` and the badge updates.

### 20.4 Refunds / revocation

The system is offline so you can't *revoke* a key once issued. Options:

- Use **short expiries** + reissue (annual cycle).
- For abuse, ask the customer to send their **Hardware ID**, then mint a key
  bound to a different hardware ID (the customer-side fingerprint).

---

## 21. Troubleshooting / ដោះស្រាយបញ្ហា

| Symptom | Cause | Fix |
|---------|-------|-----|
| App boots blank window | FFmpeg not on PATH | install ffmpeg, restart shell |
| Render fails with "ffmpeg not found" | same | same |
| Overlay text missing in output | Old build before `expansion=none` fix | pull latest main, or set `expansion=none` |
| Output has no audio | `audio_mode=keep` but source has none | switch to `mute` or `mp3` |
| "ffmpeg exit 1" with NVENC | no Nvidia driver on this host | switch encoder to `cpu` |
| Khmer text shows squares | Noto Sans Khmer missing | install `fonts-noto-core` (Linux) or the Khmer language pack (Windows) |
| `data/settings.json` becomes invalid after a crash | (would have happened pre-audit) | atomic write is now in place; if you still see it, delete the `.tmp` file next to it |
| Activation says "invalid signature" | The build's `PUBLIC_KEY_B64URL` doesn't match the private key that signed | run `tools/generate_key.py --init` once on the build machine, then ship that build |
| Closing window mid-render hangs Python | (pre-audit) | latest `main_window.py` disconnects signals and bounds `worker.wait(5000)` |
| "Stray %" in FFmpeg log | (pre-audit) | use `expansion=none` on user-supplied drawtext |

---

## 22. Audit lessons / មេរៀនពី Audit

The PRs `#1` (licensing) and `#2` (audit) consolidate the most important
lessons learned while making the app shippable:

1. **Atomic writes** — every persisted JSON file goes through
   `tmp + os.replace`. A `Ctrl+C` mid-save no longer corrupts the user's
   settings/trial/license.
2. **`expansion=none` for user-supplied drawtext** — never let user content
   into a filter that interprets `%`. Reserve expanded drawtext for built-in
   expressions only (timer's `%{pts\:hms}`).
3. **Concat-demuxer single-quote escape** — `'\''` for any apostrophe in a
   path, because the demuxer's mini-shell parser will choke otherwise.
4. **Pre-flight validation in the worker AND the UI** — the UI gives a friendly
   dialog (`msg_no_output_folder`), the worker also rejects the bad state in
   case some other caller bypasses the UI.
5. **Signal disconnect before thread stop** — Qt signals from a dying worker
   are evaluated on the main thread *after* the receiver has begun
   destruction. Disconnect first, then stop.
6. **`unsubscribe()` on close** — without it, the i18n subscriber list holds a
   reference to the destroyed window, preventing GC and creating a slow leak
   if the app re-opens MainWindow during its lifetime.
7. **Pillow API compatibility** — use `try/except TypeError` for the
   `load_default(size=...)` change between Pillow 9 and 10.
8. **Placeholder public key guard** — `is_placeholder_public_key()` makes it
   impossible to ship an unrotated dev key and accidentally license everyone.
9. **CLI `verify` accepts stdin and a file path** — scripts and pipelines now
   work without needing to embed the entire key on one shell line.
10. **Qt mnemonic `&` escape** — every label containing `&` must be doubled to
    `&&` or Qt will eat it.

---

## License / ច្បាប់​សិទ្ធ

The application itself is © HORN LYHENG (Admin-Kh) 2026.
This developer tutorial document is part of the same repository and shares
its license.

— សូមរីករាយជាមួយការអភិវឌ្ឍ! Happy hacking!
