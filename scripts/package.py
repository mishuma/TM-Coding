"""Zip the starter/ folder into dist/tm-image-app-starter.zip, the one file teachers hand to students.

Usage:  python scripts/package.py            (writes dist/tm-image-app-starter.zip)
        python scripts/package.py OUT.zip    (writes to OUT.zip)

Files sit at the top of the zip (no wrapper folder). On both Mac (Archive Utility) and Windows
("Extract All") that unzips to a single folder named after the zip, not a folder inside a folder.
A saved student model and OS junk files are left out.
"""
import os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARTER = os.path.join(ROOT, "starter")
DEFAULT_OUT = os.path.join(ROOT, "dist", "tm-image-app-starter.zip")
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "__pycache__"}
# model/ ships empty except for this note: a developer's saved model or test zip must never ship.
MODEL_KEEP = {"model/PUT-MODEL-HERE.txt"}
SKIP_SUFFIXES = (".zip",)
REQUIRED = ["index.html", "tm-helper.js", "AGENTS.md", "CLAUDE.md", "README.md",
            "lib/tf.min.js", "lib/teachablemachine-image.min.js", "lib/LICENSE.txt", "lib/NOTICE.txt",
            "model/PUT-MODEL-HERE.txt"]


def collect(starter: str) -> list[str]:
    """Return the sorted relative paths (forward slashes) to ship."""
    found = []
    for dirpath, dirnames, filenames in os.walk(starter):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_NAMES and not d.startswith("."))
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), starter).replace(os.sep, "/")
            if name in SKIP_NAMES or name.startswith(".") or name.endswith(SKIP_SUFFIXES):
                continue
            if rel.startswith("model/") and rel not in MODEL_KEEP:
                continue
            found.append(rel)
    missing = [r for r in REQUIRED if r not in found]
    if missing:
        raise SystemExit("package.py: starter/ is missing required files: " + ", ".join(missing))
    return sorted(found)


def build(out_path: str = DEFAULT_OUT, starter: str = STARTER) -> tuple[str, list[str]]:
    files = collect(starter)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            z.write(os.path.join(starter, rel), rel)
    return out_path, files


if __name__ == "__main__":
    path, files = build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
    print(f"Wrote {os.path.abspath(path)} ({len(files)} files, {os.path.getsize(path) // 1024} KB)")
