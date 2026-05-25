"""Render the first frame of a video with the overlay effects for live preview."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont


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
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    # last resort — the bitmap default font (size is ignored).
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10
    except TypeError:
        return ImageFont.load_default()


def _font_height(font: ImageFont.ImageFont) -> int:
    """Return a usable height in pixels for *font* across Pillow versions."""
    size = getattr(font, "size", None)
    if isinstance(size, (int, float)):
        return int(size)
    try:
        bbox = font.getbbox("Ag")
        return int(bbox[3] - bbox[1])
    except Exception:
        return 16


def first_frame(path: Path) -> Optional[Image.Image]:
    if not path or not Path(path).is_file():
        return None
    cap = cv2.VideoCapture(str(path))
    try:
        # seek a fraction in so we don't grab a black frame
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total > 30:
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(30, total // 4))
        ok, frame = cap.read()
        if not ok or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = cap.read()
        if not ok or frame is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    finally:
        cap.release()


def apply_preview_effects(
    img: Image.Image,
    *,
    blur_background: bool = False,
    overlay_text: str = "",
    show_timer: bool = False,
    logo_path: Optional[Path] = None,
    target_w: int = 360,
    target_h: int = 640,
) -> Image.Image:
    """Return a preview-sized image with the same effects the renderer applies."""
    src = img.convert("RGBA")

    if blur_background:
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
        bg = src.copy()
        bg_ratio = max(target_w / bg.width, target_h / bg.height)
        bg = bg.resize((int(bg.width * bg_ratio), int(bg.height * bg_ratio)))
        bg = bg.crop((
            (bg.width - target_w) // 2,
            (bg.height - target_h) // 2,
            (bg.width - target_w) // 2 + target_w,
            (bg.height - target_h) // 2 + target_h,
        ))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=18))
        canvas.paste(bg, (0, 0))

        fg = src.copy()
        fg_ratio = target_w / fg.width
        fg = fg.resize((target_w, int(fg.height * fg_ratio)))
        if fg.height > target_h:
            fg_ratio = target_h / fg.height
            fg = fg.resize((int(fg.width * fg_ratio), target_h))
        canvas.paste(fg, ((target_w - fg.width) // 2, (target_h - fg.height) // 2), fg)
        out = canvas
    else:
        ratio = min(target_w / src.width, target_h / src.height)
        new_w = max(1, int(src.width * ratio))
        new_h = max(1, int(src.height * ratio))
        resized = src.resize((new_w, new_h))
        out = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
        out.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2), resized)

    if logo_path and Path(logo_path).is_file():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            lw = target_w // 5
            ratio = lw / logo.width
            logo = logo.resize((lw, max(1, int(logo.height * ratio))))
            out.paste(logo, (10, 10), logo)
        except Exception:
            pass

    draw = ImageDraw.Draw(out)
    if overlay_text:
        font = _try_load_font(max(14, target_w // 18))
        fh = _font_height(font)
        tw = draw.textlength(overlay_text, font=font)
        x = (target_w - int(tw)) // 2
        y = target_h - fh - 24
        pad = 8
        draw.rectangle(
            (x - pad, y - pad // 2, x + int(tw) + pad, y + fh + pad // 2),
            fill=(0, 0, 0, 140),
        )
        draw.text((x, y), overlay_text, font=font, fill=(255, 255, 255, 255))

    if show_timer:
        font = _try_load_font(max(12, target_w // 22))
        fh = _font_height(font)
        s = "00:00:01"
        tw = draw.textlength(s, font=font)
        pad = 6
        draw.rectangle((10, target_h - fh - 14,
                        10 + int(tw) + pad * 2, target_h - 4),
                       fill=(0, 0, 0, 140))
        draw.text((10 + pad, target_h - fh - 10), s,
                  font=font, fill=(255, 255, 0, 255))

    return out.convert("RGB")


def pil_to_qpixmap(img: Image.Image):
    """Convert a PIL image to a QPixmap (lazy import so the worker can be used headless)."""
    from PyQt6.QtGui import QImage, QPixmap
    rgb = img.convert("RGB")
    data = rgb.tobytes("raw", "RGB")
    qimg = QImage(data, rgb.width, rgb.height, rgb.width * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())
