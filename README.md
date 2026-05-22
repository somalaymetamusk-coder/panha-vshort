# Pnnha V-Short

A PyQt6 desktop application for batch video processing — built to mirror the
look-and-feel of V-Short 3.2 by HORN LYHENG (Admin-Kh).

Features
--------
* Bilingual UI — English ↔ ខ្មែរ (toggle in **Settings**)
* Batch **Merge** of detected clips
* **Cut-plus** — split each clip into N equal parts
* **Rename-plus** — bulk rename with prefix + zero-padded index
* Add **Logo**, **Text** and **Timer** overlays
* **Live preview** (renders the first frame of the selected clip with effects applied)
* **Blur background** mode for vertical videos
* Audio modes — **Mix**, **Mute**, **Random**, **MP3** (replace with a folder of MP3s)
* Hardware acceleration — **Nvidia NVENC**, **AMD AMF**, or **CPU x264**
* **CPU limit** slider (caps the number of ffmpeg worker threads per job)
* **Threads Render** — process several clips in parallel
* 30-day **Free Trial** counter persisted to disk

Requirements
------------
* Python ≥ 3.10
* ffmpeg available on `PATH` (Windows: download from <https://www.gyan.dev/ffmpeg/builds/>
  and add the `bin` folder to `PATH`)
* `pip install -r requirements.txt`

Run
---
```bash
python main.py
```

Project layout
--------------
```
pnnha_vshort/
├── main.py                  # entry point
├── app/
│   ├── i18n/                # English + Khmer string tables
│   ├── core/                # ffmpeg pipeline, scanner, trial, hardware
│   └── ui/                  # styles, sidebar, table, preview, dialogs
├── assets/                  # logo + icons
└── data/                    # settings.json + trial.json (created at runtime)
```

© All rights reserved by HORN LYHENG (Admin-Kh) 2026
