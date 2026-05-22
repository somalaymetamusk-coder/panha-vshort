# Admin tools

This folder holds the **admin-only** CLI you keep on your machine to mint
license keys for customers. None of the files under `keys/` are shipped to
end users.

## Workflow

### 1. One-time setup (do this once when setting up the project)

```bash
pip install -r requirements.txt
python tools/generate_key.py --init
```

This creates:

* `keys/admin_private.pem` — **secret**. Never commit this. Back it up offline.
  If you lose it, every existing license key becomes unrecoverable.
* `keys/admin_public.txt` — copy of the public key (matches the value
  embedded into `app/core/licensing.py`).
* A modified `app/core/licensing.py` where the `PUBLIC_KEY_B64URL` constant
  now matches your private key. **Commit this change** so the app can verify
  the keys you'll mint.

### 2. Mint a key for a customer

Perpetual Pro license, 3-machine limit:

```bash
python tools/generate_key.py mint \
    --name "Sok Dara" --email dara@example.com \
    --type pro --max-machines 3
```

One-year Standard license, single machine:

```bash
python tools/generate_key.py mint \
    --name "Lim Chenda" --email chenda@example.com \
    --type standard --expires 2027-05-22
```

The key prints to stdout. A copy is also saved to
`keys-issued/<kid>.txt` and a one-line audit record is appended to
`keys-issued/log.jsonl`.

### 3. Send the key to the customer

Send them the single-line `PNNHA1.<payload>.<sig>` string. They paste it
into the **Activate license** dialog (click the trial badge in the app).

### 4. (Optional) verify a key without the app

```bash
python tools/generate_key.py verify 'PNNHA1.eyJ...XXX.YYY'
```

Prints the decoded payload and warns if the key is expired.

## License types

| Type      | Meaning                          | Notes                              |
|-----------|----------------------------------|------------------------------------|
| trial     | Time-limited evaluation key      | Combine with `--expires`           |
| standard  | Standard tier                    | Usually 1 machine, optional expiry |
| pro       | Pro tier                         | Higher machine count               |
| lifetime  | Lifetime, never expires          | `--expires` is ignored             |

## Security notes

* `admin_private.pem` is the **only secret** in the system. If you keep it
  on a single offline machine and only use it to mint keys, the rest of the
  workflow is bulletproof.
* The app embeds your public key. Anyone tampering with `licensing.py`
  would need to ship a modified build to bypass verification — you ship a
  build with your public key, you're safe.
* Keys are bound to a hardware ID at activation time. If a customer
  legitimately moves machines, mint them a replacement key and increment
  the `kid` audit record.
