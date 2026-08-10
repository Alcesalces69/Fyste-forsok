#!/usr/bin/env python3
"""Fetch photos from a link-shared Google Drive folder and prepare them for Instagram.

Downloads every image in the folder via Drive's public thumbnail endpoint,
then center-crops to 4:5 (1080x1350) JPEG using macOS `sips`.

The Drive folder must be shared as "Anyone with the link can view".

Usage:
    python3 scripts/fetch_photos.py --folder 1l8tkGabtFgqS8eCWqbUSlxP8fwXYHa2B
    python3 scripts/fetch_photos.py --folder <id> --limit 20
"""
import argparse
import html
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TARGET_W, TARGET_H = 1080, 1350  # IG portrait 4:5

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def list_folder(folder_id: str):
    """Scrape the public embedded folder view for (file_id, name) pairs."""
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    req = urllib.request.Request(url, headers=UA)
    body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    if "flip-entry" not in body:
        sys.exit(
            "Could not read the folder. Is it shared as 'Anyone with the link'?"
        )
    entries = re.findall(
        r'class="flip-entry" id="entry-([\w-]+)".*?flip-entry-title">([^<]+)<',
        body,
        re.S,
    )
    seen, out = set(), []
    for fid, name in entries:
        name = html.unescape(name).strip()
        if fid in seen or not re.search(r"\.(jpe?g|png|heic)$", name, re.I):
            continue
        seen.add(fid)
        out.append((fid, name))
    return out


def download(fid: str, dest: pathlib.Path) -> bool:
    url = f"https://drive.google.com/thumbnail?id={fid}&sz=w2000"
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    if not data.startswith(b"\xff\xd8"):  # not a JPEG -> got an HTML error page
        return False
    dest.write_bytes(data)
    return True


def sips_dim(path: pathlib.Path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h


def to_portrait(path: pathlib.Path, tw: int = TARGET_W, th: int = TARGET_H):
    """Cover-fit to target size: upscale-resample then center-crop."""
    w, h = sips_dim(path)
    scale = max(tw / w, th / h)
    nw, nh = round(w * scale), round(h * scale)
    subprocess.run(
        ["sips", "--resampleHeightWidth", str(nh), str(nw), str(path)],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["sips", "--cropToHeightWidth", str(th), str(tw), str(path)],
        capture_output=True,
        check=True,
    )


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
    files = list_folder(args.folder)
    print(f"Folder lists {len(files)} image files")

    fetched = 0
    index = {}
    for fid, name in files:
        stem = re.sub(r"\.\w+$", "", name).replace(" ", "_")
        dest = ASSETS / f"{stem}.jpg"
        index[dest.name] = fid
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
        print(f"  OK   {dest.name}")
        fetched += 1

    (ROOT / "photos-index.json").write_text(json.dumps(index, indent=2))
    print(f"Done. {fetched} new photos in assets/ ({len(index)} total known).")


if __name__ == "__main__":
    main()
