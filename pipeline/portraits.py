#!/usr/bin/env python3
"""Convert DDS/PNG mech portraits from RT_ROOT to a flat output directory.

Usage:
    python pipeline/portraits.py [--output-dir PATH] [--rt-root PATH] [--db-path PATH]

Defaults:
    --output-dir   frontend/src/public/portraits
    --rt-root      $RT_ROOT env var (or from .env)
    --db-path      $DB_PATH env var, else roguetech.db
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
from pathlib import Path

# Load .env if present (same logic as pipeline)
_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _build_portrait_map(rt_root: Path) -> dict[str, Path]:
    """Scan RT_ROOT for portrait/tankportrait directories; return stem.lower() → path."""
    portrait_dirs = {"portrait", "tankportrait"}
    result: dict[str, Path] = {}
    for path in rt_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".dds", ".png"}:
            if path.parent.name.lower() in portrait_dirs:
                stem = path.stem.lower()
                if stem not in result:
                    result[stem] = path
    return result


def _convert(src: Path, dst: Path) -> None:
    from PIL import Image, ImageOps

    if src.suffix.lower() == ".dds":
        img = Image.open(src)
        img = ImageOps.flip(img)
        img.save(dst, "PNG")
    else:
        shutil.copy2(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert RT portraits to PNG")
    parser.add_argument(
        "--output-dir",
        default="frontend/src/public/portraits",
        help="Output directory for PNG files (default: frontend/src/public/portraits)",
    )
    parser.add_argument("--rt-root", default=os.environ.get("RT_ROOT"), help="Path to RT_ROOT")
    parser.add_argument(
        "--db-path",
        default=os.environ.get("DB_PATH", "roguetech.db"),
        help="Path to roguetech.db",
    )
    args = parser.parse_args()

    if not args.rt_root:
        sys.exit("RT_ROOT is not set. Pass --rt-root or set RT_ROOT in .env")

    rt_root = Path(args.rt_root)
    if not rt_root.is_dir():
        sys.exit(f"RT_ROOT does not exist: {rt_root}")

    db_path = Path(args.db_path)
    if not db_path.is_file():
        sys.exit(
            f"DB not found: {db_path}\n"
            "  Tip: if using Docker, copy it first: docker cp <pipeline-container>:/data/db/roguetech.db ."
        )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning {rt_root} for portraits…")
    portrait_map = _build_portrait_map(rt_root)
    print(f"  found {len(portrait_map):,} portrait files")

    con = sqlite3.connect(db_path)
    try:
        icons = [
            row[0] for row in con.execute("SELECT DISTINCT icon FROM chassis WHERE icon IS NOT NULL AND icon != ''")
        ]
        print(f"  {len(icons):,} distinct icon values in DB")
    except sqlite3.OperationalError:
        # icon column not yet in schema (DB predates this feature) - convert everything found
        icons = list(portrait_map.keys())
        print(f"  icon column not in DB yet - converting all {len(icons):,} discovered portrait files")
    con.close()

    converted = skipped = missing = errors = 0
    for icon in icons:
        dst = out_dir / f"{icon.lower()}.png"
        src = portrait_map.get(icon.lower())
        if src is None:
            print(f"  MISSING: {icon}")
            missing += 1
            continue
        if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime:
            skipped += 1
            continue
        try:
            _convert(src, dst)
            converted += 1
        except Exception as exc:
            print(f"  ERROR: {icon} ({src}): {exc}")
            errors += 1

    print(f"Done - {converted} converted, {skipped} skipped (up-to-date), {missing} missing, {errors} errors")


if __name__ == "__main__":
    main()
