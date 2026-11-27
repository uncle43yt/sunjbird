# Windows offline security review

This branch is an **incomplete hardening experiment**, not a certified malware-free release.

## Changes

- The Windows launcher no longer downloads `phoenix.dll` or its update manifest from `assets.sunbird.tools` at startup.
- The remote-updater implementation was removed from the Windows launcher.
- An existing, manually supplied DLL is now necessary. You can launch with an explicit DLL path or place a DLL at `%LOCALAPPDATA%\\Sunbird\\phoenix.dll`.
- The original upstream code's native injection and access-gate logic has **not** been reviewed or certified as safe.
- Other runtime code, plugins, and Discord process hooks are unchanged in this branch; do not assume those are safe.

## Known outstanding risks

1. **DLL authenticity:** A local DLL can still be malicious. No cryptographic signature or pinned hash is enforced by the launcher.
2. **Executable injection:** The launcher deliberately injects a DLL into the Discord Phoenix process. This is a sensitive technique and some endpoint products may detect it.
3. **JS/plugin runtime:** Full-runtime mode can execute plugin code and access authenticated Discord APIs. Prefer gate-only mode if authorized for your use case. This is not a security guarantee.
4. **Supply chain:** Cargo.lock pins package versions, but dependencies and build steps still require independent audit.
5. **No verified binary:** This branch has not been compiled or exercised on Windows in this review.

## Review/build checklist

Run in a disposable Windows VM, with a non-production Discord account if applicable:

```powershell
cargo build --locked --release -p phoenix-loader -p phoenix-inject
cargo clippy --locked -p phoenix-loader -p phoenix-inject -- -D warnings
cargo test --locked -p phoenix-inject
Get-FileHash .\\target\\release\\phoenix.dll -Algorithm SHA256
Get-FileHash .\\target\\release\\phoenix-inject.exe -Algorithm SHA256
```

Do not download DLLs from unknown mirrors, disable Microsoft Defender, or enter Discord credentials into third-party launchers. Review all code before running. Do not treat a clean antivirus scan as proof of safety.

## Scope

This repository is an independent fork. No claim of authorization, affiliation with Discord, or guarantee of access to restricted Phoenix builds is made.
