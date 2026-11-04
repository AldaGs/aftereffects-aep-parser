"""Episode 1 timed to the recorded voiceover (coffee_vo_f5.wav, 165.2 s), at 24 fps.

    python "Coffee Episodes/generators/01_coffee_families_vo.py"   # writes ../json/01_coffee_families_vo.json

Builds schema/examples/coffee_families.py with one length per scene, so each scene precomp starts on its VO
paragraph. Scenes are re-timed, not time-stretched: start times scale with the scene and snap to frames, and every
in/out animation keeps a whole number of 12-frame beats (see retime() in coffee_families.py). Starts come from a
Whisper transcript of the recording; re-measure them for a new take.
"""
import json, os

from coffee_common import JSON_DIR
import coffee_families as ep1

# paragraph starts in the recording (s), one per scene, and the end of the last scene (VO end + a 3 s hold)
STARTS = [0.0, 8.8, 20.04, 42.5, 63.84, 79.76, 96.96, 108.72, 133.76, 158.66]
END = 165.2 + 3.0

assert len(STARTS) == len(ep1.SCENES)
fr = [ep1.frames(t) for t in STARTS + [END]]
proj = ep1.build([(b - a) / ep1.FPS for a, b in zip(fr, fr[1:])], aep="01_coffee_families.aep", schema="../../schema/motion.schema.json")
with open(os.path.join(JSON_DIR, "01_coffee_families_vo.json"), "w", encoding="utf-8") as f:
    json.dump(proj, f, indent=1, ensure_ascii=False)
pre = sorted([l for l in proj["compositions"][0]["layers"] if l["type"] == "precomp"], key=lambda l: l["startTime"])
print("\n".join(f"{l['source']:16s} {l['startTime']:7.3f}  frame {ep1.frames(l['startTime']):5d}" for l in pre))
print("total", proj["compositions"][0]["duration"], "s at", ep1.FPS, "fps")
