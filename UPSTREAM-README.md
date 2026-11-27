> **Upstream reference only.** This is the original Sunbird README preserved for comparison. Its installation instructions use the upstream installer and **do not** install this security-review fork.

# Sunbird

[![discord][discord]](https://discord.gg/jEmw3bC2m7)

Patches Discord Phoenix (Discord's native Rust client) on Android, iOS, Windows, Linux, and macOS so it opens without the access gate, and injects a QuickJS plugin runtime. TypeScript plugins can hook gateway events and Discord API requests/responses, add UI buttons, decorations, message actions and slash commands, and get their own settings pages inside Discord.

No root, no Xposed, and on desktop Discord's own files stay untouched.

## Install

Open **https://sunbird.tools/** and pick your platform:

- **Android** (9+, arm64 and armv7): patches and re-signs Discord's split APKs in the browser (`com.discord` or side-by-side `com.discord.phoenix`), with optional bundled/custom plugins or a Frida gadget.
- **iOS**: patches a decrypted Discord IPA in the browser for sideloading (AltStore, Sideloadly, etc.).
- **Windows** (x86-64): run `SunbirdSetup.exe` from the site to install a launcher (and an access-gate-only shortcut) that injects `phoenix.dll` and updates itself on launch.
- **Linux** (x86-64): run `curl -fsSL https://assets.sunbird.tools/plugins/sunbird-linux.sh | sh` to install a launcher using `LD_PRELOAD` with `libphoenix.so`.
- **macOS** (Apple silicon): run `curl -fsSL https://assets.sunbird.tools/plugins/sunbird-macos.sh | sh` (currently opens the access gate via an ad-hoc signed copy; full plugin runtime is in progress).

After installing, open Discord → Settings → **Sunbird** to toggle plugins, change their settings, install plugins from a URL or file, edit their code, and use the JS console.

## How it works

- **Unlock**: the access gate check in Phoenix's native binary is located by strings and code shape rather than fixed offsets and patched to allow startup.
- **Loading**: `crates/loader` builds the injected library (`libplm.so` on Android via renamed `DT_NEEDED`, a dylib on iOS, `phoenix.dll` on Windows, `libphoenix.so` via `LD_PRELOAD` on Linux, and `libphoenix.dylib` via `DYLD_INSERT_LIBRARIES` on macOS).
- **Hooks**: gateway events are hooked by walking Phoenix's event registry by name and swapping handler pointers. Mobile drives UI through Phoenix's Rust/native UI-op bridge (using [sunhook](https://github.com/sunbird-tools/sunhook) for inline hooks on Android and vtable swaps on iOS); desktop hooks GPUI builders, `libdiscord/crates/http` vtables, and native settings directly.
- **Signing**: Android builds are signed with the public key in `crates/patcher/keys/` (APK Signature Scheme v3) so updates install over each other without losing login state.

## Plugins

Plugins are TypeScript bundles that receive a global `phoenix` object. The API reference is [`crates/runtime/phoenix.d.ts`](crates/runtime/phoenix.d.ts), and [`plugins/example`](plugins/example/src/index.ts) exercises most of it:

```ts
// @description Logs incoming messages
// @version 1.0.0
// @author you

phoenix.on(phoenix.gateway.messageCreate, (message) => {
  phoenix.log.info(`<${message.author.username}> ${message.content}`);
});

phoenix.commands.register({
  name: "shrug",
  description: "Sends your text with ¯\\_(ツ)_/¯",
  // the returned text is sent in place of "/shrug ..."
  execute: (args) => `${args} ¯\\_(ツ)_/¯`.trim(),
});
```

Leading `// @` lines describe the plugin. Besides gateway hooks there are `settings`, `storage`, `ui` (buttons, message/member/header decorations, message actions, profile sections and tabs, dialogs), `commands`, `messages` (local-only messages, send interceptors), `stores` (read-only SQL over Phoenix's cache), `fetch`, and `discord` (session-authenticated API calls plus `onRequest` / `onResponse` hooks).

The bundled plugins live in `plugins/*/src/index.ts`. CI bundles them with esbuild (`web/tools/bundle-plugins.ts`) and publishes them to https://assets.sunbird.tools/.

## Repository

| Path | What |
|---|---|
| `crates/loader` | The injected library (`libplm.so`, `phoenix.dll`, `libphoenix.so`, `libphoenix.dylib`). |
| `crates/runtime` | The QuickJS plugin runtime and `phoenix` API, shared across platforms. |
| `crates/runtime-mobile` | Android and iOS side: UI-op bridge, Settings pages, and UI patches. |
| `crates/runtime-desktop` | Desktop Phoenix side: GPUI hooks, HTTP transport hooks, settings, and tray. |
| `crates/inject` | Windows launcher/installer (`sunbird-windows-x86_64.exe`). |
| `crates/hook`, `crates/sigs`, `crates/sigscan` | Native hooking, build-independent binary locators, and the `sigscan` CLI. |
| `crates/ui-mobile`, `crates/wire` | Mobile (Android/iOS) UI-op and bridge frame codecs. |
| `crates/ui-desktop` | Desktop host primitives (clipboard, URLs, notifications, dashboard). |
| `crates/patcher`, `crates/patcher-web` | Mobile APK/IPA patcher CLI and its wasm build for the site. |
| `crates/stand-in*` | Fake Phoenix gateway library for testing hooks without Discord. |
| `plugins/` | Bundled TypeScript plugins. |
| `scripts/` | Desktop installers and dev build helpers. |
| `web/` | Static assets CI deploys to `assets.sunbird.tools`. |
| `frida/` | Frida gadget bootstrap. |

## Building

- **Android (Linux with Nix)**:

  ```sh
  nix develop
  nu scripts/phoenix.nu base.apk config.arm64_v8a.apk config.xxhdpi.apk config.en.apk
  ```

  Pass `config.armeabi_v7a.apk` in place of the arm64 split for a 32-bit phone. This builds the loader and patcher, bundles the plugins, patches the splits, and installs them with `adb`.

- **Android (Windows)**: `.\scripts\dev.ps1` (requires `cargo-ndk`, Android SDK/NDK, and a JDK).
- **Windows desktop**: `.\scripts\dev.ps1 -Desktop` for the dev loop, or `cargo build --release -p phoenix-loader -p phoenix-inject` for `phoenix.dll` and the launcher.
- **Linux desktop**: `cargo build --release -p phoenix-loader` (`target/release/libphoenix.so`).
- **macOS desktop**: `cargo build --release -p phoenix-loader` (`target/release/libphoenix.dylib`).
- **iOS**: built on macOS with Xcode for `aarch64-apple-ios` (see `.github/workflows/ios.yml`).
- **Plugins & site assets**: `node web/tools/bundle-plugins.ts` and `nu scripts/site.nu web`.

The site itself lives in [sunbird-tools/site](https://github.com/sunbird-tools/site).

## Agentic development

If you're working on this repo with a coding agent, point it at [AGENTS.md](AGENTS.md) first. It documents the crate layout, build/debug-shell workflows, signing and privacy rules, and code style conventions.

## Contributors

<a href="https://github.com/sunbird-tools/sunbird/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=sunbird-tools/sunbird" alt="Contributors" />
</a>

Not affiliated with Discord.

[discord]: https://img.shields.io/discord/917308687423533086?logo=discord&label=discord
