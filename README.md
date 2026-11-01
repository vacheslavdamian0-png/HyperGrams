# HyperGram

HyperGram is an independent messaging application project being prepared from the OwpenGram codebase.

## Project ownership

- Project owner: Дамьян В. В.
- Co-founder: Кизилов М. А.

## Upstream projects

- Android client: https://github.com/owpengram/owpengram-android-client
- Server: https://github.com/owpengram/owpengram-server
- Organization: https://github.com/owpengram

## Project status

The repository contains project documentation and a local-first development plan. The upstream Android application source has not yet been imported, a HyperGram APK has not been built, and a working HyperGram messaging backend has not yet been completed.

The initial development target is a same-device local prototype on Android using Termux, Python, and SQLite. PostgreSQL and Docker are not assumed to work inside the current Android/PRoot environment. A service bound to 127.0.0.1 is accessible only on that same device; it is not a public server.

HyperGram is an independent project and is not an official Telegram application or service.

## Licensing

The upstream Android client is licensed under GPL-2.0-or-later and the upstream server under Apache-2.0. Preserve required copyright and license notices and comply with the applicable licenses when importing, modifying, or distributing upstream components.

## Security

Never commit passwords, API keys, Telegram bot tokens, private signing keys, database credentials, or other secrets. Local environment files and signing artifacts are excluded by .gitignore.