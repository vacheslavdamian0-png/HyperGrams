# HyperGram local server (prototype)

This first backend prototype runs on the same Android phone in Termux. It uses Python's standard library and SQLite; PostgreSQL and Docker are not needed.

## 1. Prepare Termux

Install Git and Python:

```sh
pkg update
pkg install git python
git clone https://github.com/vacheslavdamian0-png/HyperGrams.git
cd HyperGrams/local-server
```

If you already cloned the repository, use `cd` to enter its `local-server` directory and run `git pull` first.

## 2. Start without Telegram

```sh
python server.py
```

In another Termux session, check the local API:

```sh
curl http://127.0.0.1:8787/health
```

Expected response:

```json
{"ok": true, "service": "HyperGram local prototype"}
```

Stop the server with Ctrl+C.

## 3. Enable Telegram login (only after revoking any exposed token)

Create or rotate the bot token with @BotFather. Do not paste it into chat, source files, or GitHub. Set it only in the private Termux shell:

```sh
export TELEGRAM_BOT_TOKEN='PASTE_THE_NEW_TOKEN_HERE'
python server.py
```

Then open your bot in Telegram and press **Start**. The bot records your private chat ID locally. The local API can then send a one-time code to that registered chat.

Keep the shell session private. For a more persistent setup, store the token in a local file excluded by Git and restrict its permissions; never upload it.

## API endpoints

- `GET /health` — local health check.
- `POST /request-code` with JSON `{"chat_id":"YOUR_TELEGRAM_CHAT_ID"}` — sends a six-digit code; code expires in 5 minutes, resend cooldown is 60 seconds.
- `POST /verify-code` with JSON `{"chat_id":"YOUR_TELEGRAM_CHAT_ID","code":"123456"}` — consumes the code and returns a random session token.

The Telegram chat ID is visible in the bot's local SQLite registration, but this prototype does not yet include a polished client UI or an endpoint to display the ID. The next development step is to add a safe local account/status flow and then connect an Android client.

## Limits and safety

- The service binds to `127.0.0.1`; only apps on this same phone can reach it. It is not accessible to other people's phones or the public internet.
- Telegram bot polling still requires an internet connection.
- This is a development prototype, not a production-ready messenger. It has no message transport, group chats, media storage, push notifications, account recovery, backups, or security audit.
- Do not expose this development server publicly. Do not commit tokens or session credentials.


## Direct-message API (prototype)

After a user has verified a Telegram login code, use the returned session token as a Bearer token:

```sh
curl -X POST http://127.0.0.1:8787/send-message \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SESSION_TOKEN' \
  -d '{"to":"RECIPIENT_CHAT_ID","text":"Привет из HyperGram"}'
```

Read the latest 100 messages in that conversation:

```sh
curl 'http://127.0.0.1:8787/messages?with=RECIPIENT_CHAT_ID' \
  -H 'Authorization: Bearer YOUR_SESSION_TOKEN'
```

Both users must have pressed Start in the bot. The recipient must also have completed login before they can send messages. Messages are stored locally in SQLite; this prototype does not yet provide end-to-end encryption, delivery notifications, attachments, or a graphical chat interface. Treat session tokens as passwords.
