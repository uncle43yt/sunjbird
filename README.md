# Sunjbird: Windows minimal-security review fork

**Status: UNDER REVIEW — no malware-free claim, no verified Windows release.**

This is an independent Windows-focused fork of [sunbird-tools/sunbird](https://github.com/sunbird-tools/sunbird). It is intended to reduce the risk of running unverified executables or plugins when evaluating the original Sunbird project with Discord Phoenix.

## What has changed

- The Windows launcher does **not** download a DLL or its version manifest at startup.
- The Windows launcher requires a **locally supplied DLL and a matching SHA-256 checksum file** before attempting to load it.
- The Windows launcher forces the minimal, plugin-runtime-disabled path. There is no full-runtime opt-in in this launcher.
- The unnecessary Windows HTTP updater source and upstream auto-merge, site publishing, release, and cross-platform CI workflows were removed from this review branch.
- The original native process-injection and Phoenix access-gate routines are **not** modified, audited in full, or proven to work.

A matching SHA-256 checksum detects unexpected changes to a file. It **does not** make an unknown DLL trustworthy, particularly when both the DLL and checksum come from the same untrusted party.

## What to do before running anything

See [SECURITY-WINDOWS.md](SECURITY-WINDOWS.md) for actual audit notes and known risks. In a disposable Windows VM with a trusted Rust toolchain and Python 3, you can run the offline review/build helper:

```powershell
.\scripts\review-build-windows.ps1
```

It checks source invariants, runs launcher unit tests, builds the Windows components, calculates SHA-256 hashes, writes the local DLL checksum sidecar, and requests Microsoft Defender scans when supported. **It does not start Discord or inject anything.**

The GitHub Actions Windows workflow is in [`.github/workflows/windows-minimal-security.yml`](.github/workflows/windows-minimal-security.yml). Initial runs failed **before any runner was assigned**, so neither the build nor unit tests are yet verified. See [the current pull request](https://github.com/uncle43yt/sunjbird/pull/1) for updates.

Do not run installers from the upstream website expecting them to use this fork. Do not download a mystery DLL, disable antivirus, or use a sensitive Discord account for unverified testing.

## Source and scope

The original [README](UPSTREAM-README.md) is preserved for reference; its installation instructions install **upstream software**, not this review fork. The original project is licensed under EUPL-1.2 as indicated by its workspace manifest. This repository is not affiliated with Discord and does not guarantee access to restricted builds or features.
