#!/usr/bin/env python3
"""Fetch photos from a link-shared Google Drive folder and prepare them for Instagram.

Recursively walks the folder (including subfolders — e.g. one per animal
species) via Drive's public embedded-folder view, downloads every image via
the public thumbnail endpoint, then center-crops to 4:5 (1080x1350) or, with
--story, 9:16 (1080x1920) JPEG using Pillow.

The Drive folder must be shared as "Anyone with the link can view".

Usage:
    python scripts/fetch_photos.py --folder 1l8tkGabtFgqS8eCWqbUSlxP8fwXYHa2B
    python scripts/fetch_photos.py --folder <id> --limit 20
    python scripts/fetch_photos.py --folder <id> --story
"""
import argparse
import html
import json
import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TARGET_W, TARGET_H = 1080, 1350  # IG portrait 4:5

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

IMAGE_RE = re.compile(r"\.(jpe?g|png|heic)$", re.I)
ENTRY_RE = re.compile(
    r'class="flip-entry"[^>]*id="entry-([\w-]+)".*?flip-entry-title">([^<]+)<',
    re.S,
)


def list_entries(folder_id: str):
    """Scrape the public embedded folder view for (id, name) pairs."""
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    req = urllib.request.Request(url, headers=UA)
    body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    if "flip-entry" not in body:
        sys.exit(
            "Could not read the folder. Is it shared as 'Anyone with the link'?"
        )
    return [(fid, html.unescape(name).strip()) for fid, name in ENTRY_RE.findall(body)]


def walk(folder_id: str, group: str = None):
    """Recursively collect image files, tagging each with its immediate parent
    folder name as `group` (e.g. the species name). Entries without an image
    extension are assumed to be subfolders and are recursed into."""
    seen_ids = set()
    files = []
    for fid, name in list_entries(folder_id):
        if fid in seen_ids:
            continue
        seen_ids.add(fid)
        if IMAGE_RE.search(name):
            files.append((fid, name, group))
        else:
            files.extend(walk(fid, group=name))
    return files


def download(fid: str, dest: pathlib.Path) -> bool:
    url = f"https://drive.google.com/thumbnail?id={fid}&sz=w2000"
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    if not data.startswith(b"\xff\xd8"):  # not a JPEG -> got an HTML error page
        return False
    dest.write_bytes(data)
    return True


def to_portrait(path: pathlib.Path, tw: int, th: int):
    """Cover-fit to target size: upscale-resample then center-crop."""
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = img.size
    scale = max(tw / w, th / h)
    nw, nh = round(w * scale), round(h * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    img = img.crop((left, top, left + tw, top + th))
    img.save(path, "JPEG", quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="Google Drive folder id")
    ap.add_argument("--limit", type=int, default=0, help="max new photos")
    ap.add_argument("--landscape", action="store_true", help="skip 4:5 crop")
    ap.add_argument(
        "--story",
        action="store_true",
        help="crop to 9:16 (1080x1920) into assets/story/ instead of 4:5",
    )
    args = ap.parse_args()

    global ASSETS, TARGET_W, TARGET_H
    if args.story:
        ASSETS = ROOT / "assets" / "story"
        TARGET_W, TARGET_H = 1080, 1920
    ASSETS.mkdir(parents=True, exist_ok=True)

    files = walk(args.folder)
    print(f"Folder tree lists {len(files)} image files")

    fetched = 0
    index = {}
    for fid, name, group in files:
        stem = re.sub(r"\.\w+$", "", name).replace(" ", "_")
        prefix = f"{group}_" if group else ""
        dest = ASSETS / f"{prefix}{stem}.jpg"
        index[dest.name] = {"id": fid, "species": group}
        if dest.exists():
            continue
        if args.limit and fetched >= args.limit:
            continue
        ok = download(fid, dest)
        if not ok:
            print(f"  SKIP {name} (not downloadable — check sharing)")
            dest.unlink(missing_ok=True)
            continue
        if not args.landscape:
            to_portrait(dest, TARGET_W, TARGET_H)
        print(f"  OK   {dest.name}  [{group}]")
        fetched += 1

    (ROOT / "photos-index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False)
    )
    print(f"Done. {fetched} new photos in assets/ ({len(index)} total known).")


if __name__ == "__main__":
    main()
