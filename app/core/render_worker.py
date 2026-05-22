"""QThread that orchestrates rendering for the queue of videos."""
from __future__ import annotations

import random
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from .ffmpeg_runner import (
    RenderOptions, build_merge_command, build_render_command,
    have_ffmpeg, video_duration,
)
from .hardware import resolve_encoder
from .video_scanner import VideoItem


class RenderWorker(QThread):
    """Runs *all* queued video items in a thread pool.

    Signals
    -------
    item_started(int)              — emitted when item at row ``index`` starts
    item_progress(int, int)        — (row, percent)
    item_finished(int, bool, str)  — (row, success, message)
    overall_progress(int)          — 0..100 across the whole queue
    finished_all()                 — every item processed (or aborted)
    log(str)                       — verbose status line for the console
    """
    item_started = pyqtSignal(int)
    item_progress = pyqtSignal(int, int)
    item_finished = pyqtSignal(int, bool, str)
    overall_progress = pyqtSignal(int)
    finished_all = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(
        self,
        items: List[VideoItem],
        opts: RenderOptions,
        threads_render: int = 3,
        merge: bool = False,
        rename_prefix: str = "video_",
        rename_start: int = 1,
        cut_parts: int = 1,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.items = items
        self.opts = opts
        self.threads_render = max(1, int(threads_render))
        self.merge = merge
        self.rename_prefix = rename_prefix
        self.rename_start = max(1, int(rename_start))
        self.cut_parts = max(1, int(cut_parts))
        self._abort = threading.Event()
        self._procs: list[subprocess.Popen] = []
        self._procs_lock = threading.Lock()

    def stop(self) -> None:
        self._abort.set()
        with self._procs_lock:
            for p in self._procs:
                try:
                    p.terminate()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    def run(self) -> None:
        if not have_ffmpeg():
            self.log.emit("ffmpeg not found")
            self.finished_all.emit()
            return

        out_dir = Path(self.opts.output_folder)
        out_dir.mkdir(parents=True, exist_ok=True)

        if self.merge and len(self.items) > 1:
            self._run_merge(out_dir)
            self.finished_all.emit()
            return

        total = len(self.items) * self.cut_parts
        done = 0
        lock = threading.Lock()

        def on_done(row: int, ok: bool, msg: str):
            nonlocal done
            with lock:
                done += 1
                pct = int(done / max(1, total) * 100)
            self.item_finished.emit(row, ok, msg)
            self.overall_progress.emit(pct)

        with ThreadPoolExecutor(max_workers=self.threads_render) as pool:
            futures: list[Future] = []
            for i, item in enumerate(self.items):
                if self._abort.is_set():
                    break
                futures.append(pool.submit(self._process_item, i, item, out_dir, on_done))
            for f in futures:
                try:
                    f.result()
                except Exception as e:
                    self.log.emit(f"task failed: {e!r}")

        self.finished_all.emit()

    # ------------------------------------------------------------------
    def _audio_choice(self, item: VideoItem) -> Optional[Path]:
        """Resolve which audio file to use for *item* given the audio mode."""
        mode = self.opts.audio_mode
        if mode == "random" and self.opts.audio_pool:
            return Path(random.choice(self.opts.audio_pool))
        if mode in ("mix", "mp3") and self.opts.audio_file:
            return Path(self.opts.audio_file)
        return None

    def _process_item(self, row: int, item: VideoItem, out_dir: Path, on_done) -> None:
        if self._abort.is_set():
            on_done(row, False, "aborted")
            return
        self.item_started.emit(row)
        try:
            # build a per-item RenderOptions copy so threads don't trample each other
            opts = RenderOptions(
                output_folder=self.opts.output_folder,
                output_format=self.opts.output_format,
                overlay_text=self.opts.overlay_text,
                show_timer=self.opts.show_timer,
                blur_background=self.opts.blur_background,
                logo_file=self.opts.logo_file,
                audio_mode=self.opts.audio_mode,
                audio_file=self._audio_choice(item),
                audio_pool=self.opts.audio_pool,
                encoder=self.opts.encoder,
                cpu_limit=self.opts.cpu_limit,
                cut_parts=self.cut_parts,
                rename_prefix=self.rename_prefix,
                rename_index=self.rename_start + row,
            )

            base_name = f"{self.rename_prefix}{(self.rename_start + row):04d}"
            ext = "." + (self.opts.output_format or "mp4").lstrip(".")

            if self.cut_parts <= 1:
                dst = out_dir / f"{base_name}{ext}"
                ok, msg = self._run_one(row, item, dst, opts, segment=None)
                on_done(row, ok, msg)
                return

            duration = video_duration(item.path) or 0.0
            if duration <= 0:
                on_done(row, False, "could not read duration")
                return
            piece = duration / self.cut_parts
            success_all = True
            messages: list[str] = []
            for p in range(self.cut_parts):
                if self._abort.is_set():
                    on_done(row, False, "aborted")
                    return
                start = p * piece
                dur = piece
                dst = out_dir / f"{base_name}_part{p + 1:02d}{ext}"
                ok, msg = self._run_one(row, item, dst, opts, segment=(start, dur))
                success_all = success_all and ok
                messages.append(msg)
                self.item_progress.emit(row, int((p + 1) / self.cut_parts * 100))
            on_done(row, success_all, "; ".join(messages))
        except Exception as e:
            on_done(row, False, repr(e))

    def _run_one(
        self,
        row: int,
        item: VideoItem,
        dst: Path,
        opts: RenderOptions,
        segment,
    ) -> tuple[bool, str]:
        cmd = build_render_command(item.path, dst, opts, cut_segment=segment)
        self.log.emit(f"$ {' '.join(map(str, cmd))}")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            with self._procs_lock:
                self._procs.append(proc)
            for line in proc.stdout or []:
                if self._abort.is_set():
                    proc.terminate()
                    break
                line = line.strip()
                if line:
                    self.log.emit(line[:240])
            proc.wait()
            with self._procs_lock:
                if proc in self._procs:
                    self._procs.remove(proc)
            if proc.returncode == 0:
                return True, f"ok -> {dst.name}"
            return False, f"ffmpeg exit {proc.returncode}"
        except Exception as e:
            return False, repr(e)

    # ------------------------------------------------------------------
    def _run_merge(self, out_dir: Path) -> None:
        self.log.emit("merge mode: combining all clips")
        for i, _ in enumerate(self.items):
            self.item_started.emit(i)
        ext = "." + (self.opts.output_format or "mp4").lstrip(".")
        dst = out_dir / f"{self.rename_prefix}merged{ext}"
        with tempfile.TemporaryDirectory() as td:
            list_path = Path(td) / "concat.txt"
            opts = RenderOptions(
                output_folder=self.opts.output_folder,
                output_format=self.opts.output_format,
                overlay_text=self.opts.overlay_text,
                show_timer=self.opts.show_timer,
                blur_background=self.opts.blur_background,
                logo_file=self.opts.logo_file,
                audio_mode=self.opts.audio_mode,
                audio_file=self.opts.audio_file,
                audio_pool=self.opts.audio_pool,
                encoder=self.opts.encoder,
                cpu_limit=self.opts.cpu_limit,
            )
            cmd = build_merge_command([it.path for it in self.items], dst, opts, list_path)
            self.log.emit(f"$ {' '.join(map(str, cmd))}")
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                with self._procs_lock:
                    self._procs.append(proc)
                for line in proc.stdout or []:
                    if self._abort.is_set():
                        proc.terminate()
                        break
                    if line.strip():
                        self.log.emit(line.strip()[:240])
                proc.wait()
                with self._procs_lock:
                    if proc in self._procs:
                        self._procs.remove(proc)
                ok = proc.returncode == 0
                for i, _ in enumerate(self.items):
                    self.item_finished.emit(i, ok, "merged" if ok else f"exit {proc.returncode}")
                self.overall_progress.emit(100 if ok else 0)
            except Exception as e:
                for i, _ in enumerate(self.items):
                    self.item_finished.emit(i, False, repr(e))
