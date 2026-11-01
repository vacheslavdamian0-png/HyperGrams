# HyperGram Android client

## Upstream source

The Android application is being prepared from the OwpenGram Android client:

https://github.com/owpengram/owpengram-android-client

This directory currently contains project-specific integration notes; it does not yet contain a copied or modified Android application source tree.

## Planned HyperGram changes

1. Preserve the upstream GPL-2.0-or-later license and copyright notices.
2. Replace user-visible OwpenGram branding with HyperGram branding where legally permitted.
3. Configure the app to connect to HyperGram's own server only after that server is deployed and its API compatibility is verified.
4. Keep signing keys, passwords, API credentials, and production endpoints out of public source control where appropriate.
5. Build and test a release APK on a supported Android build environment.

## Build prerequisites from the upstream project

Check the upstream README before every build because requirements can change. The currently documented setup requires JDK 17 or newer, Android SDK API 36, Android Build Tools 36.0.0, and NDK 27.2.12479018. The upstream project documents a Windows build script named build-android.bat.

A normal Android phone running Termux/PRoot is not a supported substitute for the documented Android build environment.

## Important

HyperGram is an independent project, not an official Telegram application or service. Do not distribute a build until branding, server configuration, licensing notices, and release signing have been checked.