#!/usr/bin/env python3
"""Static invariants for the Windows minimal-security profile.

These checks do not prove malware absence and do not replace compiling or
sandboxing the actual Windows binaries.
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
launcher = (root / "crates/inject/src/main.rs").read_text(encoding="utf-8")
shortcuts = (root / "crates/inject/src/shortcuts.rs").read_text(encoding="utf-8")
loader = (root / "crates/loader/src/lib.rs").read_text(encoding="utf-8")
manifest = (root / "crates/inject/Cargo.toml").read_text(encoding="utf-8")
lock = (root / "Cargo.lock").read_text(encoding="utf-8")

checks = [
    ("Windows updater module is not compiled", "mod http;" not in launcher),
    ("Windows downloader source was removed", not (root / "crates/inject/src/http.rs").exists()),
    ("No Windows remote DLL update calls", "crate::http::download" not in launcher and "fn update(" not in launcher),
    ("DLL integrity check is performed before launch",
     "verify_dll_sha256(&dll)?;" in launcher and
     launcher.index("verify_dll_sha256(&dll)?;") < launcher.index("launch(&exe, &app, &dll, &args)")),
    ("SHA-256 checksum is mandatory", 'fs::read_to_string(&manifest)' in launcher and 'Sha256::digest(&content)' in launcher),
    ("Minimal mode is enforced in launcher", "let no_runtime = true;" in launcher and 'env::set_var("SUNBIRD_GATE_ONLY", "1")' in launcher),
    ("Full-runtime launcher opt-in is absent", "--with-runtime" not in launcher),
    ("Loader returns before plugin-runtime setup in minimal mode",
     loader.index('if env::var_os("SUNBIRD_GATE_ONLY").is_some()') <
     loader.index('phoenix_runtime_desktop::prepare')),
    ("Minimal-mode shortcuts", shortcuts.count('"--no-runtime"') >= 2),
    ("SHA-256 dependency is present in manifest", 'sha2 = "0.10"' in manifest),
    ("SHA-256 dependency is pinned in Cargo.lock",
     'name = "sha2"\nversion = "0.10.9"' in lock and
     'name = "phoenix-inject"\nversion = "0.1.0"\ndependencies = [\n "misstep",\n "sha2",\n]' in lock),
]

# Validate locked registry checksums and immutable Git revisions without
# downloading or executing any dependency.
packages = lock.split("[[package]]")[1:]
registry_entries = [p for p in packages if 'source = "registry+' in p]
git_entries = [p for p in packages if 'source = "git+' in p]
checks.extend([
    ("All registry packages have a 64-digit checksum",
     all(re.search(r'^checksum = "[0-9a-f]{64}"
    print(f'{"PASS" if passed else "FAIL"}: {label}')
    failed |= not passed
print("Static check cannot certify malware-free or confirm Discord Phoenix access.")
sys.exit(1 if failed else 0)
, p, re.MULTILINE)
         for p in registry_entries)),
    ("All Git dependencies are pinned to 40-digit commit IDs",
     all(re.search(r'^source = "git+[^"]+#[0-9a-f]{40}"
    print(f'{"PASS" if passed else "FAIL"}: {label}')
    failed |= not passed
print("Static check cannot certify malware-free or confirm Discord Phoenix access.")
sys.exit(1 if failed else 0)
, p, re.MULTILINE)
         for p in git_entries)),
    ("Only the dedicated Windows security workflow remains",
     sorted(x.name for x in (root / ".github/workflows").glob("*.yml")) ==
     ["windows-minimal-security.yml"]),
])
print(f"Locked packages: {len(packages)} total; {len(registry_entries)} registry; "
      f"{len(git_entries)} pinned Git entries.")

failed = False
for label, passed in checks:
    print(f'{"PASS" if passed else "FAIL"}: {label}')
    failed |= not passed
print("Static check cannot certify malware-free or confirm Discord Phoenix access.")
sys.exit(1 if failed else 0)
