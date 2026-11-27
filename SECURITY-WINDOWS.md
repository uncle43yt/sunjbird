# Windows offline security review

This branch is an **incomplete hardening experiment**, not a certified malware-free release.

## Changes

- The Windows launcher no longer downloads `phoenix.dll` or its update manifest from `assets.sunbird.tools` at startup.
- The remote-updater implementation was removed from the Windows launcher.
- An existing, manually supplied DLL is now necessary. You can launch with an explicit DLL path or place a DLL at `%LOCALAPPDATA%\\Sunbird\\phoenix.dll`.
- The Windows launcher defaults to gate-only operation and no longer offers a full-plugin-runtime opt-in. This reduces the active attack surface, but does not remove the runtime code from the workspace or prove the DLL safe.
- The original upstream code's native injection and access-gate logic has **not** been reviewed or certified as safe.
- Other runtime code, plugins, and Discord process hooks are unchanged in this branch; do not assume those are safe.

## Known outstanding risks

1. **DLL authenticity:** A local DLL can still be malicious. No cryptographic signature or pinned hash is enforced by the launcher.
2. **Executable injection:** The launcher deliberately injects a DLL into the Discord Phoenix process. This is a sensitive technique and some endpoint products may detect it.
3. **JS/plugin runtime:** The minimal Windows launcher forces gate-only mode, so the full plugin runtime is not initialized on this launch path. However, code implementing it is still in the repository; standalone or upstream artifacts may still enable it.
4. **Supply chain:** Cargo.lock pins package versions, but dependencies and build steps still require independent audit.
5. **No verified binary:** This branch has not been compiled or exercised on Windows in this review; workflows on forked repositories may need explicit enabling.

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

## Additional static audit findings

- The upstream Windows injector launches Discord suspended, writes the DLL path into the process, and queues `LoadLibraryW` on its main thread. That is intentional process injection, not evidence by itself that the DLL is benign.
- The upstream plugin updater uses CRC-32 checks for downloaded JavaScript bundles and loader images. CRC-32 catches accidental corruption but is not a cryptographic authenticity check.
- The Rust lockfile includes a Git dependency on `sunbird-tools/sunhook`, pinned to a specific commit. This helps repeatability but the dependency still needs an audit.
- Existing shortcuts from an earlier installation are not necessarily rewritten by the new install. Inspect the target/arguments yourself before use.
- Source changes were committed for review, but **no Windows build, Defender scan, sandbox test, or reproducibility verification has yet succeeded**.
