# Windows offline security review

This branch is an **incomplete hardening experiment**, not a certified malware-free release.

## Changes

- The Windows launcher no longer downloads `phoenix.dll` or its update manifest from `assets.sunbird.tools` at startup.
- The remote-updater implementation and its unused HTTP source file were removed from the Windows launcher.
- An existing, manually supplied DLL is necessary. It must have a matching `phoenix.dll.sha256` file beside it. Both files must come from a trustworthy, reviewed local build; a self-written checksum is not independent authentication.
- The Windows launcher defaults to gate-only operation and no longer offers a full-plugin-runtime opt-in. This reduces the active attack surface, but does not remove the runtime code from the workspace or prove the DLL safe.
- The original upstream code's native injection and access-gate logic has **not** been reviewed or certified as safe.
- Other runtime code, plugins, and Discord process hooks remain in the source; do not assume they are safe.
- Removed upstream auto-merge, cross-platform, updater-check, and site publishing workflows. The fork now has a focused Windows build-review workflow.

## Known outstanding risks

1. **DLL authenticity:** The launcher now checks a local SHA-256 sidecar before loading the DLL. This detects discrepancies but **does not authenticate the source**: an attacker who can change both files can replace both. There is no signed release or independent trusted hash.
2. **Executable injection:** The launcher deliberately injects a DLL into the Discord Phoenix process. This is a sensitive technique and some endpoint products may detect it.
3. **JS/plugin runtime:** The minimal Windows launcher forces gate-only mode, so the full plugin runtime is not initialized on this launch path. However, code implementing it is still in the repository; standalone or upstream artifacts may still enable it.
4. **Supply chain:** Cargo.lock pins package versions, but dependencies and build steps still require independent audit.
5. **No verified binary:** This branch has not been compiled or exercised on Windows in this review. A GitHub Actions attempt and retry failed before any runner was assigned (no steps executed), so no Windows build results exist.

## Review/build checklist

Use a **disposable Windows VM** and examine this branch before running anything. This does not launch or inject into Discord:

```powershell
.\\scripts\\review-build-windows.ps1
```

The script performs static checks, runs Rust launcher unit tests, builds the Windows DLL and launcher with locked dependencies, generates SHA-256 hashes and the DLL's matching sidecar, and requests a Defender scan where supported. Run `cargo clippy --locked -p phoenix-loader -p phoenix-inject -- -D warnings` separately for additional linting.

If using an explicit DLL path, keep the reviewed SHA-256 sidecar beside the DLL under the name `phoenix.dll.sha256`. The launcher refuses to load without one or if the digest differs. A checksum computed from a malicious file will still match that file; verify source provenance independently.

Do not download DLLs from unknown mirrors, disable Microsoft Defender, or enter Discord credentials into third-party launchers. Review code before running. Neither clean scanning nor hashing proves safety.

## Check results

- **18/18 independent source-level invariants passed** in repository-content checks on the security branch (DLL download disabled, hash check present, minimal mode forced, lockfile pinned, 135 registry package checksums and 1 Git commit pin checked, restricted CI).
- **Windows compile: NOT VERIFIED.** The [GitHub Actions run](https://github.com/uncle43yt/sunjbird/actions/runs/45973881644) and retry concluded as failures with no allocated runner and no executed steps. This is not evidence that compilation failed. Check the repository's Actions settings/billing/runner availability in GitHub, or use a disposable Windows VM.
- **Windows Defender and dynamic execution: NOT PERFORMED.**
- **Phoenix functionality: NOT TESTED.** Original access-gate logic is unchanged, but its actual behavior has not been established.

## Scope

This repository is an independent fork. No claim of authorization, affiliation with Discord, or guarantee of access to restricted Phoenix builds is made.

## Additional static audit findings

- The upstream Windows injector launches Discord suspended, writes the DLL path into the process, and queues `LoadLibraryW` on its main thread. That is intentional process injection, not evidence by itself that the DLL is benign.
- The upstream plugin updater uses CRC-32 checks for downloaded JavaScript bundles and loader images. CRC-32 catches accidental corruption but is not a cryptographic authenticity check.
- The Rust lockfile includes a Git dependency on `sunbird-tools/sunhook`, pinned to a specific commit. This helps repeatability but the dependency still needs an audit.
- Existing shortcuts from an earlier installation are not necessarily rewritten by the new install. Inspect the target/arguments yourself before use.
- Source changes were committed for review, but **no Windows build, Defender scan, sandbox test, or reproducibility verification has yet succeeded**.
