"""Install the DaVinci Resolve bridge scripts into Resolve's Workspace > Scripts > Utility menu."""
from __future__ import annotations

import platform
from pathlib import Path

from .common import ROOT


def resolve_install() -> None:
    home = Path.home()
    targets = {
        "Darwin": home / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility",
        "Windows": home / "AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Utility",
        "Linux": home / ".local/share/DaVinciResolve/Fusion/Scripts/Utility",
    }
    dest = targets.get(platform.system())
    if dest is None:
        raise SystemExit(f"Unsupported platform: {platform.system()}")
    dest.mkdir(parents=True, exist_ok=True)
    (ROOT / "resolve" / "inbox").mkdir(parents=True, exist_ok=True)
    (ROOT / "resolve" / "outbox").mkdir(parents=True, exist_ok=True)
    for name in ("sermon_clipper_bridge.py", "sermon_clipper_bridge_lua.lua"):
        text = (ROOT / "resolve" / name).read_text().replace("__SERMON_CLIPPER_ROOT__", ROOT.as_posix())
        (dest / name).write_text(text)
        print(f"Installed {dest / name}")
    print("In Resolve: Workspace > Scripts > Utility > sermon_clipper_bridge (or _lua). Restart Resolve if not listed.")
