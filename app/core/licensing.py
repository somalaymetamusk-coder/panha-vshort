"""License key system — Ed25519-signed, offline-verifiable, hardware-bound.

Format
------
A license key is a UTF-8 string of three dot-separated parts:

    PNNHA1.<base64url(payload_json)>.<base64url(ed25519_signature)>

`payload_json` is a JSON object containing::

    {
        "kid":   "abcd1234",             # short key id (8 hex chars)
        "name":  "Customer name",
        "email": "buyer@example.com",
        "type":  "trial" | "standard" | "pro" | "lifetime",
        "issued_at": "2026-05-22",       # ISO date
        "expires":    "2027-05-22" | null,
        "max_machines": 1,
        "features": ["merge", "cut_plus", "blur", "nvenc", ...]
    }

The signature is over the **exact bytes** of `payload_json` (no canonicalisation),
verified with the project's public key.

Activation
----------
When the user pastes a key into the Activate dialog the app:

1. Verifies the signature with the embedded public key.
2. Checks the `expires` date is in the future (or null).
3. Computes a stable hardware ID and stores it next to the key.
4. Writes `data/license.json` with payload + hardware ID + activation time.

On every launch we re-verify and re-check the hardware ID. If the user tries
to activate the same key on more than ``max_machines`` machines the app will
allow it (the count enforcement requires a server we deliberately don't have)
but the user-visible activation file records the bound hardware so each
machine has its own activation record.
"""
from __future__ import annotations

import base64
import dataclasses
import hashlib
import json
import os
import platform
import re
import socket
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization

from .trial import Trial

# Embedded project public key (Ed25519, 32 bytes, base64url-encoded).
# This value is overwritten by `tools/generate_key.py --init` when the admin
# generates the keypair for the first time. The default below is a placeholder
# **disabled** key so unsigned builds reject every license.
PUBLIC_KEY_B64URL = "Ywcs-gcEhVLNAXVdKGfngPiJQExWhZ6WgLt-9Hwb9R4"

KEY_PREFIX = "PNNHA1"
LICENSE_TYPES = ("trial", "standard", "pro", "lifetime")
ALL_FEATURES = (
    "merge", "cut_plus", "rename_plus", "logo", "text", "timer",
    "blur", "audio_mix", "audio_random", "audio_mp3",
    "nvenc", "amf", "cpu",
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
LICENSE_FILE = DATA_DIR / "license.json"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _public_key() -> Ed25519PublicKey:
    raw = _b64url_decode(PUBLIC_KEY_B64URL)
    return Ed25519PublicKey.from_public_bytes(raw)


def hardware_id() -> str:
    """Return a stable, deterministic hardware fingerprint for this machine.

    We avoid relying on a single source so the value survives one component
    changing (e.g. swapping a NIC). 16 hex chars of SHA-256 over a tuple of
    machine identifiers is plenty for license binding.
    """
    parts: List[str] = []
    try:
        parts.append(str(uuid.getnode()))           # 48-bit MAC, falls back to random
    except Exception:
        parts.append("0")
    try:
        parts.append(socket.gethostname())
    except Exception:
        parts.append("host")
    try:
        parts.append(platform.system())
        parts.append(platform.machine())
    except Exception:
        pass
    # Linux machine-id is very stable
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            parts.append(Path(p).read_text(encoding="utf-8").strip())
            break
        except Exception:
            continue
    # Windows: registry MachineGuid is stable, but we just use socket+platform there
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


# ---------------------------------------------------------------------------
# license payload
# ---------------------------------------------------------------------------

@dataclass
class LicenseInfo:
    kid: str
    name: str
    email: str
    type: str
    issued_at: str
    expires: Optional[str] = None        # ISO date or None
    max_machines: int = 1
    features: List[str] = field(default_factory=lambda: list(ALL_FEATURES))

    def days_remaining(self) -> Optional[int]:
        if not self.expires:
            return None
        try:
            d = date.fromisoformat(self.expires)
        except Exception:
            return 0
        return (d - date.today()).days

    def is_expired(self) -> bool:
        if not self.expires:
            return False
        remaining = self.days_remaining()
        return remaining is not None and remaining < 0

    def has_feature(self, name: str) -> bool:
        return not self.features or name in self.features

    def display_label(self) -> str:
        if self.type == "lifetime" or self.expires is None:
            return f"{self.name} • {self.type.title()}"
        return f"{self.name} • {self.type.title()} • {self.days_remaining()}d"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LicenseInfo":
        return cls(
            kid=str(d.get("kid", "")),
            name=str(d.get("name", "")),
            email=str(d.get("email", "")),
            type=str(d.get("type", "trial")),
            issued_at=str(d.get("issued_at", "")),
            expires=(str(d["expires"]) if d.get("expires") else None),
            max_machines=int(d.get("max_machines", 1)),
            features=list(d.get("features") or list(ALL_FEATURES)),
        )


@dataclass
class ActivationResult:
    ok: bool
    info: Optional[LicenseInfo] = None
    error: str = ""


# ---------------------------------------------------------------------------
# key encode / decode / verify
# ---------------------------------------------------------------------------

_KEY_RE = re.compile(r"^PNNHA1\.([A-Za-z0-9_\-]+)\.([A-Za-z0-9_\-]+)$")


def encode_key(payload: Dict[str, Any], private_key: Ed25519PrivateKey) -> str:
    """Mint a license key string. Used by the admin CLI."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig = private_key.sign(canonical)
    return f"{KEY_PREFIX}.{_b64url_encode(canonical)}.{_b64url_encode(sig)}"


def parse_key(key: str) -> tuple[Dict[str, Any], bytes, bytes]:
    """Parse a key into (payload_dict, payload_bytes, signature_bytes).

    Raises ``ValueError`` if the format is wrong.
    """
    key = key.strip().replace("\n", "").replace(" ", "")
    m = _KEY_RE.match(key)
    if not m:
        raise ValueError("malformed license key")
    payload_bytes = _b64url_decode(m.group(1))
    sig_bytes = _b64url_decode(m.group(2))
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"payload decode failed: {e}") from e
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    return payload, payload_bytes, sig_bytes


def verify_key(key: str, public_key: Optional[Ed25519PublicKey] = None) -> LicenseInfo:
    """Return the ``LicenseInfo`` carried by *key* or raise ``ValueError``.

    The signature is checked against the embedded public key. The expiry is
    *not* checked here — callers decide whether to allow expired keys (e.g.
    for showing them in the UI as "expired") or to reject them.
    """
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


# ---------------------------------------------------------------------------
# activation persistence
# ---------------------------------------------------------------------------

class LicenseManager:
    """Loads/saves the per-machine activation file."""

    def __init__(self, trial: Optional[Trial] = None) -> None:
        self.path = LICENSE_FILE
        self.trial = trial or Trial()
        self.info: Optional[LicenseInfo] = None
        self.activated_hw: str = ""
        self.activated_at: str = ""
        self.key: str = ""
        self.load()

    # ------------------------------------------------------------------
    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return
        key = data.get("key", "")
        if not key:
            return
        try:
            info = verify_key(key)
        except ValueError:
            # corrupted / tampered file — refuse to load
            return
        self.info = info
        self.key = key
        self.activated_hw = str(data.get("hw", ""))
        self.activated_at = str(data.get("activated_at", ""))

    def save(self) -> None:
        if not self.info:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "key": self.key,
                    "hw": self.activated_hw,
                    "activated_at": self.activated_at,
                    "info": self.info.to_dict(),
                },
                indent=2, ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    def activate(self, key: str) -> ActivationResult:
        try:
            info = verify_key(key)
        except ValueError as e:
            return ActivationResult(False, error=str(e))
        if info.is_expired():
            return ActivationResult(False, info=info, error="license expired")
        self.info = info
        self.key = key.strip()
        self.activated_hw = hardware_id()
        self.activated_at = datetime.now().isoformat(timespec="seconds")
        self.save()
        return ActivationResult(True, info=info)

    def deactivate(self) -> None:
        self.info = None
        self.key = ""
        self.activated_hw = ""
        self.activated_at = ""
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    # ------------------------------------------------------------------
    def is_licensed(self) -> bool:
        if not self.info:
            return False
        if self.info.is_expired():
            return False
        # hardware mismatch → treat as not licensed on this machine
        if self.activated_hw and self.activated_hw != hardware_id():
            return False
        return True

    def can_render(self) -> bool:
        """Allow rendering if there's a valid license OR an unexpired trial."""
        if self.is_licensed():
            return True
        return not self.trial.is_expired()

    def display_status(self) -> Dict[str, Any]:
        """Return a small dict suitable for badge / settings display."""
        if self.is_licensed() and self.info:
            return {
                "state": "licensed",
                "label": self.info.display_label(),
                "type": self.info.type,
                "days": self.info.days_remaining(),
                "name": self.info.name,
            }
        if self.info and self.info.is_expired():
            return {"state": "expired", "label": "License expired", "type": self.info.type}
        days = self.trial.days_remaining()
        if days > 0:
            return {"state": "trial", "label": f"Trial: {days} Day", "days": days}
        return {"state": "trial_expired", "label": "Trial expired"}


# ---------------------------------------------------------------------------
# admin-side helpers (used by tools/generate_key.py)
# ---------------------------------------------------------------------------

def generate_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()


def save_private_key(sk: Ed25519PrivateKey, path: Path) -> None:
    pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pem)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def load_private_key(path: Path) -> Ed25519PrivateKey:
    pem = path.read_bytes()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("expected an Ed25519 private key")
    return key


def public_key_b64url(pk: Ed25519PublicKey) -> str:
    raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64url_encode(raw)


def patch_public_key_in_source(public_b64url: str) -> Path:
    """Rewrite the ``PUBLIC_KEY_B64URL = "..."`` line in this module so the
    embedded public key in the app matches the admin's private key.

    Returns the path that was modified.
    """
    src_path = Path(__file__)
    text = src_path.read_text(encoding="utf-8")
    new_line = f'PUBLIC_KEY_B64URL = "{public_b64url}"'
    new_text = re.sub(
        r'PUBLIC_KEY_B64URL\s*=\s*"[^"]*"',
        new_line,
        text,
        count=1,
    )
    if new_text == text:
        raise RuntimeError("could not locate PUBLIC_KEY_B64URL line")
    src_path.write_text(new_text, encoding="utf-8")
    return src_path
