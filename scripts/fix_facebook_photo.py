#!/usr/bin/env python3
"""One-off fix: delete a live Facebook Page post and republish its image using
the kept original (uncropped) file instead of the Instagram-cropped one.

Facebook's Graph API has no way to swap the image on an already-published
post, so this deletes the old post and creates a new one with the same
caption. The post gets a new id and timestamp; likes/comments on the old
post are lost. Instagram is left untouched.

Required env vars:
    META_TOKEN, FB_PAGE_ID, GITHUB_REPOSITORY, GITHUB_SHA
    POST_DIR   path to the posted/<folder> to fix, e.g. posted/003-raudrev-to
"""
import json
import os
import pathlib
import posixpath
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v21.0"


def api(path: str, params: dict, method: str = "POST") -> dict:
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}"
    if method == "DELETE":
        url = f"{url}?{data.decode()}"
        req = urllib.request.Request(url, method="DELETE")
    else:
        req = urllib.request.Request(url, data=data)
    try:
        body = urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Graph API error on {method} /{path}: {e.read().decode()[:800]}")
    return json.loads(body)


def fb_original_rel(rel: str) -> str:
    d, name = posixpath.split(rel)
    original = posixpath.join(d, "original", name)
    return original if (ROOT / original).exists() else rel


def main():
    post_dir = ROOT / os.environ["POST_DIR"]
    post_file = post_dir / "post.json"
    post = json.loads(post_file.read_text(encoding="utf-8"))
    old_fb_id = post.get("published", {}).get("facebook")
    if not old_fb_id:
        sys.exit(f"No published.facebook id found in {post_file}")

    token = os.environ["META_TOKEN"]
    page_id = os.environ["FB_PAGE_ID"]
    repo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ.get("GITHUB_SHA", "main")

    def raw_url(rel):
        return f"https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(rel)}"

    rel = post["images"][0]
    original_rel = fb_original_rel(rel)
    if original_rel == rel:
        sys.exit(f"No original kept for {rel} — nothing to switch to")
    image_url = raw_url(original_rel)
    caption = post["caption"].strip()

    print(f"Deleting old Facebook post {old_fb_id}")
    api(old_fb_id, {"access_token": token}, method="DELETE")

    print(f"Republishing with original-format image: {original_rel}")
    photo = api(
        f"{page_id}/photos",
        {"url": image_url, "published": "false", "access_token": token},
    )["id"]
    params = {"message": caption, "access_token": token}
    params["attached_media[0]"] = json.dumps({"media_fbid": photo})
    result = api(f"{page_id}/feed", params)
    new_id = result["id"]
    print(f"Facebook: republished as {new_id}")

    post["published"]["facebook"] = new_id
    post["published"]["facebook_image_fixed"] = True
    post_file.write_text(json.dumps(post, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {post_file}")


if __name__ == "__main__":
    main()
