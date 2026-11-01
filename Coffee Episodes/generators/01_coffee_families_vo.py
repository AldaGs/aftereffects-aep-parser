"""Episode 1 retimed to the recorded voiceover (coffee_vo_f5.wav, 165.2 s).

    python "Coffee Episodes/generators/01_coffee_families_vo.py"   # writes ../json/01_coffee_families_vo.json

Reads schema/examples/coffee_families.json and time-stretches each scene precomp on the master so it starts on its
VO paragraph. Starts come from a Whisper transcript of the recording; re-measure them for a new take.
"""
import json, os

from coffee_common import ROOT, JSON_DIR, HS, A, KL

# paragraph starts in the recording (s), one per scene, and the end of the last scene (VO end + a 3 s hold)
STARTS = [0.0, 8.8, 20.04, 42.5, 63.84, 79.76, 96.96, 108.72, 133.76, 158.66]
END = 165.2 + 3.0

proj = json.load(open(os.path.join(ROOT, "schema", "examples", "coffee_families.json"), encoding="utf-8"))
master = proj["compositions"][0]
pre = sorted([l for l in master["layers"] if l["type"] == "precomp"], key=lambda l: l["startTime"])
assert len(pre) == len(STARTS), len(pre)
bounds = STARTS + [END]
for l, t0, t1 in zip(pre, bounds, bounds[1:]):
    d = l["out"] - l["in"]
    l["stretch"] = round((t1 - t0) / d * 100, 3)
    l["startTime"], l["in"], l["out"] = t0, t0, t1
    l["transform"]["scale"] = A(KL(t0, [100, 100]), KL(t1, [HS * 100, HS * 100]))
for l in master["layers"]:
    if l["type"] != "precomp":
        l["out"] = END
master["duration"] = END
proj["file"] = "01_coffee_families.aep"
with open(os.path.join(JSON_DIR, "01_coffee_families_vo.json"), "w", encoding="utf-8") as f:
    json.dump(proj, f, indent=1, ensure_ascii=False)
print("\n".join(f"{l['source']:16s} {l['startTime']:7.2f}  {l['stretch']:.1f} %" for l in pre))
