"""English + Khmer string tables.

Usage:
    from app.i18n import tr, set_language
    set_language("km")
    label = tr("start")
"""
from __future__ import annotations

from typing import Dict

_STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        # Top bar
        "home": "HOME",
        "settings": "Settings",
        "help": "Help",
        "app_title": "Pnnha V-Short",
        "trial_remaining": "Trial: {days} Day",
        "trial_expired": "Trial expired",
        "licensed_to": "Licensed: {label}",
        "license_expired": "License expired",
        "activate_license": "Activate license",

        # Licensing dialog
        "lic_dialog_title": "License",
        "lic_paste_key": "Paste your license key below:",
        "lic_current_status": "Current status",
        "lic_hardware_id": "Hardware ID",
        "lic_activate": "Activate",
        "lic_deactivate": "Deactivate",
        "lic_activated_ok": "Activated for {name}.",
        "lic_activate_failed": "Activation failed: {err}",
        "lic_confirm_deactivate": "Remove the activated license from this machine?",
        "settings_licensing": "Licensing",

        # Main panel
        "detected_videos": "Detected Videos",
        "output": "Output",
        "filter_name": "Filter name...",
        "all": "All",
        "col_index": "#",
        "col_name": "Name",
        "col_audio": "Audio",
        "col_logo": "Logo",
        "col_status": "Status",
        "status_ready": "Ready",
        "status_running": "Running",
        "status_done": "Done",
        "status_error": "Error",
        "status_queued": "Queued",
        "stats_summary": "{videos} video(s), {audios} audio file(s), {logos} logo file",

        # Live preview
        "live_preview": "Live preview",
        "preview_info": "{size} - {srcw} x {srch} --> - {dstw} x {dsth}",
        "no_preview": "No video selected",

        # Buttons
        "start": "START",
        "stop": "STOP",
        "reload": "Reload",
        "browse": "Browse...",
        "ok": "OK",
        "cancel": "Cancel",
        "apply": "Apply",
        "close": "Close",
        "threads_render": "Threads Render",

        # Help menu
        "help_about": "About",
        "help_check_updates": "Check updates",
        "help_contact": "Contact Admin-Kh",

        # Settings dialog
        "settings_title": "Settings",
        "settings_language": "Language",
        "settings_input_folder": "Input folder",
        "settings_output_folder": "Output folder",
        "settings_audio_folder": "Audio folder (MP3)",
        "settings_logo_file": "Logo file",
        "settings_overlay_text": "Overlay text",
        "settings_show_timer": "Show timer overlay",
        "settings_blur_bg": "Blur background (vertical pad)",
        "settings_merge": "Merge all clips into one",
        "settings_cut_plus": "Cut each clip into N parts",
        "settings_cut_parts": "Parts per clip",
        "settings_rename_prefix": "Rename prefix",
        "settings_rename_start": "Rename start index",
        "settings_audio_mode": "Audio mode",
        "settings_audio_mix": "Mix (keep + add)",
        "settings_audio_mute": "Mute",
        "settings_audio_random": "Random MP3",
        "settings_audio_mp3": "Use a specific MP3",
        "settings_audio_keep": "Keep original",
        "settings_encoder": "Encoder",
        "settings_encoder_auto": "Auto detect",
        "settings_encoder_nvenc": "Nvidia (NVENC)",
        "settings_encoder_amf": "AMD (AMF)",
        "settings_encoder_cpu": "CPU (x264)",
        "settings_cpu_limit": "CPU limit (threads per job)",
        "settings_output_format": "Output format",

        # Messages
        "msg_no_videos": "No videos in the input folder. Pick one in Settings.",
        "msg_trial_expired": "Your 30-day free trial has expired.",
        "msg_need_license": "Your trial has ended. Activate a license to keep rendering.",
        "msg_license_expired": "Your license has expired. Activate a new one to keep rendering.",
        "msg_done": "All jobs finished.",
        "msg_aborted": "Stopped by user.",
        "msg_ffmpeg_missing": "ffmpeg was not found on PATH. Please install it.",
        "footer": "© All rights reserved by HORN LYHENG (Admin-Kh) {year}",
    },
    "km": {
        "home": "ដើម",
        "settings": "កំណត់",
        "help": "ជំនួយ",
        "app_title": "Pnnha V-Short",
        "trial_remaining": "សាកល្បង៖ {days} ថ្ងៃ",
        "trial_expired": "ការសាកល្បងបានផុតកំណត់",
        "licensed_to": "មានអាជ្ញាបណ្ណ៖ {label}",
        "license_expired": "អាជ្ញាបណ្ណផុតកំណត់",
        "activate_license": "បាតួរអាជ្ញាបណ្ណ",

        "lic_dialog_title": "អាជ្ញាបណ្ណ",
        "lic_paste_key": "បិទភ្ជាប់សោអាជ្ញាបណ្ណរបស់អ្នកនៅទីនេះ៖",
        "lic_current_status": "ស្ថានភាពបច្ចុប្បន្ន",
        "lic_hardware_id": "លេខសម្គាល់ម៉ាស៊ីន",
        "lic_activate": "បាតួរ",
        "lic_deactivate": "ដកការបាតួរ",
        "lic_activated_ok": "បានបាតួរអាជ្ញាបណ្ណសម្រាប់ {name}។",
        "lic_activate_failed": "ការបាតួរបរាជ័យ៖ {err}",
        "lic_confirm_deactivate": "ដកអាជ្ញាបណ្ណចេញពីម៉ាស៊ីននេះ?",
        "settings_licensing": "អាជ្ញាបណ្ណ",

        "detected_videos": "វីដេអូដែលរកឃើញ",
        "output": "លទ្ធផល",
        "filter_name": "ច្រោះតាមឈ្មោះ...",
        "all": "ទាំងអស់",
        "col_index": "#",
        "col_name": "ឈ្មោះ",
        "col_audio": "សំឡេង",
        "col_logo": "ឡូហ្គោ",
        "col_status": "ស្ថានភាព",
        "status_ready": "រួចរាល់",
        "status_running": "កំពុងដំណើរការ",
        "status_done": "បានបញ្ចប់",
        "status_error": "បរាជ័យ",
        "status_queued": "រងចាំ",
        "stats_summary": "វីដេអូ {videos} ឯកសារសំឡេង {audios} ឡូហ្គោ {logos}",

        "live_preview": "មើលផ្ទាល់",
        "preview_info": "{size} - {srcw} x {srch} --> - {dstw} x {dsth}",
        "no_preview": "មិនទាន់ជ្រើសវីដេអូ",

        "start": "ចាប់ផ្តើម",
        "stop": "បញ្ឈប់",
        "reload": "ផ្ទុកឡើងវិញ",
        "browse": "រកមើល...",
        "ok": "យល់ព្រម",
        "cancel": "បោះបង់",
        "apply": "អនុវត្ត",
        "close": "បិទ",
        "threads_render": "ចំនួន Threads",

        "help_about": "អំពី",
        "help_check_updates": "ពិនិត្យកំណែថ្មី",
        "help_contact": "ទាក់ទង Admin-Kh",

        "settings_title": "កំណត់",
        "settings_language": "ភាសា",
        "settings_input_folder": "ថតបញ្ចូល",
        "settings_output_folder": "ថតលទ្ធផល",
        "settings_audio_folder": "ថត MP3",
        "settings_logo_file": "ឯកសារឡូហ្គោ",
        "settings_overlay_text": "អក្សរផ្ដាក់ពីលើ",
        "settings_show_timer": "បង្ហាញនាឡិកា",
        "settings_blur_bg": "ផ្ទៃខាងក្រោយព្រិល",
        "settings_merge": "បញ្ចូលគ្នាទៅជាមួយ",
        "settings_cut_plus": "កាត់វីដេអូជា N ផ្នែក",
        "settings_cut_parts": "ចំនួនផ្នែក",
        "settings_rename_prefix": "បុព្វបទប្តូរឈ្មោះ",
        "settings_rename_start": "លេខចាប់ផ្ដើម",
        "settings_audio_mode": "របៀបសំឡេង",
        "settings_audio_mix": "លាយ (រក្សា + បន្ថែម)",
        "settings_audio_mute": "បិទសំឡេង",
        "settings_audio_random": "MP3 ចៃដន្យ",
        "settings_audio_mp3": "MP3 ជាក់លាក់",
        "settings_audio_keep": "រក្សាសំឡេងដើម",
        "settings_encoder": "Encoder",
        "settings_encoder_auto": "ស្វ័យប្រវត្តិ",
        "settings_encoder_nvenc": "Nvidia (NVENC)",
        "settings_encoder_amf": "AMD (AMF)",
        "settings_encoder_cpu": "CPU (x264)",
        "settings_cpu_limit": "កំណត់ CPU (threads/job)",
        "settings_output_format": "ទម្រង់លទ្ធផល",

        "msg_no_videos": "មិនមានវីដេអូក្នុងថត។ សូមជ្រើសក្នុង Settings។",
        "msg_trial_expired": "ការសាកល្បង ៣០ ថ្ងៃបានផុតកំណត់។",
        "msg_need_license": "ការសាកល្បងបានផុត។ សូមបាតួរអាជ្ញាបណ្ណដើម្បីបន្ត។",
        "msg_license_expired": "អាជ្ញាបណ្ណរបស់អ្នកផុតកំណត់។ សូមបាតួរថ្មីដើម្បីបន្ត។",
        "msg_done": "ការងារទាំងអស់បានបញ្ចប់។",
        "msg_aborted": "បានបញ្ឈប់ដោយអ្នកប្រើ។",
        "msg_ffmpeg_missing": "មិនមាន ffmpeg ក្នុង PATH ទេ។ សូមដំឡើង។",
        "footer": "© រក្សាសិទ្ធិ HORN LYHENG (Admin-Kh) {year}",
    },
}

_current_lang = "en"
_listeners: list = []


def set_language(code: str) -> None:
    """Change the active language and notify all subscribers."""
    global _current_lang
    if code not in _STRINGS:
        raise ValueError(f"Unknown language: {code}")
    if code == _current_lang:
        return
    _current_lang = code
    for cb in list(_listeners):
        try:
            cb()
        except Exception:
            pass


def get_language() -> str:
    return _current_lang


def available_languages() -> list[tuple[str, str]]:
    return [("en", "English"), ("km", "ខ្មែរ")]


def tr(key: str, **fmt) -> str:
    """Look up *key* in the current language. Falls back to English then key."""
    table = _STRINGS.get(_current_lang, {})
    text = table.get(key) or _STRINGS["en"].get(key) or key
    if fmt:
        try:
            return text.format(**fmt)
        except Exception:
            return text
    return text


def subscribe(cb) -> None:
    """Register *cb* to be called whenever the language changes."""
    _listeners.append(cb)


def unsubscribe(cb) -> None:
    if cb in _listeners:
        _listeners.remove(cb)
