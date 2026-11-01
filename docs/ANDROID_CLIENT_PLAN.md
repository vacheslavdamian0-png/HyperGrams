# HyperGram Android client preparation plan

## Current state

- Project repository: https://github.com/vacheslavdamian0-png/HyperGrams
- Upstream Android client: https://github.com/owpengram/owpengram-android-client
- No Android source code has been copied into this repository yet.
- No HyperGram APK has been built or tested yet.
- No production HyperGram server endpoint has been configured.

## Implementation sequence

### 1. Bring in the upstream source
Use a GitHub fork or import the upstream repository while preserving its history and GPL-2.0-or-later notices. Keep the upstream project attribution and license files.

### 2. Establish a clean baseline
Build the unmodified upstream app first. Record the upstream commit used and verify installation and basic connectivity before changing branding.

### 3. Apply HyperGram identity
Update application name, launcher icons, splash/intro branding, in-app labels, and package/application identifiers only after checking migration and signing implications. Do not reuse protected third-party marks or artwork without permission.

### 4. Configure the independent network
Only point the app at HyperGram infrastructure after the server is deployed, secured with HTTPS, and confirmed compatible with the client's protocol. Never ship placeholder or guessed production endpoints.

### 5. Test and release
Test login, messaging, media, notifications, updates, and multi-device behavior. Protect the Android release signing key and publish checksums with each release.

## Build environment

The upstream instructions currently specify JDK 17+, Android SDK API 36, Build Tools 36.0.0, and NDK 27.2.12479018. Follow the upstream README for exact commands and dependencies. Building on the current Android/PRoot phone environment is not considered a supported build path.

## License and security

The upstream Android client is GPL-2.0-or-later. Preserve copyright and license notices and comply with GPL obligations when distributing modified binaries. Never commit passwords, signing keys, tokens, or private infrastructure credentials.