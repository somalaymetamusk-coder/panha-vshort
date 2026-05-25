# Pnnha V-Short — Developer Tutorial / មេរៀនសម្រាប់អ្នកអភិវឌ្ឍន៍

> A complete, step-by-step tutorial for working on this project end-to-end —
> from a fresh `git clone` all the way through running, customising, testing,
> packaging, distributing, and supporting it for paying end users.
>
> If you only have 5 minutes, jump to **[§2 Quick Start](#2-quick-start)**.

---

## សេចក្តីផ្តើមជាខ្មែរ (Khmer summary)

ឯកសារនេះជាមេរៀនពេញលេញសម្រាប់ **អ្នកអភិវឌ្ឍន៍ (Developer)** ដើម្បីដំណើរការ
គម្រោង **Pnnha V-Short** នេះ ចាប់ពីការដំឡើងលើ machine ដំបូងរហូតដល់
ការប្រគល់ឲ្យ End-user ប្រើប្រាស់។

មាតិកាសំខាន់ៗ៖

- ការដំឡើង Python 3.10+, FFmpeg, និង PyQt6 លើ Windows / Linux / macOS
- រចនាសម្ព័ន្ធ Project: `app/core/`, `app/ui/`, `app/i18n/`, `tools/`, `data/`
- ការសរសេរ `main.py` និងលំដាប់ bootstrap (QApplication → Settings →
  Trial → License → MainWindow)
- ការប្តូរភាសា **English ↔ ខ្មែរ** ដោយ live (subscribe / unsubscribe)
- ការសរសេរ **FFmpeg filter graph** សម្រាប់ Blur background, Logo overlay,
  Text overlay, Timer overlay
- ការដោះស្រាយបញ្ហា drawtext `%` (expansion=none) និង concat path
  apostrophe escaping
- ការប្រើ **QThread + ThreadPoolExecutor** សម្រាប់ render parallel ដោយ
  មិន freeze UI
- ការសរសេរ Live Preview ដោយ OpenCV + Pillow
- ប្រព័ន្ធ License **Ed25519-signed offline** + Hardware fingerprint
- ការខ្ចប់ជា `.exe` ដោយ **PyInstaller** សម្រាប់ Windows
- ការសង់ key, លក់, បន្តរសុពលភាព និង​បញ្ហាប្រឈម​នៅ End user

ផ្នែកបច្ចេកទេសត្រូវបានសរសេរជា **English** ដោយចេតនា ដើម្បីស៊ីគ្នាជាមួយ
ឯកសារផ្លូវការរបស់ Python / PyQt6 / FFmpeg ហើយដើម្បីឱ្យអ្នកអភិវឌ្ឍន៍
search ឯកសារខាងក្រៅងាយ។ បើចង់សរសេរជាខ្មែរ ១០០% សូមប្រាប់។

---

## មាតិកា / Table of contents

1. [Project overview / ទិដ្ឋភាពទូទៅ](#1-project-overview)
2. [Quick start](#2-quick-start)
3. [Architecture overview / រចនាសម្ព័ន្ធ](#3-architecture-overview)
4. [Folder structure](#4-folder-structure)
5. [Lesson 1 — `app/__init__.py` and `main.py`](#5-lesson-1-app__init__py-and-mainpy)
6. [Lesson 2 — i18n (English ↔ ខ្មែរ)](#6-lesson-2-i18n)
7. [Lesson 3 — SettingsStore (JSON persistence)](#7-lesson-3-settingsstore)
8. [Lesson 4 — Trial (30-day counter)](#8-lesson-4-trial)
9. [Lesson 5 — Hardware (encoder detection)](#9-lesson-5-hardware)
10. [Lesson 6 — VideoScanner](#10-lesson-6-videoscanner)
11. [Lesson 7 — FFmpegRunner (filter graph + commands)](#11-lesson-7-ffmpegrunner)
12. [Lesson 8 — RenderWorker (QThread + ThreadPoolExecutor)](#12-lesson-8-renderworker)
13. [Lesson 9 — Preview (OpenCV + Pillow)](#13-lesson-9-preview)
14. [Lesson 10 — Licensing (Ed25519, offline-verifiable)](#14-lesson-10-licensing)
15. [Lesson 11 — UI: QSS styles](#15-lesson-11-ui-qss-styles)
16. [Lesson 12 — UI: VideoTable (model + filter proxy)](#16-lesson-12-ui-videotable)
17. [Lesson 13 — UI: ActivateDialog](#17-lesson-13-ui-activatedialog)
18. [Lesson 14 — UI: SettingsDialog](#18-lesson-14-ui-settingsdialog)
19. [Lesson 15 — UI: MainWindow (wiring everything)](#19-lesson-15-ui-mainwindow)
20. [Lesson 16 — Admin CLI (`tools/generate_key.py`)](#20-lesson-16-admin-cli)
21. [Development workflow](#21-development-workflow)
22. [Packaging a Windows `.exe` with PyInstaller](#22-packaging-a-windows-exe-with-pyinstaller)
23. [Distributing to customers / បញ្ជូនទៅអតិថិជន](#23-distributing-to-customers)
24. [Common extension tasks / កិច្ចការពង្រីក](#24-common-extension-tasks)
25. [Troubleshooting / ដោះស្រាយបញ្ហា](#25-troubleshooting)
26. [Audit lessons / មេរៀនពី Audit](#26-audit-lessons)
27. [Glossary KH ↔ EN](#27-glossary-kh-en)
28. [Appendix — file & command reference](#28-appendix-file-command-reference)

---

## 1. Project overview

**Pnnha V-Short** is a **PyQt6 desktop application** that wraps **FFmpeg** to
perform **batch video processing** for short-form content (TikTok, YouTube
Shorts, Reels). The data flow is:

```
Input folder ──► VideoScanner ──► VideoTableModel ──► RenderWorker ──► ffmpeg subprocess(es)
        │                                                  │
        ▼                                                  ▼
   Live Preview (PIL)                              Output folder
                                                          │
                                                          ▼
                                                  video_0001.mp4, video_0002.mp4, ...
```

### Functional scope / មុខងារ

| Area | What it does | Khmer |
|------|--------------|-------|
| **Merge** | Concatenate every input clip into a single output file | បូកវីដេអូទាំងអស់ |
| **Cut-plus** | Split each clip into N equal parts | កាត់ជាផ្នែកស្មើៗ |
| **Rename-plus** | Bulk-rename outputs with `prefix + 0001, 0002, ...` | ប្តូរឈ្មោះស្វ័យប្រវត្តិ |
| **Logo overlay** | Paste an image at top-left of every output | បន្ថែម Logo |
| **Text overlay** | Render user-supplied text near the bottom | បន្ថែម Text |
| **Timer overlay** | Live `HH:MM:SS.mmm` counter at the bottom-left | បន្ថែម Timer |
| **Blur background** | Make a vertical 9:16 video with a blurred fill | ធ្វើ Blur ផ្ទៃខាងក្រោយ |
| **Audio: Keep** | Pass-through the source's audio track | រក្សាសំឡេងដើម |
| **Audio: Mute** | Drop audio | បិទសំឡេង |
| **Audio: Mix** | Add an MP3 on top of the source audio | លាយសំឡេង |
| **Audio: Random** | Pick a random MP3 per clip from a pool | ជ្រើសសំឡេងដោយចៃដន្យ |
| **Audio: MP3** | Replace audio with a chosen MP3 | ប្តូរសំឡេងជាក់លាក់ |
| **Encoder: Auto** | Pick the best available (GPU first, then CPU) | ស្វ័យប្រវត្តិ |
| **Encoder: NVENC** | Use Nvidia GPU H.264 encoder | Nvidia GPU |
| **Encoder: AMF** | Use AMD GPU H.264 encoder | AMD GPU |
| **Encoder: CPU** | Use libx264 (always available) | CPU x264 |
| **CPU limit** | Cap the number of FFmpeg threads per job | កំណត់ CPU per job |
| **Threads Render** | Number of FFmpeg processes running in parallel | ដំណើរការក្នុងពេលតែមួយ |
| **Trial** | 30-day free use, then needs activation | សាកល្បង ៣០ ថ្ងៃ |
| **License** | Ed25519-signed, offline-verified key | License Key ផ្ទាល់ |

### Tech stack / បច្ចេកវិទ្យា

| Layer | Technology | Version | Why |
|-------|-----------|---------|-----|
| Language | Python | ≥ 3.10 | f-strings, modern typing |
| GUI | PyQt6 | ≥ 6.6 | mature, cross-platform, native look |
| Video pipeline | FFmpeg (subprocess) | ≥ 4.4 | drawtext expansion behaviour we rely on |
| Frame extraction | OpenCV (headless) | ≥ 4.8 | fast `VideoCapture` for preview |
| Image effects | Pillow (PIL) | ≥ 10.0 | PIL `ImageDraw`, `ImageFilter` |
| Cryptography | `cryptography` | ≥ 41.0 | Ed25519 sign / verify |
| Persistence | plain JSON | – | atomic `tmp + os.replace` writes |

> **Why no database?** The app is single-user, single-machine. JSON files in
> `data/` are simpler and survive uninstalls / reinstalls cleanly. Three
> files total: `settings.json`, `trial.json`, `license.json`.

---

## 2. Quick start

### 2.1 Prerequisites

| Tool | Version | Install hint |
|------|---------|--------------|
| Python | ≥ 3.10 | <https://www.python.org/downloads/> (tick "Add to PATH" on Windows) |
| FFmpeg | ≥ 4.4 | Windows: <https://www.gyan.dev/ffmpeg/builds/> · Ubuntu: `apt install ffmpeg` · macOS: `brew install ffmpeg` |
| Git | ≥ 2.30 | <https://git-scm.com/downloads> |
| Khmer font (UI rendering) | latest | Ubuntu: `apt install fonts-noto-core` · Windows: Settings → Language → add Khmer pack |

Verify everything is on your PATH:

```bash
python --version       # Python 3.10.x or higher
ffmpeg -version        # ffmpeg version 4.4 or higher
git --version
```

### 2.2 Clone & install

```bash
git clone https://github.com/somalaymetamusk-coder/panha-vshort.git
cd panha-vshort

# create a virtual environment (recommended)
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# install Python deps
pip install --upgrade pip wheel
pip install -r requirements.txt
```

### 2.3 (Admin only) rotate the signing keypair

The repo ships with a **development** public key embedded in
`app/core/licensing.py`. Anyone could mint a key for it, which is fine for
local testing but unacceptable for shipping. Rotate it on your machine:

```bash
python tools/generate_key.py --init
git add app/core/licensing.py keys/admin_public.txt
git commit -m "Rotate license signing keypair"
```

> `keys/admin_private.pem` is **never** committed (gitignored). If you lose
> it, every key you ever minted becomes unverifiable.

### 2.4 First launch

```bash
python main.py
```

You should see the V-Short 3.2-style window. The first launch creates:

- `data/settings.json` — empty defaults
- `data/trial.json` — 30-day clock starts now

Open **Settings**, set:

- **Input folder** — a folder containing some `.mp4` files
- **Output folder** — anywhere writable (default: `~/Desktop/Done`)
- **Overlay text**, **Timer**, **Blur background** — optional

Close Settings → click **START**. Output files appear as `video_0001.mp4`,
`video_0002.mp4`, …

### 2.5 First license test

```bash
# mint a Pro key for yourself
python tools/generate_key.py mint \
    --name "Dev Test" --email dev@local --type pro --max-machines 1

# the key prints to stdout — copy it
```

Click the **⏳ Trial: 30 Day** badge in the top right → paste the key → click
**Activate**. Badge changes to **🔑 Licensed: Dev Test • Pro**. The activation
is bound to your machine's hardware ID and written to `data/license.json`.

---

## 3. Architecture overview

### 3.1 Layered architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              UI Thread (PyQt6)                           │
│                                                                          │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────────┐    │
│   │ MainWindow  │  │SettingsDialog│  │ ActivateDialog              │    │
│   └──────┬──────┘  └──────────────┘  └──────────────┬──────────────┘    │
│          │                                          │                    │
│          │   signals/slots (auto-marshalled)        │                    │
│          ▼                                          ▼                    │
│   ┌──────────────────┐                  ┌─────────────────────────┐     │
│   │ VideoTableModel  │                  │ LicenseManager          │     │
│   └──────────────────┘                  └─────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │ QThread.start()
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            Worker Thread (RenderWorker)                  │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ ThreadPoolExecutor(max_workers=threads_render)                  │   │
│   │   spawns N parallel ffmpeg subprocesses                         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                      │                                   │
└──────────────────────────────────────┼───────────────────────────────────┘
                                       │ subprocess.Popen()
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       ffmpeg child processes (1..N)                      │
│   Each one: input file → filter_complex → -c:v <encoder> → output.mp4   │
└──────────────────────────────────────────────────────────────────────────┘
```

Key design rules:

1. **UI thread never blocks.** Anything slower than ~16 ms goes on a thread.
2. **Worker thread never touches widgets.** It communicates with the UI by
   emitting Qt signals. Qt auto-marshals signal payloads back to the UI
   thread via a queued connection.
3. **FFmpeg never sees Python objects.** The worker builds a flat
   `list[str]` command and spawns `subprocess.Popen`. This means we can
   `terminate()` a hung FFmpeg without unwinding Python state.
4. **Persistence is always atomic.** Every JSON file (settings / trial /
   license) is written via `tmp + os.replace` so a crash mid-write never
   leaves a half-baked file behind.

### 3.2 Threading model

```
                Time ─►

UI thread        ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
                 │     │     │      │       │           │
                 │     │     │      │       │           └─ finished_all → "All jobs finished"
                 │     │     │      │       └─ item_finished(2, ok=True)
                 │     │     │      └─ item_progress(2, 60%)
                 │     │     └─ item_started(2)
                 │     └─ item_finished(1, ok=True)
                 └─ START clicked, worker.start()

Worker thread       █████████████████████████████████████████
                                  │                │
                                  │ pool.submit(_process_item, 0)
                                  └ pool.submit(_process_item, 1)
                                         ...

ffmpeg child 1          █████████████  (clip01 done)
ffmpeg child 2              █████████████████████  (clip02 done)
```

### 3.3 Signal/slot wiring

```
RenderWorker signal       MainWindow slot                Side effect
──────────────────────────────────────────────────────────────────────
item_started(row)        _on_item_started(row)           set status="running", reset per-item bar
item_progress(row, pct)  _on_item_progress(row, pct)     update per-item progress bar
item_finished(row,ok,msg) _on_item_finished(row,ok,msg)  set status="done"/"error" + tooltip
overall_progress(pct)    pb_overall.setValue            update overall bar
finished_all()           _on_finished_all()             re-enable START, show "Done" dialog
log(line)                _on_log(line)                  (currently no-op; hooked for debug panel)
```

Every connection is `Qt.AutoConnection`, which becomes `QueuedConnection`
when the sender and receiver live on different threads — Qt enqueues the
payload onto the receiver's event loop. This is **how thread-safe GUI
updates work in Qt** without us writing a single `mutex.lock()`.

---

## 4. Folder structure

```
panha-vshort/
├── main.py                        ← entry point (QApplication boot)
├── requirements.txt               ← pinned Python deps
├── README.md
├── .gitignore                     ← excludes data/, keys/, keys-issued/, .venv/, dist/, build/
│
├── app/
│   ├── __init__.py                ← APP_NAME, APP_AUTHOR, APP_YEAR, __version__
│   │
│   ├── i18n/
│   │   └── __init__.py            ← string tables EN+KM, tr(), set_language(), subscribe/unsubscribe
│   │
│   ├── core/                      ← business logic, no Qt widgets allowed
│   │   ├── __init__.py            ← re-exports the small public surface
│   │   ├── ffmpeg_runner.py       ← RenderOptions, build_filter_graph, build_render_command
│   │   ├── hardware.py            ← Encoder dataclass + detection
│   │   ├── licensing.py           ← LicenseInfo, LicenseManager, hardware_id, Ed25519 sign/verify
│   │   ├── preview.py             ← first_frame() + apply_preview_effects() + pil_to_qpixmap()
│   │   ├── render_worker.py       ← RenderWorker(QThread)
│   │   ├── settings_store.py      ← SettingsStore + DEFAULTS schema
│   │   ├── trial.py               ← Trial class
│   │   └── video_scanner.py       ← VideoItem, ScanResult, scan_folder()
│   │
│   └── ui/                        ← Qt-aware widgets
│       ├── __init__.py
│       ├── activate_dialog.py     ← paste a license key dialog
│       ├── main_window.py         ← the V-Short 3.2 layout (≈580 lines)
│       ├── settings_dialog.py     ← tabbed Settings dialog
│       ├── styles.py              ← QSS dark stylesheet
│       └── video_table.py         ← QAbstractTableModel + filter proxy
│
├── tools/
│   ├── __init__.py
│   ├── README.md                  ← admin workflow docs
│   └── generate_key.py            ← --init / mint / verify
│
├── docs/                          ← this file lives here
│   └── DEVELOPER_TUTORIAL.md
│
├── keys/                          ← admin_private.pem + admin_public.txt (gitignored)
│
├── keys-issued/                   ← per-customer copies + audit log (gitignored)
│
├── assets/                        ← logo / icons (optional)
│
└── data/                          ← runtime state (gitignored)
    ├── settings.json
    ├── trial.json
    └── license.json
```

> **Layering rule.** `app/core/` must NEVER import from `app/ui/` or PyQt
> widget classes. The only Qt import allowed in `core/` is
> `PyQt6.QtCore` (for `QObject`/`QThread`/`pyqtSignal`), because those are
> *threading primitives* that the worker needs. UI imports from `core/` is
> fine. This one-way dependency keeps the business logic testable.

---

## 5. Lesson 1 — `app/__init__.py` and `main.py`

### 5.1 Goal

Get the app to boot cleanly — load persistent state, apply saved language,
show the main window — in a deterministic order that prevents UI flicker
and signal races.

### 5.2 `app/__init__.py`

This is just project-wide constants. Keeping them in one place means the
PyInstaller spec, the help dialog ("About"), and the footer all read from
the same source:

```python
"""Pnnha V-Short — application package."""

__version__ = "1.0.0"
APP_NAME    = "Pnnha V-Short"
APP_AUTHOR  = "HORN LYHENG (Admin-Kh)"
APP_YEAR    = 2026
```

### 5.3 `main.py`

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

    store = SettingsStore()                       # ← 1. read data/settings.json
    trial = Trial()                                # ← 2. read/init data/trial.json
    license_manager = LicenseManager(trial=trial)  # ← 3. read data/license.json + verify sig
    set_language(store.get("language", "en"))      # ← 4. before widgets are built

    w = MainWindow(store, trial, license_manager)  # ← 5. build & show
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

### 5.4 Why this order matters

| Step | If you skip it | Symptom |
|------|----------------|---------|
| 1. `SettingsStore` first | The app boots with defaults | User's saved Input/Output folders are gone |
| 2. `Trial` before `LicenseManager` | The LicenseManager can't fall back to trial state | "License expired" shown even on day 1 |
| 3. `LicenseManager` reads `data/license.json` | Activation is silently dropped | Customer has to re-activate every launch |
| 4. `set_language(...)` BEFORE widgets | Widgets paint English first, then re-translate to Khmer | Visible flicker on launch |
| 5. `MainWindow` last | – | – |

### 5.5 Exercise / លំហាត់

Add a `--reset-trial` CLI flag to `main.py` that deletes `data/trial.json`
before instantiating `Trial()` (admin/dev use only — do **not** ship to
customers). Hint: `argparse` before `QApplication(sys.argv)` so Qt doesn't
swallow the argument.

<details><summary>Solution sketch</summary>

```python
import argparse

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-trial", action="store_true")
    args, qt_args = parser.parse_known_args()
    if args.reset_trial:
        from app.core.trial import TRIAL_FILE
        TRIAL_FILE.unlink(missing_ok=True)

    app = QApplication([sys.argv[0]] + qt_args)
    ...
```

</details>

---

## 6. Lesson 2 — i18n

### 6.1 Goal

Switch the UI between **English** and **ខ្មែរ** live, without restarting the
app, and without missing any label.

### 6.2 Mental model

```
+-----------------+   set_language("km")    +------------------+
| User clicks KM  | ─────────────────────► │ _current_lang="km"│
+-----------------+                         +------------------+
                                                     │
                                                     │ for cb in _listeners: cb()
                                                     ▼
                                       +------------------------------------+
                                       │ MainWindow._retranslate()         │
                                       │ SettingsDialog._retranslate()     │
                                       │ VideoTableModel.refresh_headers() │
                                       │ ... every subscribed callback     │
                                       +------------------------------------+
```

Each widget that displays translatable text:

1. In its `__init__`, calls `subscribe(self._retranslate)`.
2. Defines `_retranslate(self)` that reads every label/placeholder/window
   title via `tr("key")` and re-sets it.
3. In its `closeEvent` (or in the parent's `closeEvent` for short-lived
   dialogs), calls `unsubscribe(self._retranslate)`.

### 6.3 Full module (`app/i18n/__init__.py`)

```python
"""English + Khmer string tables.

Usage:
    from app.i18n import tr, set_language, subscribe, unsubscribe
    set_language("km")
    label = tr("start")
"""
from __future__ import annotations
from typing import Callable, Dict, List, Tuple

_STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        # Top bar
        "home": "HOME",
        "settings": "Settings",
        "help": "Help",
        "trial_remaining": "Trial: {days} Day",
        "licensed_to": "Licensed: {label}",

        # Main panel
        "detected_videos": "Detected Videos",
        "start": "START",
        "stop": "STOP",
        "reload": "Reload",

        # Settings tabs (the audit-fixed ones)
        "settings_tab_general": "General",
        "settings_tab_effects": "Effects",
        "settings_tab_media":   "Audio && Encoder",   # &&  ← Qt mnemonic escape

        # Messages
        "msg_no_output_folder": "No output folder set. Pick one in Settings first.",
        "msg_ffmpeg_missing":   "ffmpeg is not on your PATH. Install it and restart.",
        "msg_done":             "All jobs finished.",
        # ...
    },
    "km": {
        "home": "ទំព័រដើម",
        "settings": "ការកំណត់",
        "help": "ជំនួយ",
        "trial_remaining": "សាកល្បង៖ {days} ថ្ងៃ",
        "licensed_to": "ត្រូវបានដំឡើង: {label}",

        "detected_videos": "វីដេអូដែលរកឃើញ",
        "start": "ចាប់ផ្ដើម",
        "stop": "ឈប់",
        "reload": "ផ្ទុកឡើងវិញ",

        "settings_tab_general": "ទូទៅ",
        "settings_tab_effects": "បែបផែន",
        "settings_tab_media":   "សំឡេង && Encoder",

        "msg_no_output_folder": "មិនបានកំណត់ Folder ខាងក្រៅ — សូមជ្រើសរើសក្នុង Settings ជាមុនសិន។",
        "msg_ffmpeg_missing":   "ffmpeg មិនមាននៅក្នុង PATH ទេ។ សូមដំឡើង រួចបើកកម្មវិធីឡើងវិញ។",
        "msg_done":             "ការងារទាំងអស់បានបញ្ចប់។",
        # ...
    },
}

_current_lang = "en"
_listeners: List[Callable[[], None]] = []


def set_language(code: str) -> None:
    """Change the active language and notify all subscribers."""
    global _current_lang
    if code not in _STRINGS:
        raise ValueError(f"Unknown language: {code}")
    if code == _current_lang:
        return
    _current_lang = code
    for cb in list(_listeners):    # iterate a copy in case a callback unsubscribes
        try:
            cb()
        except Exception:
            pass                   # never let one bad subscriber break the toggle


def get_language() -> str:
    return _current_lang


def available_languages() -> List[Tuple[str, str]]:
    return [("en", "English"), ("km", "ខ្មែរ")]


def tr(key: str, **fmt) -> str:
    """Look up *key* in the current language. Falls back to English then to the key."""
    table = _STRINGS.get(_current_lang, {})
    text = table.get(key) or _STRINGS["en"].get(key) or key
    if fmt:
        try:
            return text.format(**fmt)
        except Exception:
            return text
    return text


def subscribe(cb: Callable[[], None]) -> None:
    _listeners.append(cb)


def unsubscribe(cb: Callable[[], None]) -> None:
    if cb in _listeners:
        _listeners.remove(cb)
```

### 6.4 The `&&` Qt mnemonic trap

Qt parses `&` in a label as the start of a **keyboard mnemonic** (Alt+X).
So the label `"Audio & Encoder"` renders as `"Audio _Encoder"` with the `&`
swallowed and the **E** underlined. To show a literal `&` in a tab title or
button label, **double it**:

| You write | Qt renders |
|-----------|------------|
| `"Audio & Encoder"` | `Audio_Encoder` (underline on `E`) ❌ |
| `"Audio && Encoder"` | `Audio & Encoder` ✅ |

Caught in the audit pass (see [§26](#26-audit-lessons)).

### 6.5 The fall-through chain

`tr("start")` does:

```
1. Look up "start" in _STRINGS["km"]   →  "ចាប់ផ្ដើម"  ← return
2. Otherwise look up in _STRINGS["en"] →  "START"     ← return
3. Otherwise return the key itself     →  "start"     ← visible bug, easy to spot
```

This means a missing translation is **never** a crash and is always
*visibly* wrong (you see the raw key in the UI), making it easy to catch
during QA.

### 6.6 Exercises / លំហាត់

1. Add a French translation. List the *exact* set of new keys you'd need to
   add to `_STRINGS["fr"]` (hint: it must be a superset of all keys
   referenced by `tr(...)` in `app/ui/`). Use `grep -rn 'tr(' app/ui/` to
   enumerate.
2. Add a `language_changed.connect(...)` Qt signal alternative. Compare it
   to the current callback list — when would you choose one over the other?
3. Make `set_language` log a warning every time a `tr()` call has to fall
   back to English. Useful in development; turn it off in production.

---

## 7. Lesson 3 — SettingsStore

### 7.1 Goal

Persist every user-tunable knob to `data/settings.json`. Survive partial
writes (power loss / kill -9). Be tolerant of schema drift.

### 7.2 Atomic write — the why

Naïve code:

```python
with open(path, "w") as f:        # ❌ DON'T DO THIS
    json.dump(data, f)
```

If `Ctrl+C` lands between `open()` (which truncates the file to 0 bytes)
and `json.dump` (which fills it), you end up with an empty `settings.json`,
which on next launch yields *defaults* — the user's settings are gone.

The fix is to write to a sibling temp file and then **atomically rename**:

```python
def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)         # POSIX: atomic; Windows: durable-replace
```

`os.replace` (Python ≥ 3.3) is the cross-platform "atomic rename" wrapper.
On Linux/macOS it's a single `rename(2)` syscall. On Windows it uses
`MoveFileExW(... MOVEFILE_REPLACE_EXISTING)`, which is durable but only
truly atomic if both files are on the same volume — which is fine for us
because they're in the same folder.

### 7.3 Schema drift tolerance

Two cases:

1. **File has a key we no longer know about.** Ignore it.
2. **File is missing a key.** Use the default.

The trick is to keep a single source of truth — `DEFAULTS` — and merge:

```python
def load(self) -> None:
    if self.path.exists():
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for k, v in loaded.items():
                    if k in DEFAULTS:        # ← drop unknown keys silently
                        self._data[k] = v
        except Exception:
            pass                              # ← corrupt file? fall back to defaults
```

### 7.4 `DEFAULTS` as schema documentation

```python
DEFAULTS: Dict[str, Any] = {
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

Adding a new setting? Add it here, give it a default, and you're done —
existing user files will pick up the default automatically.

### 7.5 Full module (`app/core/settings_store.py`)

```python
"""Persistent JSON settings store under ./data/settings.json."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULTS: Dict[str, Any] = {  # ... see §7.4 ... }


class SettingsStore:
    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path
        self._data: Dict[str, Any] = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    for k, v in loaded.items():
                        if k in DEFAULTS:
                            self._data[k] = v
            except Exception:
                pass

    def save(self) -> None:
        _atomic_write_text(
            self.path,
            json.dumps(self._data, indent=2, ensure_ascii=False),
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, mapping: Dict[str, Any]) -> None:
        for k, v in mapping.items():
            if k in DEFAULTS:
                self._data[k] = v

    def all(self) -> Dict[str, Any]:
        return dict(self._data)
```

### 7.6 Exercises

1. Add an `"output_quality"` setting that accepts `"low" | "medium" | "high"`
   and a default of `"medium"`. Plumb it through to FFmpegRunner so it
   controls `-crf 28 / 23 / 18`.
2. Migrate `cpu_limit` from `int` to a string `"low" | "balanced" | "high"`
   without breaking existing user files. Hint: a `migrate(loaded)` function
   called from `load()`.

---

## 8. Lesson 4 — Trial

### 8.1 Goal

Track the day the app was first launched and refuse rendering after 30
days **unless** a valid license is activated.

### 8.2 Code

```python
TRIAL_DAYS = 30
DATA_DIR   = Path(__file__).resolve().parents[2] / "data"
TRIAL_FILE = DATA_DIR / "trial.json"


class Trial:
    def __init__(self, path: Path = TRIAL_FILE, days: int = TRIAL_DAYS) -> None:
        self.path = path
        self.days = days
        self.start_date: date = date.today()
        self._load_or_init()

    def _load_or_init(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.start_date = date.fromisoformat(data["start_date"])
                return
            except Exception:
                pass
        self.start_date = date.today()
        self._save()

    def _save(self) -> None:
        _atomic_write_text(self.path, json.dumps({
            "start_date": self.start_date.isoformat(),
            "saved_at":   datetime.now().isoformat(timespec="seconds"),
        }, indent=2))

    def days_remaining(self) -> int:
        used = (date.today() - self.start_date).days
        return max(0, self.days - used)

    def is_expired(self) -> bool:
        return self.days_remaining() <= 0
```

### 8.3 "Can the user defeat this?"

Yes — `data/trial.json` is a plain text file on the user's disk. They can
delete it and the clock restarts. **This is intentional and acceptable**
for a free trial because:

1. The cost to copy-paste 5 seconds of trial-resetting saves you nothing.
2. The honest power-users who would otherwise pay aren't bothered by it.
3. The license system (Lesson 10) is the real revenue gate — it's
   cryptographic and not bypassable.

If you really want anti-tamper, store the date in:

- Windows registry under `HKCU\Software\Pnnha\VShort\TrialStart`
- macOS `~/Library/Preferences/com.AdminKh.PnnhaVShort.plist`
- Linux `~/.config/pnnha/trial.json` (still file-based, no real win)

…but each of these is also user-readable. The honest answer is **don't try
to defeat your own users**; price for paying customers, not pirates.

### 8.4 Exercises

1. Add `extend_trial(days: int)` that requires a signed coupon code (use
   the same Ed25519 key from Lesson 10). Useful for support: "your trial
   ended yesterday but the customer is on holiday for 3 days, send them a
   3-day extension".
2. Add `last_run_at` to `trial.json` and refuse to load if the date is in
   the future (catches users who tried to roll their clock back).

---

## 9. Lesson 5 — Hardware

### 9.1 Goal

Auto-detect which **video encoders** the local FFmpeg build advertises and
let the user pick one (or `auto`).

### 9.2 Detection algorithm

```
1. `shutil.which("ffmpeg")` → if None, return empty list
2. `ffmpeg -hide_banner -encoders` → parse stdout
3. for each "V..... <codec> ..." row, collect <codec>
4. Return concrete Encoder objects in this priority order:
       NVENC (h264_nvenc) > AMF (h264_amf) > CPU (libx264 always)
```

### 9.3 Code

```python
@dataclass(frozen=True)
class Encoder:
    key: str                          # "auto" | "nvenc" | "amf" | "cpu"
    label: str                        # human-readable label
    ffmpeg_codec: str                 # -c:v value
    extra_args: tuple[str, ...] = ()  # appended after -c:v


CPU_X264 = Encoder("cpu",   "CPU (x264)",       "libx264",     ("-preset", "veryfast"))
NVENC    = Encoder("nvenc", "Nvidia (NVENC)",   "h264_nvenc",  ("-preset", "p4"))
AMF      = Encoder("amf",   "AMD (AMF)",        "h264_amf",    ())


def _list_encoders() -> List[str]:
    if not shutil.which("ffmpeg"):
        return []
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-encoders"],
        capture_output=True, text=True, timeout=10,
    )
    names = []
    for line in out.stdout.splitlines():
        parts = line.strip().split()
        # encoder rows look like:  " V..... libx264 ..."
        if len(parts) >= 2 and parts[0].startswith("V"):
            names.append(parts[1])
    return names


def available_encoders() -> List[Encoder]:
    names = set(_list_encoders())
    result = []
    if NVENC.ffmpeg_codec in names: result.append(NVENC)
    if AMF.ffmpeg_codec   in names: result.append(AMF)
    result.append(CPU_X264)          # x264 is in every build
    return result


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

### 9.4 Adding a new encoder

Say you want to support Apple VideoToolbox on macOS:

```python
VIDEOTOOLBOX = Encoder("vt", "Apple (VideoToolbox)", "h264_videotoolbox", ())

def available_encoders() -> List[Encoder]:
    names = set(_list_encoders())
    result = []
    if NVENC.ffmpeg_codec        in names: result.append(NVENC)
    if AMF.ffmpeg_codec          in names: result.append(AMF)
    if VIDEOTOOLBOX.ffmpeg_codec in names: result.append(VIDEOTOOLBOX)
    result.append(CPU_X264)
    return result
```

And in `resolve_encoder("auto")` insert `"vt"` between `"amf"` and `"cpu"`.
Add `("vt", "Apple (VideoToolbox)")` to the Settings combobox. Done.

### 9.5 Exercises

1. Add HEVC encoders (`hevc_nvenc`, `hevc_amf`, `libx265`). Wire them
   through a new Settings dropdown `Codec: H.264 / H.265`.
2. Detect available *audio* encoders (`libfdk_aac`, `aac`, `libmp3lame`).
   Surface them in Settings as a fallback chain.

---

## 10. Lesson 6 — VideoScanner

### 10.1 Goal

Walk a folder once and return a structured `ScanResult` the UI table can
render directly. Don't recurse — the user can pre-flatten if they want.

### 10.2 Decisions

| Question | Answer |
|----------|--------|
| Recurse into subfolders? | **No.** Predictable behaviour beats clever scanning. |
| What counts as a video? | Eight common extensions (mp4, mov, mkv, avi, webm, m4v, flv, wmv). |
| Where do audio files come from? | A separate "audio_folder" setting **or** the same folder. |
| Where does the logo come from? | A separate "logo_file" setting **or** the first image in the folder. |
| Sort order? | Lexicographic on filename, so the user can prefix with `01_`, `02_`. |

### 10.3 Full code

```python
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv"}
AUDIO_EXTS = {".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class VideoItem:
    index: int
    path: Path
    audio: Optional[Path] = None
    logo:  Optional[Path] = None
    status: str = "ready"           # ready | queued | running | done | error
    status_detail: str = ""
    progress: int = 0               # 0..100

    @property
    def name(self) -> str:  return self.path.name
    @property
    def stem(self) -> str:  return self.path.stem


@dataclass
class ScanResult:
    videos: List[VideoItem] = field(default_factory=list)
    audios: List[Path]      = field(default_factory=list)
    logo:   Optional[Path]  = None

    @property
    def video_count(self) -> int: return len(self.videos)
    @property
    def audio_count(self) -> int: return len(self.audios)
    @property
    def logo_count(self)  -> int: return 1 if self.logo else 0


def scan_folder(folder, logo_file="", audio_folder="") -> ScanResult:
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
                result.logo = p   # auto-pick first image as logo

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
```

### 10.4 Exercise

Add a `min_duration_seconds` parameter that filters out clips shorter than
N seconds (use `ffmpeg_runner.video_duration(p)`). Tradeoff: scanning gets
slower because every file gets probed.

---

## 11. Lesson 7 — FFmpegRunner

This is the longest lesson — the heart of the app.

### 11.1 Goal

Translate the `RenderOptions` dataclass into a complete `ffmpeg ...`
command array, including the correct `-filter_complex` string for blur
background, logo, text overlay, timer, and audio mode.

### 11.2 `RenderOptions` dataclass

```python
@dataclass
class RenderOptions:
    output_folder: Path
    output_format: str = "mp4"
    overlay_text: str = ""
    show_timer: bool = False
    blur_background: bool = False
    logo_file: Optional[Path] = None
    audio_mode: str = "keep"               # keep | mix | mute | random | mp3
    audio_file: Optional[Path] = None      # used when audio_mode in {mix, mp3}
    audio_pool: Tuple[Path, ...] = ()      # random pool
    encoder: Optional[Encoder] = None      # resolved Encoder
    cpu_limit: int = 4
    cut_parts: int = 1                     # >1 means cut-plus
    rename_prefix: str = "video_"
    rename_index: int = 1
```

### 11.3 Filter graph diagram

```
            ┌────────────────────────────────────────────────────────────────┐
            │                   Filter graph                                 │
            │                                                                │
[0:v] ───►  │  if blur_background:                                          │
            │      split=2[main][bg]                                         │
            │      [bg]scale=1080:1920:fit-increase,                         │
            │           crop=1080:1920,                                      │
            │           boxblur=20:1                       [bg2]             │
            │      [main]scale=1080:-2                     [fg]              │
            │      [bg2][fg]overlay=(W-w)/2:(H-h)/2        [vbg] ──┐        │
            │  else:                                                │        │
            │      scale=trunc(iw/2)*2:trunc(ih/2)*2       [vsc] ──┤        │
            │                                                       │        │
[1:v] ───►  │  if has_logo: [(vbg|vsc)][1:v]overlay=20:20 [vl]  ──┤        │
            │                                                       │        │
            │  if overlay_text:                                    │        │
            │      drawtext=text='<escaped>':                      │        │
            │               expansion=none                         │        │
            │               x=(w-text_w)/2:y=h-100                 │        │
            │  if show_timer:                                      │        │
            │      drawtext=text='%{pts\:hms}':                    │        │
            │               (default expansion)                    │        │
            │               x=20:y=h-60                            ▼        │
            │                                                  [vt] ──►    │
            │                                                       │       │
            │  format=yuv420p                                       ▼       │
            │                                                  [vout] ──► output
            └────────────────────────────────────────────────────────────────┘
```

### 11.4 The `%` trap in drawtext

The `drawtext` filter has a built-in **text expansion** mode. With the
default `expansion=normal`, FFmpeg interprets a `%` as the start of a
`%{...}` expression:

```
text="Discount 50% off"      →  FFmpeg tries to parse "%off}"      →  error
text="Audit Check 100%"      →  FFmpeg tries to parse "%"          →  "Stray %" warning + silent text drop
text="%{pts\:hms}"           →  FFmpeg evaluates the expression    →  "00:00:01.000"  ✅
```

Solution: tell FFmpeg "treat every character as literal" by adding
`expansion=none` to *user-supplied* drawtext, while keeping default
expansion on the *timer* drawtext (we *want* `%{pts\:hms}` to evaluate
there).

```python
def _escape_drawtext(text: str) -> str:
    # Always escape backslash, colon, single-quote (parser meta-chars).
    # Do NOT escape `%` — the documented \% escape doesn't survive expansion.
    return (
        text.replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", r"\'")
    )


drawtexts = []
if opts.overlay_text:
    drawtexts.append(
        "drawtext=text='%s':fontcolor=white:fontsize=42:"
        "box=1:boxcolor=black@0.4:boxborderw=10:"
        "expansion=none:"               # ←  THE FIX
        "x=(w-text_w)/2:y=h-100" % _escape_drawtext(opts.overlay_text)
    )
if opts.show_timer:
    drawtexts.append(
        "drawtext=text='%{pts\\:hms}':fontcolor=yellow:fontsize=32:"
        "box=1:boxcolor=black@0.4:boxborderw=8:x=20:y=h-60"
        # ←  no expansion=none here — we WANT the expression to evaluate
    )
```

### 11.5 `build_filter_graph`

```python
def build_filter_graph(opts: RenderOptions, has_logo_input: bool) -> str:
    parts = []
    cur = "0:v"

    # 1. background (blur or simple even-resize)
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

    # 2. logo overlay
    if has_logo_input:
        parts.append(f"[{cur}][1:v]overlay=20:20[vl]")
        cur = "vl"

    # 3. drawtexts (text + timer)
    drawtexts = []
    if opts.overlay_text:
        drawtexts.append(
            "drawtext=text='%s':fontcolor=white:fontsize=42:"
            "box=1:boxcolor=black@0.4:boxborderw=10:"
            "expansion=none:"
            "x=(w-text_w)/2:y=h-100" % _escape_drawtext(opts.overlay_text)
        )
    if opts.show_timer:
        drawtexts.append(
            "drawtext=text='%{pts\\:hms}':fontcolor=yellow:fontsize=32:"
            "box=1:boxcolor=black@0.4:boxborderw=8:x=20:y=h-60"
        )
    if drawtexts:
        parts.append(f"[{cur}]" + ",".join(drawtexts) + "[vt]")
        cur = "vt"

    # 4. final pixel format
    parts.append(f"[{cur}]format=yuv420p[vout]")

    return ";".join(parts)
```

### 11.6 Audio mode dispatch

```python
def _audio_args(opts, fallback_to_silent=False):
    inputs, mapping = [], []
    if opts.audio_mode == "mute":
        mapping += ["-an"]
    elif opts.audio_mode == "keep":
        mapping += ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    elif opts.audio_mode in ("mp3", "random") and opts.audio_file:
        inputs += ["-i", str(opts.audio_file)]
        mapping += ["-map", "AUDIO:a:0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    elif opts.audio_mode == "mix" and opts.audio_file:
        inputs += ["-i", str(opts.audio_file)]
        mapping += [
            "-filter_complex_extra",
            "[0:a][AUDIO:a]amix=inputs=2:duration=shortest[aout]",
            "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
        ]
    else:
        if fallback_to_silent: mapping += ["-an"]
        else: mapping += ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    return inputs, mapping
```

The `AUDIO` literal is a placeholder. `build_render_command` rewrites it
to the correct stream slot:

```python
audio_slot = 2 if has_logo else 1   # logo always occupies slot 1 when present
audio_map = [a.replace("AUDIO", str(audio_slot)) for a in audio_map]
```

The `-filter_complex_extra` token is pseudo — it's stripped out of
`audio_map` by `build_render_command` and concatenated onto the main
filter graph so the `amix` is part of one `-filter_complex` argument.

### 11.7 `build_render_command`

```python
def build_render_command(src, dst, opts, *, cut_segment=None) -> List[str]:
    enc = opts.encoder or resolve_encoder("auto")

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-threads", str(max(1, int(opts.cpu_limit))),
    ]

    if cut_segment is not None:                  # cut-plus seeking
        start, dur = cut_segment
        cmd += ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"]

    cmd += ["-i", str(src)]                      # input 0 = video

    has_logo = bool(opts.logo_file and Path(opts.logo_file).is_file())
    if has_logo:
        cmd += ["-i", str(opts.logo_file)]       # input 1 = logo (if any)

    audio_slot = 2 if has_logo else 1
    audio_inputs, audio_map = _audio_args(opts)
    audio_map = [a.replace("AUDIO", str(audio_slot)) for a in audio_map]
    cmd += audio_inputs                          # input 2 (or 1) = audio (if any)

    fg = build_filter_graph(opts, has_logo_input=has_logo)

    # pull -filter_complex_extra out of audio_map and merge into main graph
    extra_audio_graph = ""
    cleaned_audio_map, skip = [], False
    for i, tok in enumerate(audio_map):
        if skip: skip = False; continue
        if tok == "-filter_complex_extra":
            extra_audio_graph = audio_map[i + 1]; skip = True; continue
        cleaned_audio_map.append(tok)
    audio_map = cleaned_audio_map

    full_graph = fg + (";" + extra_audio_graph if extra_audio_graph else "")
    cmd += ["-filter_complex", full_graph, "-map", "[vout]"]
    cmd += audio_map

    cmd += ["-c:v", enc.ffmpeg_codec, *enc.extra_args, "-pix_fmt", "yuv420p"]
    cmd += ["-movflags", "+faststart"]   # web-friendly
    cmd += [str(dst)]
    return cmd
```

### 11.8 The concat-demuxer apostrophe trap

The **concat demuxer** reads a list file of lines like:

```
file '/path/to/clip01.mp4'
file '/path/to/clip02.mp4'
```

If a path contains a single quote, the naive serialiser produces broken
syntax. The escape is the **classic shell trick** "close, escape, reopen":

```python
def _concat_quote(p: Path) -> str:
    return p.as_posix().replace("'", "'\\''")
```

So `/tmp/a's clip.mp4` becomes `/tmp/a'\''s clip.mp4`, which the demuxer
parses as the three pieces `a` + `'` + `s clip.mp4` joined.

### 11.9 `build_merge_command`

```python
def build_merge_command(sources, dst, opts, concat_list_path) -> List[str]:
    enc = opts.encoder or resolve_encoder("auto")

    def _concat_quote(p):
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
    # ... same filter graph / logo / audio plumbing as build_render_command ...
    return cmd
```

### 11.10 Cheat sheet: which ffmpeg flag does what

| Flag | What it does |
|------|--------------|
| `-hide_banner` | Suppress FFmpeg's version banner — keeps logs clean |
| `-loglevel error -stats` | Only show errors and progress stats |
| `-y` | Overwrite output file without prompting |
| `-threads N` | Cap FFmpeg's internal worker thread count |
| `-ss T -t D` (before `-i`) | Demuxer-level seek: jump to T, output D seconds |
| `-i FILE` | Add an input — repeat to add more (videos, logos, audio) |
| `-filter_complex GRAPH` | Apply a multi-input/output filter graph |
| `-map [LABEL]` | Pick which stream(s) to write to the output |
| `-c:v CODEC -pix_fmt yuv420p` | Video encoder + universal pixel format |
| `-c:a aac -b:a 192k` | AAC audio @ 192 kbps |
| `-shortest` | Stop output at the shortest input (avoid silent trailing video) |
| `-movflags +faststart` | Move MP4 metadata to the front so streaming works |

### 11.11 Exercises

1. Add a **letterbox** option (vertical black bars instead of blur). Hint:
   replace the blur graph branch with `scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:black`.
2. Add a **crop** option: cut N seconds off the start (`opts.crop_start`).
3. Add a **fade-in / fade-out** option using `fade=in:0:30,fade=out:st=X:d=30`
   where X is `duration - 1.0`.
4. Add an **audio normalize** filter (`loudnorm`) so MP3 mixes match the
   source loudness.

---

## 12. Lesson 8 — RenderWorker

### 12.1 Goal

Run all queued items in parallel without blocking the UI thread, with a
clean abort path and pre-flight validation.

### 12.2 Signal contract

```python
class RenderWorker(QThread):
    item_started     = pyqtSignal(int)               # row index
    item_progress    = pyqtSignal(int, int)          # (row, 0..100)
    item_finished    = pyqtSignal(int, bool, str)    # (row, ok, message)
    overall_progress = pyqtSignal(int)               # 0..100
    finished_all     = pyqtSignal()
    log              = pyqtSignal(str)               # stderr line for debug panel
```

### 12.3 Lifecycle diagram

```
            ┌────────────────────────────┐
            │ MainWindow.start_render()  │
            │   - build RenderOptions    │
            │   - new RenderWorker(...)  │
            │   - connect 6 signals      │
            │   - worker.start()         │
            └─────────────┬──────────────┘
                          │ QThread spawns OS thread
                          ▼
            ┌────────────────────────────┐
            │ RenderWorker.run()         │
            │  - have_ffmpeg? else exit  │
            │  - items present?          │
            │  - output_folder set?      │
            │  - merge mode? else ...    │
            │  - ThreadPoolExecutor(N)   │
            │     submit _process_item   │
            │     for each video         │
            │  - on each finish: emit    │
            │     item_finished + bump   │
            │     overall_progress       │
            │  - finally: finished_all   │
            └─────────────┬──────────────┘
                          │
            ┌─────────────▼──────────────┐
            │ MainWindow._on_finished_all│
            │   re-enable START          │
            │   show "Done" dialog       │
            └────────────────────────────┘
```

### 12.4 Abort path — the careful bit

```python
def stop(self) -> None:
    self._abort.set()                      # 1. signal: every loop should bail
    with self._procs_lock:                 # 2. terminate live subprocesses
        for p in self._procs:
            try:
                p.terminate()              # SIGTERM on POSIX; on Windows: TerminateProcess
            except Exception:
                pass
```

The reader loop polls the abort flag each iteration:

```python
for line in proc.stdout or []:
    if self._abort.is_set():
        proc.terminate()
        break
    line = line.strip()
    if line:
        self.log.emit(line[:240])
```

This means a stuck FFmpeg dies within ~16 ms of `stop()`.

### 12.5 Per-item RenderOptions copy

When `audio_mode == "random"`, we want each clip to potentially get a
different MP3. We **copy** the options struct so worker threads don't trample
each other:

```python
def _process_item(self, row, item, out_dir, on_done):
    ...
    opts = RenderOptions(
        output_folder=self.opts.output_folder,
        ...
        audio_file=self._audio_choice(item),    # ← resolved per-item here
        ...
    )
```

### 12.6 Cut-plus loop

```python
duration = video_duration(item.path)
piece    = duration / self.cut_parts
for p in range(self.cut_parts):
    if self._abort.is_set():
        on_done(row, False, "aborted"); return
    start = p * piece
    dst = out_dir / f"{base_name}_part{p+1:02d}{ext}"
    ok, msg = self._run_one(row, item, dst, opts, segment=(start, piece))
    success_all = success_all and ok
    self.item_progress.emit(row, int((p+1) / self.cut_parts * 100))
```

This emits incremental progress so the per-item progress bar moves *during*
a multi-part render, not just between items.

### 12.7 Pre-flight validation (audit fix)

```python
def run(self) -> None:
    if not have_ffmpeg():
        self.log.emit("ffmpeg not found"); self.finished_all.emit(); return
    if not self.items:
        self.log.emit("no items to render"); self.finished_all.emit(); return

    out_dir_str = str(self.opts.output_folder or "").strip()
    if not out_dir_str:
        self.log.emit("output folder is not configured")
        self.finished_all.emit(); return
    out_dir = Path(out_dir_str)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        self.log.emit(f"cannot create output folder {out_dir}: {e}")
        self.finished_all.emit(); return
    ...
```

These checks duplicate what `MainWindow.start_render` already does — but
**defence in depth**: if a future caller bypasses the UI (e.g. CLI mode),
the worker still refuses gracefully.

### 12.8 Exercises

1. Add a **priority queue** so the user can drag items to reorder them
   before clicking START.
2. Add a **retry-on-failure** counter: if an item fails, retry once with a
   fallback encoder (CPU) before giving up.
3. Add **bandwidth throttling**: limit each FFmpeg child to N MB/s of CPU
   throughput. Hint: `cpulimit` external tool or `nice` priority.

---

## 13. Lesson 9 — Preview

### 13.1 Goal

Render a 360×640 still preview that mirrors every effect the renderer will
apply, so the user can iterate on Settings without burning a real render.

### 13.2 Pipeline

```
1. cv2.VideoCapture(path)
   - seek to frame min(30, total // 4)  ← avoid black slates
   - read 1 frame as BGR
2. cv2.cvtColor(BGR → RGB)
3. PIL.Image.fromarray(rgb)
4. apply_preview_effects():
   - if blur_background: scale + GaussianBlur + paste
   - else: letterbox-fit
   - paste logo at (10, 10)
   - draw overlay_text near bottom
   - draw "00:00:01" timer near bottom-left
5. pil_to_qpixmap(pil_image) → QPixmap
6. preview_label.setPixmap(pixmap)
```

### 13.3 Font fallback across Pillow versions

Pillow 10 added a `size=` parameter to `ImageFont.load_default()`. Older
Pillows raise `TypeError`. The compatible loader:

```python
def _try_load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, size)
            except Exception: continue
    try:    return ImageFont.load_default(size=size)
    except TypeError: return ImageFont.load_default()
```

Similarly for `_font_height(font)` — newer Pillow exposes `font.size`,
older `font.getbbox("Ag")` gives the bounding box.

### 13.4 Why OpenCV for the first frame?

PIL alone can decode JPEG/PNG but not MP4/H.264. We could shell out to
`ffmpeg -ss 0 -frames:v 1 - -f image2pipe` and parse the byte stream, but
OpenCV's `VideoCapture` is **already** in our deps for nothing, and it's
~5× faster on big files because it doesn't spawn a subprocess.

### 13.5 Exercise

Add a 5-second video preview that loops via `QMediaPlayer` (PyQt6's
multimedia module). Tradeoff: another dependency that PyInstaller has to
ship.

---

## 14. Lesson 10 — Licensing

### 14.1 Goal

Validate paying customers offline, with a key the customer pastes once and
that's bound to their machine.

### 14.2 Why Ed25519?

| Property | Ed25519 | RSA-2048 |
|----------|---------|----------|
| Public key size | **32 bytes** (easy to embed in source as a base64url string) | 256+ bytes |
| Signature size | **64 bytes** | 256 bytes |
| Verify speed | very fast | slow |
| Deterministic | yes | no (extra entropy needed) |
| Library | `cryptography` (we already have it) | also `cryptography` |

Ed25519 is the modern default for "sign a small payload and verify it
offline".

### 14.3 Key format

```
PNNHA1.<base64url(payload_json)>.<base64url(ed25519_signature)>
                                        ▲
                                        │
                              signature is over the EXACT bytes
                              of payload_json (no canonicalisation
                              by the verifier — both sides
                              use json.dumps(payload, sort_keys=True,
                              separators=(",", ":")) so the bytes
                              are deterministic)
```

The `payload_json` is:

```json
{
    "kid": "abcd1234",
    "name": "Customer Name",
    "email": "buyer@example.com",
    "type": "pro",
    "issued_at": "2026-05-22",
    "expires": "2027-05-22",
    "max_machines": 1,
    "features": ["merge", "cut_plus", ...]
}
```

### 14.4 Hardware fingerprint

```python
def hardware_id() -> str:
    parts = [
        str(uuid.getnode()),         # 48-bit MAC, falls back to random
        socket.gethostname(),
        platform.system(),
        platform.machine(),
    ]
    # Linux machine-id is very stable across reboots
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            parts.append(Path(p).read_text(encoding="utf-8").strip())
            break
        except Exception:
            continue
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
```

16 hex chars (≈64 bits) is plenty for hardware binding. It's displayed in
the Activate dialog so customers can include it in support tickets.

### 14.5 Activation flow

```
Customer pastes key into Activate dialog
        │
        ▼
LicenseManager.activate(key)
        │
        ├─► verify_key(key)
        │   ├─ parse 3-part format          (raises ValueError if malformed)
        │   ├─ Ed25519.verify(sig, payload) (raises InvalidSignature → ValueError)
        │   └─ check type in LICENSE_TYPES  (raises ValueError on unknown type)
        │
        ├─► is_expired? → ActivationResult(False, error="license expired")
        │
        ├─► self.info        = info
        │   self.key         = key
        │   self.activated_hw = hardware_id()
        │   self.activated_at = datetime.now().isoformat()
        │
        └─► save()  →  atomic write of data/license.json
                       { "key": ..., "hw": ..., "activated_at": ..., "info": {...} }
```

### 14.6 Placeholder public-key guard (audit fix)

If you ship without rotating the dev keypair, **anyone** can mint a key
that the app would accept. To guard against this, the audit added:

```python
_PLACEHOLDER_PK = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

def is_placeholder_public_key() -> bool:
    return PUBLIC_KEY_B64URL == _PLACEHOLDER_PK
```

The main window calls this on startup and shows an info dialog so the
admin notices — production builds should never see this.

### 14.7 Trial fall-back

```python
def can_render(self) -> bool:
    if self.is_licensed():
        return True
    return not self.trial.is_expired()
```

A fresh install gets 30 days of trial. Paste a valid key → licensed,
trial irrelevant. Trial expires + no key → render is gated until they
paste one.

### 14.8 Display status

```python
def display_status(self) -> Dict[str, Any]:
    if self.is_licensed() and self.info:
        return {
            "state": "licensed",
            "label": self.info.display_label(),   # "Sok Dara • Pro • 365d"
            "type":  self.info.type,
            "days":  self.info.days_remaining(),
            "name":  self.info.name,
        }
    if self.info and self.info.is_expired():
        return {"state": "expired", "label": "License expired", "type": self.info.type}
    days = self.trial.days_remaining()
    if days > 0:
        return {"state": "trial", "label": f"Trial: {days} Day", "days": days}
    return {"state": "trial_expired", "label": "Trial expired"}
```

The main window's top-bar badge consumes the returned `label` verbatim.

### 14.9 Exercises

1. Add an **online activation server** option — a small Flask endpoint
   that issues + revokes keys. Keep the offline verification path as a
   fallback.
2. Add **feature gating**: render with `audio_mode="mix"` requires the
   `audio_mix` feature flag in `info.features`. Surface a friendly error
   when the user tries to use a feature their license doesn't include.

---

## 15. Lesson 11 — UI: QSS styles

### 15.1 Goal

A single dark-mode stylesheet that the main window applies to itself.
Centralising styles means re-theming is one file, not 20.

### 15.2 Example excerpt

```python
# app/ui/styles.py
QSS = """
QWidget { background: #0f172a; color: #e7ecf3; font-family: 'Segoe UI'; }

QFrame#TopBar { background: #111827; border-bottom: 1px solid #1f2937; }
QPushButton#NavButton {
    background: transparent; color: #e7ecf3;
    padding: 6px 12px; border-radius: 6px;
}
QPushButton#NavButton:hover { background: #1f2937; }

QPushButton#TrialBadge {
    background: #facc15; color: #0f172a;
    padding: 6px 14px; border-radius: 14px; font-weight: 600;
}

QPushButton[role="primary"] {
    background: #22c55e; color: #0f172a;
    padding: 8px 24px; border-radius: 6px; font-weight: 700;
}

QTableView {
    background: #0b1220;
    alternate-background-color: #0f172a;
    gridline-color: #1f2937;
    selection-background-color: #38bdf8;
}
QHeaderView::section { background: #111827; padding: 6px; }

QProgressBar { background: #1f2937; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #22c55e; }
"""
```

The `#objectName` and `[attribute]` selectors are how we target specific
widgets (`setObjectName("TopBar")`, `setProperty("role", "primary")`).

### 15.3 Exercise

Add a **light-mode** theme toggle in Settings. Hint: keep two QSS strings,
pick one in `MainWindow.__init__` based on `store.get("theme", "dark")`.

---

## 16. Lesson 12 — UI: VideoTable

### 16.1 The model

```python
COL_INDEX, COL_NAME, COL_AUDIO, COL_LOGO, COL_STATUS = range(5)

_STATUS_COLORS = {
    "ready":   QColor("#e7ecf3"),
    "queued":  QColor("#cbd5e1"),
    "running": QColor("#38bdf8"),
    "done":    QColor("#22c55e"),
    "error":   QColor("#ef4444"),
}


class VideoTableModel(QAbstractTableModel):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._items: List[VideoItem] = list(items or [])

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)
    def columnCount(self, parent=QModelIndex()):
        return 5

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        item = self._items[index.row()]; col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == COL_INDEX:  return item.index
            if col == COL_NAME:   return item.name
            if col == COL_AUDIO:  return item.audio.name if item.audio else "-"
            if col == COL_LOGO:   return item.logo.name if item.logo else "-"
            if col == COL_STATUS:
                base = tr(f"status_{item.status}")
                return f"{base} — {item.status_detail}" if item.status_detail else base
        elif role == Qt.ItemDataRole.ForegroundRole and col == COL_STATUS:
            return QBrush(_STATUS_COLORS.get(item.status, QColor("#e7ecf3")))
        return None
```

### 16.2 Why `dataChanged` over `reset()` for status updates

`reset()` invalidates **every** cell and forces a full re-layout. With 100+
items this causes a visible flicker. `dataChanged.emit(idx, idx)` says "this
one cell changed; just repaint it":

```python
def set_status(self, row: int, status: str, detail: str = "") -> None:
    if 0 <= row < len(self._items):
        self._items[row].status = status
        self._items[row].status_detail = detail
        idx = self.index(row, COL_STATUS)
        self.dataChanged.emit(idx, idx)
```

### 16.3 Filter proxy

```python
class VideoFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(COL_NAME)
        self._status_filter = "all"

    def set_status_filter(self, key: str) -> None:
        self._status_filter = key
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        if not super().filterAcceptsRow(row, parent): return False
        if self._status_filter == "all": return True
        model = self.sourceModel()
        if not isinstance(model, VideoTableModel): return True
        item = model.item_at(row)
        return bool(item and item.status == self._status_filter)
```

`QSortFilterProxyModel` handles the **name** filter for free
(`setFilterFixedString(text)` from the line edit). We just override
`filterAcceptsRow` to AND it with the status filter.

### 16.4 Exercise

Add a **size column** (file size in MB) and a **duration column**
(probed via `ffmpeg_runner.video_duration`). Don't probe on every cell
render — cache the result on the `VideoItem`.

---

## 17. Lesson 13 — UI: ActivateDialog

### 17.1 Layout

```
┌───────── License ─────────┐
│                           │
│ Paste your license key:   │
│ ┌───────────────────────┐ │
│ │ PNNHA1.eyJ...         │ │
│ │                       │ │
│ └───────────────────────┘ │
│                           │
│ Current status: Trial: 27 │
│ Hardware ID:    751f5b... │
│                           │
│ [Deactivate]   [Activate] │
│                  [Close]  │
└───────────────────────────┘
```

### 17.2 Code skeleton

```python
class ActivateDialog(QDialog):
    def __init__(self, manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle(tr("lic_dialog_title"))
        self.setModal(True)
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(tr("lic_paste_key")))

        self.key_edit = QPlainTextEdit()
        self.key_edit.setPlaceholderText("PNNHA1.eyJ...")
        self.key_edit.setMinimumHeight(80)
        layout.addWidget(self.key_edit)

        form = QFormLayout()
        self.status_label = QLabel()
        form.addRow(QLabel(tr("lic_current_status")), self.status_label)
        self.hw_label = QLabel(hardware_id())
        self.hw_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )
        form.addRow(QLabel(tr("lic_hardware_id")), self.hw_label)
        ...
```

### 17.3 Activate handler

```python
def _on_activate(self) -> None:
    key = self.key_edit.toPlainText().strip()
    if not key:
        return
    result = self.manager.activate(key)
    if result.ok:
        QMessageBox.information(self, tr("lic_dialog_title"),
                                tr("lic_activated_ok", name=result.info.name))
        self._refresh_status()
        self.accept()
        return
    QMessageBox.critical(self, tr("lic_dialog_title"),
                         tr("lic_activate_failed", err=result.error))
```

The dialog **closes on successful activation** so the user immediately
returns to the main window with the updated badge.

### 17.4 Exercise

Add **drag-and-drop** support: dropping a `.txt` file containing a key
auto-fills the QPlainTextEdit. Hint: override `dragEnterEvent` and
`dropEvent`.

---

## 18. Lesson 14 — UI: SettingsDialog

### 18.1 Three tabs

| Tab key | EN | KH | Contents |
|---------|----|----|----------|
| `settings_tab_general` | General | ទូទៅ | language, input/output/audio/logo |
| `settings_tab_effects` | Effects | បែបផែន | overlay text, timer, blur, merge, cut-plus, rename |
| `settings_tab_media`   | Audio && Encoder | សំឡេង && Encoder | audio mode, encoder, cpu_limit, threads_render |

The `&&` is the Qt mnemonic escape — see [§6.4](#64-the-qt-mnemonic-trap).

### 18.2 File picker helper

```python
def _picker(line: QLineEdit, btn_text: str, dir_mode: bool, parent: QWidget):
    def _on_click():
        if dir_mode:
            p = QFileDialog.getExistingDirectory(parent, btn_text,
                line.text() or str(Path.home()))
        else:
            p, _ = QFileDialog.getOpenFileName(parent, btn_text,
                line.text() or str(Path.home()))
        if p:
            line.setText(p)
    btn = QPushButton(tr("browse"))
    btn.clicked.connect(_on_click)
    return btn
```

Used like:

```python
self.in_folder = QLineEdit(store.get("input_folder", ""))
row = QHBoxLayout()
row.addWidget(self.in_folder)
row.addWidget(_picker(self.in_folder, tr("settings_input_folder"), True, self))
gform.addRow(QLabel(tr("settings_input_folder")), self._wrap(row))
```

### 18.3 Saving

```python
def accept(self):
    self.store.update({
        "input_folder":     self.in_folder.text(),
        "output_folder":    self.out_folder.text(),
        "audio_folder":     self.audio_folder.text(),
        "logo_file":        self.logo_file.text(),
        "overlay_text":     self.overlay_text.text(),
        "show_timer":       self.show_timer.isChecked(),
        "blur_background":  self.blur_bg.isChecked(),
        "merge":            self.merge.isChecked(),
        "cut_plus":         self.cut_plus.isChecked(),
        "cut_parts":        self.cut_parts.value(),
        "rename_prefix":    self.rename_prefix.text(),
        "rename_start":     self.rename_start.value(),
        "audio_mode":       self.audio_mode.currentData(),
        "audio_file":       self.audio_file.text(),
        "encoder":          self.encoder.currentData(),
        "cpu_limit":        self.cpu_limit.value(),
        "threads_render":   self.threads.value(),
    })
    self.store.set("language", self.lang_combo.currentData())
    self.store.save()
    set_language(self.lang_combo.currentData())   # fires i18n subscribers
    super().accept()
```

The `currentData()` calls return the **userData** of the selected combobox
item, not the visible label — so the persisted value is the stable English
code (`keep`/`mix`/`nvenc`/...) regardless of the user's language.

### 18.4 Exercise

Add a **Reset to defaults** button at the bottom of each tab that calls
`store._data = dict(DEFAULTS); store.save()` and re-paints the dialog.

---

## 19. Lesson 15 — UI: MainWindow

### 19.1 Layout breakdown

```
┌─ TopBar (60 px) ───────────────────────────────────────────────────────┐
│ 🏠 HOME   ⚙ Settings   ❓ Help ▾     "Pnnha V-Short"   ⏳ Trial   — ✕  │
├──────────────┬─────────────────────────────────────────────────────────┤
│              │ 🎬 Detected Videos : 2                 📁 Output: /…    │
│              ├─────────────────────────────────────────────────────────┤
│              │ [Filter name...]                       [Status ▾]       │
│              ├─────────────────────────────────────────────────────────┤
│              │ ┌───┬───────────┬───────┬──────┬──────────────┐         │
│ live preview │ │ # │ Name      │ Audio │ Logo │ Status       │         │
│  (PIL→Qt)    │ ├───┼───────────┼───────┼──────┼──────────────┤         │
│   ~360×640   │ │ 1 │ clip01.mp4│ -     │ -    │ Ready        │         │
│              │ │ 2 │ clip02.mp4│ -     │ -    │ Ready        │         │
│              │ └───┴───────────┴───────┴──────┴──────────────┘         │
│              │ 2 video(s), 0 audio file(s), 0 logo file                │
│              ├─────────────────────────────────────────────────────────┤
│              │ ────────  per-item progress bar  ────────               │
│              │ ────────  overall progress bar   ────────               │
│              ├─────────────────────────────────────────────────────────┤
│              │ Threads Render [2 ▾]          [START] [STOP] [Reload]   │
├──────────────┴─────────────────────────────────────────────────────────┤
│             © All rights reserved by HORN LYHENG (Admin-Kh) 2026        │
└────────────────────────────────────────────────────────────────────────┘
```

### 19.2 Wiring — what connects to what

| Source | Signal | Slot |
|--------|--------|------|
| `btn_home` | `clicked` | `reload_videos` |
| `btn_settings` | `clicked` | `open_settings` |
| `btn_help` | `clicked` | `_show_help_menu` |
| `trial_badge` | `clicked` | `open_activate_dialog` |
| `btn_min` | `clicked` | `showMinimized` |
| `btn_close` | `clicked` | `close` |
| `filter_edit` | `textChanged(str)` | `_on_filter_text` |
| `filter_combo` | `currentIndexChanged(int)` | `_on_filter_status` |
| `table.selectionModel()` | `currentChanged(...)` | `refresh_preview` |
| `preview_checkbox` | `toggled(bool)` | `refresh_preview` |
| `btn_start` | `clicked` | `start_render` |
| `btn_stop` | `clicked` | `stop_render` |
| `btn_reload` | `clicked` | `reload_videos` |
| `worker.item_started` | (signal) | `_on_item_started` |
| `worker.item_progress` | (signal) | `_on_item_progress` |
| `worker.item_finished` | (signal) | `_on_item_finished` |
| `worker.overall_progress` | (signal) | `pb_overall.setValue` |
| `worker.finished_all` | (signal) | `_on_finished_all` |
| `worker.log` | (signal) | `_on_log` |
| `app.i18n.set_language` | (callback) | `self._retranslate` (via `subscribe`) |

### 19.3 `start_render` validation chain

```python
def start_render(self) -> None:
    # 1. License or trial alive?
    if not self.license_manager.can_render():
        msg = tr("msg_license_expired") if self.license_manager.info \
                                    else tr("msg_need_license")
        res = QMessageBox.warning(self, APP_NAME, msg,
              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if res == QMessageBox.StandardButton.Ok:
            self.open_activate_dialog()
        return

    # 2. ffmpeg actually installed?
    if not have_ffmpeg():
        QMessageBox.critical(self, APP_NAME, tr("msg_ffmpeg_missing"))
        return

    # 3. Anything to render?
    if not self.scan.videos:
        QMessageBox.information(self, APP_NAME, tr("msg_no_videos"))
        return

    # 4. Output folder set? (audit fix)
    if not (self.store.get("output_folder") or "").strip():
        QMessageBox.warning(self, APP_NAME, tr("msg_no_output_folder"))
        return

    # 5. Don't double-start
    if self.worker and self.worker.isRunning():
        return

    # 6. Build options, sanity-check audio source
    opts = self._options_from_store()
    if opts.audio_mode in ("mp3", "mix") and not opts.audio_file and opts.audio_pool:
        opts.audio_file = opts.audio_pool[0]
    if opts.audio_mode in ("mix", "mp3", "random") \
       and not opts.audio_file and not opts.audio_pool:
        QMessageBox.information(self, APP_NAME, tr("msg_no_audio_source"))
        opts.audio_mode = "keep"

    # 7. Spawn the worker
    self.worker = RenderWorker(...)
    # ... connect 6 signals ...
    self.worker.start()
```

Each step has a **specific, translated** user-visible message. Never let
FFmpeg's opaque error bubble up to the user.

### 19.4 `closeEvent` (audit fix — the big one)

```python
def closeEvent(self, event) -> None:
    # 1. Drop the i18n subscription so a future GC doesn't fire into a dead window
    try:
        unsubscribe(self._retranslate)
    except Exception:
        pass

    # 2. If a render is in flight, disconnect ALL worker signals BEFORE
    #    asking the worker to stop. Otherwise the worker's last finished_all
    #    emit will reach _on_finished_all → QMessageBox.information(...)
    #    on a window that's already in destruction → stray popup.
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

        # 3. Now ask the worker to stop (kills its ffmpeg children)
        self.worker.stop()

        # 4. Give it 5 seconds, then proceed regardless. Don't hang the UI.
        self.worker.wait(5000)

    super().closeEvent(event)
```

The `try/except (TypeError, RuntimeError)` covers both:

- `TypeError` — signal had no connections
- `RuntimeError` — sender already deleted

…both of which can happen depending on the order of Qt's deferred deletion.

### 19.5 Exercises

1. Add a hidden **Log panel** that fills with everything emitted by
   `worker.log`. Toggle via `Ctrl+L`.
2. Add a system-tray icon so minimising sends to tray. Hint:
   `QSystemTrayIcon`.
3. Add a **drag-drop video files onto the window** mechanism that adds
   them to the queue without changing `input_folder`.

---

## 20. Lesson 16 — Admin CLI

### 20.1 `--init` (one-time)

```bash
python tools/generate_key.py --init
```

What it does:

1. Generates a fresh Ed25519 keypair.
2. Writes `keys/admin_private.pem` (PEM, PKCS8, no encryption, mode `0600`).
3. Writes `keys/admin_public.txt` (base64url of the 32-byte raw public key).
4. **Patches** `app/core/licensing.py` so its `PUBLIC_KEY_B64URL = "..."` line
   matches the new public key.
5. Reminds the admin to commit the patched file (+ `admin_public.txt`).

Code excerpt:

```python
def cmd_init(args):
    if PRIV_PATH.exists() and not args.force:
        print(f"private key already exists: {PRIV_PATH}", file=sys.stderr)
        print("re-run with --force to overwrite (you will invalidate every existing key!)",
              file=sys.stderr)
        return 2
    sk, pk = licensing.generate_keypair()
    licensing.save_private_key(sk, PRIV_PATH)
    pub_b64 = licensing.public_key_b64url(pk)
    PUB_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUB_PATH.write_text(pub_b64 + "\n", encoding="utf-8")
    src = licensing.patch_public_key_in_source(pub_b64)
    print(f"wrote private key  : {PRIV_PATH}")
    print(f"wrote public key   : {PUB_PATH}")
    print(f"patched embedded pk in: {src}")
    return 0
```

### 20.2 `mint`

```bash
# perpetual Pro key with 3 machine slots
python tools/generate_key.py mint \
    --name "Sok Dara" --email dara@example.com \
    --type pro --max-machines 3

# 1-year Standard key
python tools/generate_key.py mint \
    --name "Lim Chenda" --email chenda@example.com \
    --type standard --expires 2027-05-22 --max-machines 1

# feature-restricted Standard key (no GPU, no audio mix)
python tools/generate_key.py mint \
    --name "Test" --email t@x.com --type standard \
    --feature merge --feature cut_plus --feature text
```

Side effects:

- Prints the key to stdout.
- Writes a copy to `keys-issued/<kid>.txt`.
- Appends a JSONL row to `keys-issued/log.jsonl` (your audit log).

### 20.3 `verify` (three input modes — audit fix)

```bash
# 1. Positional argument (good for one-shot)
python tools/generate_key.py verify "PNNHA1.eyJ..."

# 2. Stdin (good for piping)
echo "PNNHA1.eyJ..." | python tools/generate_key.py verify -

# 3. File path (good for archived keys)
python tools/generate_key.py verify /path/to/key.txt
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | valid signature, JSON payload printed to stdout |
| `1` | parsed but signature invalid |
| `2` | malformed input or no key provided |

### 20.4 Exercises

1. Add `--bulk` mode: `mint --bulk customers.csv` reads name/email/type
   per line and mints one key per row, archiving each to
   `keys-issued/<kid>.txt`.
2. Add `revoke <kid>` that appends to a `keys-issued/revoked.txt` and
   build the app to **check that file in `verify_key`** (would require an
   online sync or a shipped revocation list update).

---

## 21. Development workflow

### 21.1 Daily loop

```bash
git checkout main
git pull origin main

git checkout -b devin/$(date +%s)-feature-something

# ... edit, run, iterate ...
python main.py

# ... lint (optional) ...
python -m pyflakes app/

# ... commit + push + PR ...
git add app/...
git commit -m "Add feature X"
git push -u origin HEAD
# open a PR on GitHub
```

### 21.2 Smoke-test checklist before opening a PR

1. App boots without exceptions (`python main.py`).
2. Switch language to ខ្មែរ → all top-bar / Settings / dialogs translate.
3. Set Input + Output folders → table populates.
4. Click START on a 2-clip queue → both finish, "Done" dialog appears.
5. Close mid-render → ffmpeg children die within 5s, no stray dialog.
6. Open Activate → paste a freshly-minted key → badge updates.
7. Settings → tabs read "General / Effects / Audio & Encoder".

### 21.3 Useful debug snippets

```python
# Log every signal emit from the worker
self.worker.item_started.connect(lambda r: print(f"started row={r}"))
self.worker.log.connect(print)
```

```bash
# Re-run the renderer outside Qt for FFmpeg debugging
python -c "
from pathlib import Path
from app.core.ffmpeg_runner import RenderOptions, build_render_command
from app.core.hardware import resolve_encoder
o = RenderOptions(output_folder=Path('/tmp/out'), overlay_text='Hi 100%',
                  show_timer=True, blur_background=True, encoder=resolve_encoder('cpu'))
print(' '.join(build_render_command(Path('/tmp/in.mp4'), Path('/tmp/out.mp4'), o)))
"
```

### 21.4 Lint / typecheck (optional but recommended)

```bash
pip install pyflakes mypy
python -m pyflakes app/
python -m mypy --strict app/
```

This project doesn't (yet) configure `pyproject.toml`. PRs adding either
are welcome.

---

## 22. Packaging a Windows `.exe` with PyInstaller

### 22.1 Install

```powershell
pip install pyinstaller
```

### 22.2 `pnnha_vshort.spec`

```python
# pnnha_vshort.spec
# Run with:  pyinstaller --clean pnnha_vshort.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/i18n',  'app/i18n'),
        ('assets',    'assets'),
    ],
    hiddenimports=[
        'cv2',
        'PIL.ImageDraw', 'PIL.ImageFilter', 'PIL.ImageFont',
        'cryptography.hazmat.primitives.asymmetric.ed25519',
    ],
    excludes=['tkinter'],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='PnnhaVShort',
    debug=False,
    strip=False, upx=True,
    runtime_tmpdir=None,
    console=False,                         # ← no black console window
    icon='assets/app.ico',
)
```

### 22.3 Build

```powershell
pyinstaller --clean pnnha_vshort.spec
dir dist\
# dist\PnnhaVShort.exe ← deliverable
```

### 22.4 Bundle FFmpeg next to the EXE

PyInstaller bundles Python code only. FFmpeg is a **separate executable**.

**Option A: require the customer to install ffmpeg + PATH** (smaller
download). The app already handles this via `shutil.which("ffmpeg")` and
shows `msg_ffmpeg_missing`.

**Option B: ship ffmpeg.exe alongside `PnnhaVShort.exe`** (turnkey):

1. Download `ffmpeg-release-essentials.zip` from <https://www.gyan.dev/ffmpeg/builds/>.
2. Extract `ffmpeg.exe` and `ffprobe.exe`.
3. Copy them into `dist\`.
4. Patch `app/core/hardware.py` so it looks next to `sys.executable` first:

```python
import sys
def _exe_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))

def ffmpeg_available() -> bool:
    local = _exe_dir() / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if local.is_file(): return True
    return shutil.which("ffmpeg") is not None
```

### 22.5 Custom icon

Drop a 256×256 multi-resolution `.ico` at `assets/app.ico` and reference
it in the spec. If you only have a PNG:

```bash
convert app.png -define icon:auto-resize=16,32,48,64,128,256 app.ico
```

(Requires ImageMagick.)

### 22.6 Resulting deliverable layout

```
dist/
├── PnnhaVShort.exe         ← double-click to launch
├── ffmpeg.exe              ← optional (Option B)
├── ffprobe.exe             ← optional (Option B)
└── README-customer.md      ← short install + license guide
```

### 22.7 Code-signing (optional, recommended)

Unsigned executables trigger Windows SmartScreen ("Windows protected your
PC") on first launch. To suppress this:

1. Get a code-signing certificate (Sectigo, DigiCert, or EV cert for
   instant trust).
2. Run `signtool sign /f cert.pfx /p PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\PnnhaVShort.exe`.

EV certs cost ~$300/year and remove SmartScreen warnings immediately;
non-EV certs cost ~$70 but accumulate reputation over downloads.

### 22.8 macOS `.app` and Linux AppImage

Not currently maintained — PRs welcome. The spec file would need to be
duplicated with `console=False` and the right `icon=` for each platform.

---

## 23. Distributing to customers

### 23.1 Build → package → ship

```
1. Bump app/__init__.py __version__
2. python tools/generate_key.py --init   (ONLY the first time, not per release!)
3. pyinstaller --clean pnnha_vshort.spec
4. (optional) Option B: copy ffmpeg.exe + ffprobe.exe into dist\
5. Zip dist\  →  pnnha-vshort-1.0.0.zip
6. Upload to your distribution channel (Google Drive, Telegram, your site)
```

### 23.2 What the customer receives

```
pnnha-vshort-1.0.0.zip
├── PnnhaVShort.exe         (~80 MB)
├── ffmpeg.exe              (~100 MB)  [Option B only]
├── ffprobe.exe             (~100 MB)  [Option B only]
└── README-customer.md
```

### 23.3 Sample `README-customer.md`

```markdown
# Pnnha V-Short — Quick start

1. Right-click the ZIP → Extract All → pick a folder you can write to
   (e.g. `C:\PnnhaVShort\`).
2. Double-click `PnnhaVShort.exe`.
3. Click **Settings** → set your Input and Output folders → close Settings.
4. Click **START**.

Free trial lasts 30 days. To buy a license, contact @AdminKh on Telegram
and send your **Hardware ID** (visible in **License** dialog).
```

### 23.4 Key delivery workflow

```
1. Customer pays.
2. You: python tools/generate_key.py mint \
            --name "Sok Dara" --email dara@example.com \
            --type pro --expires 2027-05-22 --max-machines 2
3. Copy the PNNHA1.eyJ... line that's printed.
4. Send it to the customer (email / Telegram).
5. They paste it into Activate dialog → badge updates.
```

Your `keys-issued/log.jsonl` keeps a record of every key minted:

```json
{"issued_at":"2026-05-25T09:00:00","kid":"a1b2c3d4","name":"Sok Dara","email":"dara@example.com","type":"pro","expires":"2027-05-22","max_machines":2}
```

### 23.5 Renewals

Just mint a new key with a new `--expires`. When the customer pastes it,
`data/license.json` is overwritten with the new key + payload.

### 23.6 Refunds / revocation

The system is **offline-first**, so you can't *revoke* a key in real time.
Workarounds:

- Use **short expiries** (annual) so abuse self-terminates.
- For abuse, ask the customer to send their Hardware ID. Mint a key that
  binds to a *different* hardware ID — the app refuses to load it on the
  abuser's machine.
- Add a **revocation list** updated via the app's auto-update mechanism
  (out of scope of this tutorial).

---

## 24. Common extension tasks

### 24.1 Add a new audio mode (e.g. "fade-mix")

1. **i18n**: add `"settings_audio_fade_mix"` to both EN and KH tables.
2. **SettingsStore**: `audio_mode` already accepts arbitrary strings, but
   document `"fade_mix"` as a valid value in `DEFAULTS`'s comment.
3. **SettingsDialog**: add `("fade_mix", "settings_audio_fade_mix")` to
   the combobox `[code, key]` pairs and wire it to `audio_mode`.
4. **FFmpegRunner**: extend `_audio_args` with a new branch:

```python
elif opts.audio_mode == "fade_mix" and opts.audio_file:
    inputs += ["-i", str(opts.audio_file)]
    mapping += [
        "-filter_complex_extra",
        "[AUDIO:a]afade=t=in:st=0:d=2,afade=t=out:st=27:d=2[a1];"
        "[0:a][a1]amix=inputs=2:duration=shortest[aout]",
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
    ]
```

5. **RenderWorker**: nothing to change — it just forwards `opts.audio_mode`.
6. **Preview**: nothing to change (preview is video-only).

### 24.2 Add a new language (e.g. French)

1. **i18n**: add a `"fr"` key to `_STRINGS` with every key copied from
   `"en"` and translated.
2. **i18n**: add `("fr", "Français")` to `available_languages()`.
3. **SettingsDialog**: nothing to change — it already iterates
   `available_languages()`.
4. Test by setting `data/settings.json`'s `"language": "fr"` and relaunching.

### 24.3 Add a new encoder (e.g. HEVC NVENC)

See [§9.4 above](#9-lesson-5-hardware).

### 24.4 Add a new license type (e.g. "team")

1. **licensing.py**: add `"team"` to `LICENSE_TYPES`.
2. **tools/generate_key.py**: nothing to change — the CLI already accepts
   any value in `LICENSE_TYPES`.
3. **(optional) UI**: surface a "Team license" label in the trial badge.

### 24.5 Add a new filter (e.g. sharpening)

1. **SettingsStore**: add `"sharpen": False` to `DEFAULTS`.
2. **SettingsDialog**: add a `QCheckBox` in the Effects tab → wire to
   `sharpen` key.
3. **FFmpegRunner**: in `build_filter_graph`, before the final
   `format=yuv420p`, optionally insert a sharpening filter:

```python
if opts.sharpen:
    parts.append(f"[{cur}]unsharp=5:5:1.0:5:5:0.0[vsh]")
    cur = "vsh"
```

4. **Preview**: optionally mirror the effect in `apply_preview_effects`
   using `PIL.ImageFilter.UnsharpMask`.

---

## 25. Troubleshooting

### 25.1 Symptom → cause → fix

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| App boots, but main window is invisible / blank | DPI / Wayland issue | On Linux: `export QT_QPA_PLATFORM=xcb` before `python main.py`. On Windows: lower display scaling to 100% briefly. |
| "ffmpeg not found" warning at startup | FFmpeg not on PATH | Install FFmpeg, restart your shell, verify `ffmpeg -version` works. |
| Render fails immediately with "ffmpeg exit 1" | FFmpeg can't decode the input | Run the printed FFmpeg command manually to see stderr. Likely a codec your build lacks. |
| Render starts but every clip ends with "ffmpeg exit 1" on NVENC | No Nvidia driver / no Nvidia GPU | Switch encoder to **CPU** in Settings. |
| Output video has no audio | `audio_mode=keep` but source has no audio track | Switch to **Mute** or **MP3**. |
| Output video has "Stray %" warning in log + missing overlay text | (Pre-audit build) | Pull latest `main` — `expansion=none` is now on the user-text drawtext. |
| Khmer text in UI shows boxes | Khmer font missing | Ubuntu: `apt install fonts-noto-core`. Windows: install Khmer language pack. |
| Settings tab labelled "Audio_Encoder" with underline on E | (Pre-audit build) | Pull latest `main` — `&` is now escaped as `&&`. |
| Activation says "invalid signature" | The app build doesn't match the private key that signed | Either rebuild after `--init`, or get a key signed by the matching keypair. |
| `data/settings.json` is invalid after a crash | (Pre-audit build) | Atomic writes are now in place. If you see a `.tmp` file next to it, delete the `.tmp`. |
| Closing window mid-render hangs Python | (Pre-audit build) | Pull latest — `closeEvent` disconnects signals and bounds `worker.wait(5000)`. |
| "All jobs finished" dialog appears AFTER the window is closed | (Pre-audit build) | Same fix as above. |
| Activate dialog accepts the key but `data/license.json` doesn't appear | Path-permission issue | Make sure the install folder is writable; on Windows don't install to `Program Files`. |
| Preview is black | First frame is genuinely black (capture device intro) | Preview seeks to frame `min(30, total // 4)`. If your video is shorter than 30 frames, change that to `total // 2`. |

### 25.2 Verbose FFmpeg logging

The worker emits FFmpeg's stderr line-by-line on the `log` signal. To see
it, connect it to `print` in `MainWindow.__init__`:

```python
self.worker.log.connect(print)
```

Or rebuild the command manually:

```python
from app.core.ffmpeg_runner import build_render_command, RenderOptions
from app.core.hardware import resolve_encoder
from pathlib import Path
cmd = build_render_command(
    Path("in.mp4"), Path("out.mp4"),
    RenderOptions(output_folder=Path("."), overlay_text="Hi 100%",
                  encoder=resolve_encoder("cpu")),
)
print(" ".join(cmd))    # paste into a terminal to see full FFmpeg output
```

### 25.3 "I bricked my license file"

```bash
# nuke just the license; trial remains
rm data/license.json

# nuke everything; fresh start
rm -rf data/
```

Settings will reset to defaults; trial clock restarts. Activation needs
the original key.

---

## 26. Audit lessons

Ten transferrable lessons from PR #2 (the audit pass):

1. **Atomic writes always.** Every JSON file uses `tmp + os.replace`. A
   `Ctrl+C` mid-write no longer corrupts user state.
2. **`expansion=none` for user drawtext.** Never let user content into a
   filter that interprets `%`. Reserve expanded drawtext for built-in
   expressions only (timer's `%{pts\:hms}`).
3. **Concat-demuxer apostrophe escape.** Use `'\''` for any quote in a
   path — the demuxer's mini-shell parser doesn't tolerate raw `'`.
4. **Pre-flight validation in BOTH UI and worker.** UI gives a friendly
   dialog; worker also rejects bad state in case a future caller bypasses
   the UI.
5. **Disconnect signals BEFORE stopping the worker.** Otherwise the
   worker's last `finished_all` fires into a destroying window and pops
   stray dialogs.
6. **`unsubscribe()` on close.** Without it, the i18n subscriber list
   holds a stale callback to a destroyed window, leaking memory and
   making future `set_language()` calls noisy.
7. **Pillow API compatibility.** `try/except TypeError` around
   `ImageFont.load_default(size=...)` because Pillow 10 added the param.
8. **Placeholder public-key guard.** A `is_placeholder_public_key()`
   check at boot warns the admin that the dev key is still embedded —
   never ship that build.
9. **CLI `verify` accepts stdin, file, or arg.** Pipelines and scripts
   now work without shell-escaping a 500-char key.
10. **Qt mnemonic `&&` escape.** Every label with a literal `&` must
    double it or Qt will silently consume one.

---

## 27. Glossary KH ↔ EN

| English | ខ្មែរ | Notes |
|---------|------|-------|
| Render | បកប្រែវីដេអូ | The act of running ffmpeg to produce an output file |
| Encoder | អ្នកបំលែង / Encoder | The codec implementation (NVENC, x264, ...) |
| Frame | ស៊ុម / Frame | A single image inside a video |
| Filter graph | ដ្យាក្រាមតម្រង | The FFmpeg `-filter_complex` argument |
| Drawtext | គូសអក្សរ | The FFmpeg filter that paints text onto video |
| Expansion | ការវាយតម្លៃ | drawtext's `%{...}` evaluation mode |
| Atomic write | សរសេរដោយរលូន | `tmp + os.replace` pattern |
| Signal/slot | សញ្ញា/ស្លុត | Qt's event/handler mechanism |
| Thread | ខ្សែ​ដំណើរការ | OS thread of execution |
| Worker | កម្មកររង | The background thread that runs ffmpeg |
| Mnemonic | គន្លឹះអក្ខរក្រម | The `&` shortcut indicator in Qt labels |
| Activation | ការដំឡើងសិទ្ធិ | Pasting a license key into the app |
| Hardware ID | លេខសម្គាល់ឧបករណ៍ | The SHA-256-derived machine fingerprint |
| Keypair | គូកូនសោ | The Ed25519 private + public key |
| Sign / verify | ចុះហត្ថលេខា / ផ្ទៀងផ្ទាត់ | The two halves of digital signing |
| Trial | សាកល្បង | The 30-day free use period |
| License | លិខិតអនុញ្ញាត | A signed activation token |
| Concat demuxer | តម្រងភ្ជាប់ | FFmpeg's lossless-merge mechanism |
| Subprocess | ដំណើរការរង | A child OS process (each ffmpeg invocation) |
| Spec file | ឯកសារកំណត់ | The PyInstaller `.spec` build config |

---

## 28. Appendix — file & command reference

### 28.1 Every Python file at a glance

| File | LOC | Purpose |
|------|-----|---------|
| `main.py` | ~30 | Bootstrap order |
| `app/__init__.py` | 6 | Constants |
| `app/i18n/__init__.py` | ~265 | EN+KH tables + subscribe API |
| `app/core/settings_store.py` | ~75 | `data/settings.json` |
| `app/core/trial.py` | ~55 | `data/trial.json` |
| `app/core/hardware.py` | ~70 | Encoder detection |
| `app/core/video_scanner.py` | ~85 | `scan_folder()` |
| `app/core/ffmpeg_runner.py` | ~305 | Filter graph + command builders |
| `app/core/render_worker.py` | ~283 | `QThread` + `ThreadPoolExecutor` |
| `app/core/preview.py` | ~155 | OpenCV + PIL effects |
| `app/core/licensing.py` | ~440 | Ed25519 + LicenseManager |
| `app/ui/styles.py` | ~215 | QSS stylesheet |
| `app/ui/video_table.py` | ~125 | `QAbstractTableModel` + filter |
| `app/ui/activate_dialog.py` | ~90 | License paste dialog |
| `app/ui/settings_dialog.py` | ~200 | Tabbed settings |
| `app/ui/main_window.py` | ~585 | Everything wires here |
| `tools/generate_key.py` | ~200 | Admin CLI |

Total: ~3,200 lines of Python.

### 28.2 Every important command

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run
python main.py

# License: init keypair (ONE time, never again)
python tools/generate_key.py --init

# License: mint a key
python tools/generate_key.py mint \
    --name "<NAME>" --email "<EMAIL>" --type pro --expires 2027-12-31 --max-machines 1

# License: verify a key
python tools/generate_key.py verify "PNNHA1.eyJ..."
python tools/generate_key.py verify - < key.txt
python tools/generate_key.py verify /path/to/key.txt

# Lint
python -m pyflakes app/

# Package for Windows
pyinstaller --clean pnnha_vshort.spec

# Code-sign (optional)
signtool sign /f cert.pfx /p PASS /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\PnnhaVShort.exe
```

### 28.3 Reading order for new contributors

If you're new and want to grok the whole thing, read in this order:

1. **`main.py`** — see how the app boots.
2. **`app/__init__.py`** — see the constants.
3. **`app/i18n/__init__.py`** — see how strings are looked up and live-switched.
4. **`app/core/settings_store.py`** — see the persistence pattern (then
   `trial.py` and `licensing.py` reuse it).
5. **`app/core/video_scanner.py`** — see the input data model.
6. **`app/core/ffmpeg_runner.py`** — the heart. Read 8.1–8.7 of this
   tutorial alongside.
7. **`app/core/render_worker.py`** — how the heart is driven concurrently.
8. **`app/core/licensing.py`** — orthogonal to the pipeline.
9. **`app/ui/main_window.py`** — bottom-up: read `_build_top_bar`,
   `_build_preview`, `_build_right_pane`, then `start_render`, then
   `closeEvent`.
10. **`tools/generate_key.py`** — the admin side. Now you can mint and
    test keys.

### 28.4 Where things are written on disk

| Path | What |
|------|------|
| `data/settings.json` | Every Settings dialog field. |
| `data/trial.json` | Trial start date + last-saved timestamp. |
| `data/license.json` | Activation: key + payload + hardware ID + activated_at. |
| `data/*.tmp` | A `.tmp` file briefly exists during atomic writes. If you see one persistently, the rename failed — investigate. |
| `keys/admin_private.pem` | **Admin only.** Never committed. Protect this file with your life. |
| `keys/admin_public.txt` | The public key. Committed to source. |
| `keys-issued/<kid>.txt` | One file per minted key. Useful for re-sending. |
| `keys-issued/log.jsonl` | Append-only audit log of every mint. |
| `dist/PnnhaVShort.exe` | PyInstaller output (Windows). |

### 28.5 Where to ask for help / រក​ជំនួយ

- Open a GitHub issue: <https://github.com/somalaymetamusk-coder/panha-vshort/issues>
- Telegram: `@AdminKh`

---

## License / ច្បាប់​សិទ្ធ

The application itself is © HORN LYHENG (Admin-Kh) 2026.
This developer tutorial document is part of the same repository and
shares its license.

— សូមរីករាយ​ការ​អភិវឌ្ឍ! Happy hacking!
