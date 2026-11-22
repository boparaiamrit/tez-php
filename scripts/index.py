"""Merge every build's JSON record (fragments/*.build.json) into index.json, newest first."""
import glob
import json

builds = []
for path in glob.glob("fragments/*.build.json"):
    with open(path) as f:
        builds.append(json.load(f))
builds.sort(key=lambda b: ([int(x) for x in b["version"].split(".")], b["arch"]), reverse=True)
with open("index.json", "w") as f:
    json.dump({"builds": builds}, f, indent=1)
    f.write("\n")
print(f"index.json lists {len(builds)} builds")
