#!/usr/bin/env python3
"""Warn when only ~14 days of publishing remain in the current photo round.

A "round" means every photo in assets/ is published `round` times in total.
Round 1 = each photo once, round 2 = each photo twice, and so on. The round
number lives in round-state.json and is only raised when the owner approves it.

remaining publications N = posts waiting in queue/
                         + sum over photos of max(0, round - times used)
where "times used" counts posted/ and queue/ entries. N is turned into a date
by walking the Tue/Fri/Sun publishing schedule; when that date is <= 14 days
away the script opens ONE GitHub issue (mentioning the owner) per round.

Env:
    GH_TOKEN, GITHUB_REPOSITORY   needed to open/close issues
    CHECK_ONLY=1                  print the result, change nothing
    FORCE_TEST_ISSUE=1            open a clearly-marked test issue, no state change
"""
import datetime as dt
import glob
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "round-state.json"
THRESHOLD_DAYS = 14
PUBLISH_WEEKDAYS = {1, 4, 6}  # Tue, Fri, Sun (Mon=0)
ISSUE_PREFIX = "Varsel: 14 dagar att med unike bilete"
OWNER_MENTION = "@Alcesalces69"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"round": 1, "alerted_round": 0}


def read_posts(pattern):
    posts = []
    for f in sorted(glob.glob(str(ROOT / pattern))):
        posts.append(json.loads(pathlib.Path(f).read_text(encoding="utf-8")))
    return posts


def image_names(post):
    names = []
    for rel in post.get("images", []):
        if rel.startswith("assets/") and "/story/" not in rel:
            names.append(rel.split("/", 1)[1])
    return names


def compute(round_no, today):
    photos = sorted(p.name for p in (ROOT / "assets").glob("*.jpg"))
    posted = read_posts("posted/*/post.json")
    queued = read_posts("queue/*/post.json")

    used = {name: 0 for name in photos}
    for post in posted + queued:
        for name in image_names(post):
            if name in used:
                used[name] += 1

    deficit = sum(max(0, round_no - n) for n in used.values())
    remaining = len(queued) + deficit

    published_today = any(
        str(p.get("published", {}).get("at", "")).startswith(today.isoformat())
        for p in posted
    )
    day = today + dt.timedelta(days=1 if published_today else 0)
    last_slot = None
    counted = 0
    while counted < remaining:
        if day.weekday() in PUBLISH_WEEKDAYS:
            counted += 1
            last_slot = day
        day += dt.timedelta(days=1)

    days_left = (last_slot - today).days if last_slot else -1
    return {
        "round": round_no,
        "photos": len(photos),
        "queued": len(queued),
        "not_yet_queued": deficit,
        "remaining_publications": remaining,
        "last_publish_date": last_slot.isoformat() if last_slot else None,
        "days_left": days_left,
    }


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def open_alert_issue(info, test=False):
    r = info["round"]
    nxt = r + 1
    times = f"{nxt} gongar" if nxt > 1 else "ein gong"
    title = ("[TEST] " if test else "") + f"{ISSUE_PREFIX} (runde {r})"
    body = (
        f"{OWNER_MENTION}\n\n"
        f"Det er berre **{info['remaining_publications']} publiseringar** att i runde {r}. "
        f"Siste bilete blir publisert ca. **{info['last_publish_date']}** "
        f"({info['days_left']} dagar).\n\n"
        f"- {info['queued']} innlegg ligg i køa\n"
        f"- {info['not_yet_queued']} bilete er ikkje lagde i kø enno\n\n"
        f"**Kva no?**\n"
        f"1. Legg nye bilete i Drive-mappa. Dei blir henta automatisk kvar måndag, og "
        f"dette varselet lukkar seg sjølv når det er over 14 dagar att.\n"
        f"2. Eller godkjenn runde {nxt}: sei ifrå til Claude «godkjenn runde {nxt}». "
        f"Då blir kvart bilete publisert {times} totalt, og neste varsel kjem 14 dagar "
        f"før siste bilete blir publisert for {nxt}. gong.\n\n"
        f"Gjer du ingenting, stoppar publiseringa av seg sjølv når køen er tom."
    )
    if test:
        body = "Dette er ein test av varselkanalen - ingenting du må gjere.\n\n" + body
    gh("issue", "create", "--title", title, "--body", body)
    print(f"Opened issue: {title}")


def close_open_alert_issues():
    out = gh("issue", "list", "--state", "open", "--search", f'"{ISSUE_PREFIX}" in:title',
             "--json", "number,title")
    for issue in json.loads(out):
        if issue["title"].startswith(ISSUE_PREFIX):
            gh("issue", "close", str(issue["number"]), "--comment",
               "Over 14 dagar med unike bilete att igjen - lukkar varselet automatisk.")
            print(f"Closed issue #{issue['number']}")


def main():
    check_only = os.environ.get("CHECK_ONLY") == "1"
    state = load_state()
    today = dt.datetime.now(dt.timezone.utc).date()
    info = compute(state["round"], today)
    print(json.dumps(info, indent=2))

    if os.environ.get("FORCE_TEST_ISSUE") == "1":
        open_alert_issue(info, test=True)
        return
    if check_only:
        return

    changed = False
    if info["days_left"] <= THRESHOLD_DAYS:
        if state.get("alerted_round") != state["round"]:
            open_alert_issue(info)
            state["alerted_round"] = state["round"]
            changed = True
    elif state.get("alerted_round") == state["round"]:
        close_open_alert_issues()
        state["alerted_round"] = 0
        changed = True

    if changed:
        STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
