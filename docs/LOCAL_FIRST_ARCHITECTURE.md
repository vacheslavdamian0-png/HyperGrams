# HyperGram: local-first development architecture

## Goal
Build and test the first HyperGram prototype on the owner's Android phone without renting a VPS.

## What can run locally
- A small HTTP API bound to 127.0.0.1 for same-device development.
- A lightweight local data store such as SQLite for prototype accounts and test messages.
- A Telegram bot adapter for delivering one-time login codes, using a token stored only in a private environment variable or local untracked configuration file.
- A simple Android client build after the upstream source is imported and the required Android build environment is available.

## Important network limitation
127.0.0.1 is reachable only from the same device. Other users cannot connect to a phone-local server through localhost. Remote access requires a network path, such as a reachable home network endpoint, a tunnel, or hosted infrastructure. Do not promise public availability while the service is loopback-only.

## Current device constraints
The development device is Android ARM64 with Termux and Ubuntu under PRoot. PostgreSQL initialization failed because the environment could not create the required shared-memory segment. Docker is not installed and is not a suitable assumption inside this PRoot environment. Prefer SQLite for the local prototype; do not spend more time trying to force PostgreSQL or Docker inside PRoot.

## Safe implementation order
1. Create a minimal local API using Python's standard library and SQLite.
2. Add Telegram one-time codes after the bot token has been rotated. Keep the token out of Git and out of chat.
3. Add basic local account/session handling, rate limits, expiry, and one-time code consumption.
4. Import the OwpenGram Android source while preserving its GPL-2.0-or-later notices and history.
5. Build and test the upstream Android app on a supported desktop build environment, then apply HyperGram branding.
6. Connect the Android app only to a server endpoint that actually exists and has been tested.

## Security rules
- Never commit bot tokens, passwords, API keys, signing keys, or production credentials.
- Bind local development services to 127.0.0.1 by default.
- Do not expose debug endpoints to the internet.
- Treat Telegram OTP as an account-verification mechanism only after threat-modeling, rate limiting, and abuse controls are implemented.
- This prototype is not production-ready until security review, backups, monitoring, and network deployment are addressed.

## Upstream and licensing
- Android client: https://github.com/owpengram/owpengram-android-client (GPL-2.0-or-later)
- Server: https://github.com/owpengram/owpengram-server (Apache-2.0)

Preserve upstream copyright and license notices and comply with the applicable license when redistributing modified components.