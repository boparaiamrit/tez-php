"""Decide which PHP versions this run builds.

Input (the workflow's `versions`): space- or comma-separated. A minor ("8.4") means its newest
patch on php.net; a full version ("8.4.20") means exactly that. Empty means the newest patch of
every minor in MINORS. Versions already listed in the release's index.json are skipped unless
FORCE is true. Writes `matrix` (a JSON list) and `any` to $GITHUB_OUTPUT.
"""
import json
import os
import re
import sys
import urllib.request

MINORS = ["8.1", "8.2", "8.3", "8.4", "8.5"]


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tez-php-build"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def newest_patch(minor):
    data = fetch_json(f"https://www.php.net/releases/index.php?json&version={minor}")
    v = data.get("version")
    if not v:
        # Older entries name the version only in the source file names.
        for s in data.get("source", []):
            m = re.match(r"php-(\d+\.\d+\.\d+)\.tar", s.get("filename", ""))
            if m:
                v = m.group(1)
                break
    if not v or not v.startswith(minor + "."):
        sys.exit(f"php.net has no release for PHP {minor}")
    return v


def published(repo, release):
    url = f"https://github.com/{repo}/releases/download/{release}/index.json"
    try:
        return {b["version"] for b in fetch_json(url)["builds"]}
    except Exception:
        return set()


def main():
    raw = os.environ.get("INPUT", "").replace(",", " ").split()
    force = os.environ.get("FORCE", "false").lower() == "true"
    wanted = []
    for item in raw or MINORS:
        if re.fullmatch(r"\d+\.\d+", item):
            wanted.append(newest_patch(item))
        elif re.fullmatch(r"\d+\.\d+\.\d+", item):
            wanted.append(item)
        else:
            sys.exit(f"not a PHP version: {item}")
    done = set() if force else published(os.environ["GITHUB_REPOSITORY"], os.environ.get("RELEASE", "builds"))
    todo = sorted({v for v in wanted if v not in done}, key=lambda v: [int(x) for x in v.split(".")])
    print("wanted:", " ".join(wanted) or "-")
    print("already built:", " ".join(sorted(done & set(wanted))) or "-")
    print("building:", " ".join(todo) or "nothing")
    with open(os.environ["GITHUB_OUTPUT"], "a") as out:
        out.write(f"matrix={json.dumps(todo)}\n")
        out.write(f"any={'true' if todo else 'false'}\n")


if __name__ == "__main__":
    main()
