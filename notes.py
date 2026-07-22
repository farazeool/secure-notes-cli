#!/usr/bin/env python3
"""Secure Notes CLI.

Author: Faraz Mustafa Seyed
"""
import argparse
import base64
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Install cryptography: pip install cryptography"); sys.exit(1)

DB_DIR = Path.home() / ".secure-notes"
DB_PATH = DB_DIR / "notes.db"
KEY_PATH = DB_DIR / ".key_salt"

def derive_key(password, salt=None):
    if salt is None: salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def init_db(password):
    DB_DIR.mkdir(parents=True, exist_ok=True)
    key, salt = derive_key(password)
    KEY_PATH.write_bytes(salt)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL)")
    conn.commit(); conn.close()
    print("Init complete")

def get_cipher(password):
    if not KEY_PATH.exists(): print("Run init first"); sys.exit(1)
    key, _ = derive_key(password, KEY_PATH.read_bytes())
    return Fernet(key)

def add_note(password, title, body):
    cipher = get_cipher(password)
    now = datetime.utcnow().isoformat()+"Z"
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("INSERT INTO notes VALUES (?,?,?,?,?)", (None, cipher.encrypt(title.encode()).decode(), cipher.encrypt(body.encode()).decode(), now, now))
    conn.commit(); conn.close()
    print("Note added")

def list_notes(password):
    cipher = get_cipher(password)
    conn = sqlite3.connect(str(DB_PATH))
    for t, c in conn.execute("SELECT title,created FROM notes ORDER BY created DESC"):
        print(f"  {c[:10]}  {cipher.decrypt(t.encode()).decode()}")
    conn.close()

def show_note(password, title):
    cipher = get_cipher(password)
    conn = sqlite3.connect(str(DB_PATH))
    for t, b, c, u in conn.execute("SELECT title,body,created,updated FROM notes"):
        if cipher.decrypt(t.encode()).decode() == title:
            print(cipher.decrypt(b.encode()).decode())
    conn.close()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["init","new","list","show"])
    p.add_argument("title", nargs="?")
    p.add_argument("--password")
    p.add_argument("--body")
    args = p.parse_args()
    pw = args.password or os.environ.get("SNOTES_PASSWORD")
    if not pw and args.action != "init":
        import getpass; pw = getpass.getpass()
    if args.action == "init": init_db(pw or input("Password: "))
    elif args.action == "new": add_note(pw, args.title, args.body or input("Body: "))
    elif args.action == "list": list_notes(pw)
    elif args.action == "show": show_note(pw, args.title)

if __name__ == "__main__": main()
