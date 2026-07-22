# Secure Notes CLI

> Local encrypted notes CLI using AES-GCM with password-derived keys.

## Features

- 🔐 AES-256-GCM encryption
- 🔑 Password-derived key (Argon2id / PBKDF2)
- 📝 Create, read, list, delete notes
- 🔍 Search notes by title

## Usage

```bash
pip install cryptography
python3 notes.py init
python3 notes.py new "My Note" --body "Secret content"
python3 notes.py list
```

## Why I built this

I wanted a lightweight, local-only encrypted notes app for storing credentials.

— Faraz

## License
MIT — © 2026 Faraz Mustafa Seyed