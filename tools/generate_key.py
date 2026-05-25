"""Admin CLI: generate the project keypair + mint signed license keys.

Examples
--------

Initialise the project keypair (run **once** when setting up the project)::

    python tools/generate_key.py --init

This writes ``keys/admin_private.pem`` (keep secret!) and patches
``app/core/licensing.py`` so the embedded public key matches.

Mint a perpetual Pro key for a customer::

    python tools/generate_key.py mint \\
        --name "Sok Dara" --email dara@example.com \\
        --type pro --max-machines 3

Mint a 1-year Standard key::

    python tools/generate_key.py mint \\
        --name "Lim Chenda" --email chenda@example.com \\
        --type standard --expires 2027-05-22 --max-machines 1

A copy of every minted key is appended to ``keys-issued/log.jsonl`` and the
issued key is also written to ``keys-issued/<kid>.txt``.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core import licensing  # noqa: E402

KEY_DIR = ROOT / "keys"
PRIV_PATH = KEY_DIR / "admin_private.pem"
PUB_PATH = KEY_DIR / "admin_public.txt"
ISSUED_DIR = ROOT / "keys-issued"
LOG_FILE = ISSUED_DIR / "log.jsonl"


def cmd_init(args: argparse.Namespace) -> int:
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
    print()
    print("Keep admin_private.pem secret. Commit only the changes in licensing.py.")
    return 0


def _new_kid() -> str:
    return secrets.token_hex(4)


def cmd_mint(args: argparse.Namespace) -> int:
    if not PRIV_PATH.exists():
        print(f"no admin private key at {PRIV_PATH}. Run `--init` first.", file=sys.stderr)
        return 2
    if args.type not in licensing.LICENSE_TYPES:
        print(f"--type must be one of {licensing.LICENSE_TYPES}", file=sys.stderr)
        return 2

    expires = args.expires
    if args.type == "lifetime":
        expires = None
    elif expires:
        # accept YYYY-MM-DD
        try:
            date.fromisoformat(expires)
        except Exception:
            print("--expires must be YYYY-MM-DD", file=sys.stderr)
            return 2

    features = list(args.feature) if args.feature else list(licensing.ALL_FEATURES)
    payload = {
        "kid": _new_kid(),
        "name": args.name,
        "email": args.email,
        "type": args.type,
        "issued_at": date.today().isoformat(),
        "expires": expires,
        "max_machines": int(args.max_machines),
        "features": features,
    }

    sk = licensing.load_private_key(PRIV_PATH)
    key_str = licensing.encode_key(payload, sk)

    ISSUED_DIR.mkdir(parents=True, exist_ok=True)
    (ISSUED_DIR / f"{payload['kid']}.txt").write_text(key_str + "\n", encoding="utf-8")
    log_line = json.dumps({
        "issued_at": datetime.now().isoformat(timespec="seconds"),
        "kid": payload["kid"],
        "name": args.name,
        "email": args.email,
        "type": args.type,
        "expires": expires,
        "max_machines": int(args.max_machines),
    }, ensure_ascii=False)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    print(key_str)
    print(f"# kid={payload['kid']} saved to {ISSUED_DIR / (payload['kid'] + '.txt')}",
          file=sys.stderr)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Decode + verify a key against the embedded public key — useful sanity check.

    Reads the key from the positional argument, ``-`` (stdin), or a file path.
    """
    src = args.key
    if src == "-":
        key = sys.stdin.read().strip()
    elif src and Path(src).is_file():
        key = Path(src).read_text(encoding="utf-8").strip()
    else:
        key = (src or "").strip()
    if not key:
        print("no key provided. Pass the key as an argument, `-` for stdin, "
              "or a path to a .txt file.", file=sys.stderr)
        return 2
    try:
        info = licensing.verify_key(key)
    except ValueError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))
    if info.is_expired():
        print("# WARNING: license is past its expiry date", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="generate_key", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    sub.required = False  # `--init` accepted on top-level for friendliness

    p.add_argument("--init", action="store_true",
                   help="initialise the project keypair (one-time)")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing keypair (DANGEROUS)")

    mint = sub.add_parser("mint", help="mint a license key")
    mint.add_argument("--name", required=True)
    mint.add_argument("--email", required=True)
    mint.add_argument("--type", default="standard",
                      choices=licensing.LICENSE_TYPES)
    mint.add_argument("--expires", default=None,
                      help="YYYY-MM-DD or omit for never-expires")
    mint.add_argument("--max-machines", type=int, default=1)
    mint.add_argument("--feature", action="append", default=[],
                      help="restrict to a subset of features (repeatable)")
    mint.set_defaults(func=cmd_mint)

    verify = sub.add_parser("verify", help="verify a key string, `-` for stdin, or a path to a .txt file")
    verify.add_argument("key")
    verify.set_defaults(func=cmd_verify)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.init:
        return cmd_init(args)
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
