#!/usr/bin/env python3
"""HyperGram local prototype: loopback API + Telegram one-time codes + SQLite.

Development prototype only. Keep TELEGRAM_BOT_TOKEN out of Git and chat.
"""
import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("HYPERGRAM_DB", os.path.join(ROOT, "hypergram.sqlite3"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8787"))
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CODE_TTL = 300
RESEND_SECONDS = 60
MAX_ATTEMPTS = 5
_sessions_lock = threading.Lock()


def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS telegram_users (
            chat_id TEXT PRIMARY KEY,
            first_seen INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS login_codes (
            chat_id TEXT PRIMARY KEY,
            code_hash TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            sent_at INTEGER NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL
        );
        """)


def telegram(method, payload=None, timeout=35):
    if not BOT_TOKEN:
        raise RuntimeError("Telegram bot is not configured. Set TELEGRAM_BOT_TOKEN locally.")
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/" + method
    body = urllib.parse.urlencode(payload or {}).encode()
    req = urllib.request.Request(url, data=body)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError("Telegram API request failed")
    return result["result"]


def send_message(chat_id, message):
    telegram("sendMessage", {"chat_id": str(chat_id), "text": message}, timeout=15)


def bot_loop():
    offset = None
    while True:
        try:
            params = {"timeout": 25}
            if offset is not None:
                params["offset"] = offset
            updates = telegram("getUpdates", params, timeout=35)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue
                chat = msg.get("chat", {})
                if chat.get("type") != "private":
                    continue
                text = (msg.get("text") or "").strip()
                chat_id = str(chat.get("id", ""))
                if text.startswith("/start"):
                    with db() as c:
                        c.execute(
                            "INSERT OR IGNORE INTO telegram_users(chat_id, first_seen) VALUES(?, ?)",
                            (chat_id, int(time.time())),
                        )
                    send_message(chat_id, "HyperGram: этот Telegram-аккаунт подключён для получения кодов входа. Запросить код можно в локальном приложении.")
                elif text.startswith("/help"):
                    send_message(chat_id, "Это бот подтверждения входа HyperGram. Никому не пересылайте коды.")
        except Exception as exc:
            # Do not log URLs or exception text: they could contain credentials.
            print("Telegram polling temporarily unavailable:", type(exc).__name__, flush=True)
            time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    server_version = "HyperGramLocal/0.1"

    def log_message(self, fmt, *args):
        print("HTTP", self.address_string(), fmt % args, flush=True)

    def reply(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 4096:
                return None
            value = json.loads(self.rfile.read(size))
            return value if isinstance(value, dict) else None
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True, "service": "HyperGram local prototype"})
        return self.reply(404, {"error": "not_found"})

    def do_POST(self):
        data = self.read_json()
        if data is None:
            return self.reply(400, {"error": "invalid_json"})

        if self.path == "/request-code":
            chat_id = str(data.get("chat_id", "")).strip()
            if not chat_id.isdigit() or len(chat_id) > 20:
                return self.reply(400, {"error": "invalid_chat_id"})
            now = int(time.time())
            with db() as c:
                user = c.execute("SELECT chat_id FROM telegram_users WHERE chat_id=?", (chat_id,)).fetchone()
                old = c.execute("SELECT sent_at FROM login_codes WHERE chat_id=?", (chat_id,)).fetchone()
                if not user:
                    return self.reply(403, {"error": "open_the_bot_and_press_start_first"})
                if old and now - old["sent_at"] < RESEND_SECONDS:
                    return self.reply(429, {"error": "please_wait_before_requesting_another_code"})
                code = f"{secrets.randbelow(1000000):06d}"
                digest = hashlib.sha256((chat_id + ":" + code).encode()).hexdigest()
                c.execute(
                    "INSERT OR REPLACE INTO login_codes(chat_id, code_hash, expires_at, sent_at, attempts) VALUES(?,?,?,?,0)",
                    (chat_id, digest, now + CODE_TTL, now),
                )
            try:
                send_message(chat_id, "Ваш код входа HyperGram: " + code + "\nДействует 5 минут. Никому его не сообщайте.")
            except Exception:
                with db() as c:
                    c.execute("DELETE FROM login_codes WHERE chat_id=?", (chat_id,))
                return self.reply(502, {"error": "telegram_delivery_failed"})
            return self.reply(200, {"ok": True, "message": "code_sent_if_delivery_succeeded"})

        if self.path == "/verify-code":
            chat_id = str(data.get("chat_id", "")).strip()
            code = str(data.get("code", "")).strip()
            if not chat_id.isdigit() or len(chat_id) > 20 or len(code) != 6 or not code.isdigit():
                return self.reply(400, {"error": "invalid_input"})
            now = int(time.time())
            with db() as c:
                row = c.execute("SELECT * FROM login_codes WHERE chat_id=?", (chat_id,)).fetchone()
                if not row or row["expires_at"] < now or row["attempts"] >= MAX_ATTEMPTS:
                    c.execute("DELETE FROM login_codes WHERE chat_id=?", (chat_id,))
                    return self.reply(401, {"error": "code_invalid_or_expired"})
                expected = hashlib.sha256((chat_id + ":" + code).encode()).hexdigest()
                if not secrets.compare_digest(expected, row["code_hash"]):
                    c.execute("UPDATE login_codes SET attempts=attempts+1 WHERE chat_id=?", (chat_id,))
                    return self.reply(401, {"error": "code_invalid_or_expired"})
                c.execute("DELETE FROM login_codes WHERE chat_id=?", (chat_id,))
                token = secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                c.execute(
                    "INSERT INTO sessions(token_hash, chat_id, created_at, expires_at) VALUES(?,?,?,?)",
                    (token_hash, chat_id, now, now + 30 * 24 * 60 * 60),
                )
            return self.reply(200, {"ok": True, "session_token": token, "expires_in": 2592000})

        return self.reply(404, {"error": "not_found"})


def main():
    init_db()
    print(f"HyperGram local API starting at http://{HOST}:{PORT}", flush=True)
    print("Open the Telegram bot and press /start before requesting a login code.", flush=True)
    if BOT_TOKEN:
        threading.Thread(target=bot_loop, daemon=True).start()
    else:
        print("Telegram bot disabled: TELEGRAM_BOT_TOKEN is not set.", flush=True)
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nHyperGram local API stopped.", flush=True)


if __name__ == "__main__":
    main()
