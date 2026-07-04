# Windows SmartScreen

The Qwibo alpha installer is **not yet signed** with an Authenticode certificate. Windows Defender SmartScreen may block it.

## What you see

> Windows protected your PC  
> Microsoft Defender SmartScreen prevented an unrecognized app from starting.

This is **expected** for unsigned alpha builds.

## How to install anyway

1. Click **More info** (or **Ulteriori informazioni** in Italian Windows).
2. Click **Run anyway** (**Esegui comunque**).

## Why unsigned?

Code signing certificates cost money and require identity verification. Signing is on the [roadmap](../changelog.md) for a stable release.

## Is the file safe?

Download **only** from official [GitHub Releases](https://github.com/qwibo/qwibo/releases) on the `qwibo/qwibo` repository. Verify the filename matches `Qwibo-Setup-*.exe`.

After install, SmartScreen does not block normal app launches — only the installer triggers this warning.
