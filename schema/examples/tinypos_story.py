"""Generator for tinypos_story.json, an 18 s 9:16 Instagram story for TinyPOS (see tinypos_story_script.md).

    python schema/examples/tinypos_story.py
    go run ./cmd/json2jsx -i schema/examples/tinypos_story.json

Reuses the keyframe/shape/layer helpers from espresso_explainer.py. Scene starts follow the VO
(tinypos_story_vo.wav, F5-TTS render v2): paragraphs start at 0, 3.42, 6.2, 10.72, 14.36 s, and the VO sits at VO_AT in the master.
"""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from espresso_explainer import K, KS, A, X, G, rect, ell, path, smooth, fill, stroke, trim, shape, text, appear, pop, fade_in, zero_tangents, SANS, SANS_B

W, H, FPS = 1080, 1920, 30
CX, CY = W / 2, H / 2
C = dict(navy="#0d3a66", navy2="#0a2e52", orange="#f28b05", light="#dde8ee", white="#ffffff",
         ink="#12263f", muted="#8fa6bd", red="#e5484d", green="#3fb37f")
VO_AT = 0.4
HERE = os.path.dirname(os.path.abspath(__file__))

def bg(D, col=C["navy"]):
    return shape("BG", [G("BG", rect([W + 400, H + 400]), fill(col))], [CX, CY], 0, D)

def caption(name, s, y, t, D, size=64, col=C["white"], font=SANS_B):
    return appear(text(name, s, [CX, y], size, col, t, D, font=font), t)

def cup(name, pos, t, D, k=1.0):
    body = G("Body", path([(-90, -70), (90, -70), (70, 90), (-70, 90)], True), fill(C["light"]))
    handle = G("Handle", ell([70, 70], [100, 0]), stroke(C["light"], 18))
    coffee = G("Coffee", ell([170, 30], [0, -70]), fill(C["orange"]))
    steam = [G(f"Steam {i}", smooth([(x, -110), (x + 14, -150), (x - 10, -190), (x + 6, -230)]), trim(0, 100), stroke(C["light"], 9, 70))
             for i, x in enumerate((-40, 0, 40))]
    L = shape(name, steam + [coffee, body, handle], pos, t, D, scale=pop(t, 100 * k))
    return L

def wordmark(name, pos, t, D, size=170):
    return text(name, "TinyPOS", pos, size, C["orange"], t, D, scale=pop(t))

# ---------- scenes ----------
def s1_hook(D):
    return [
        wordmark("Wordmark", [CX, 1180], 1.45, D),
        caption("Meet", "Meet", 1000, 1.2, D, 56, C["light"], SANS),
        caption("Q", "Running a\rcoffee bar?", 420, 0.1, D, 92),
        cup("Cup", [CX, 800], 0.25, D, 0.9),
        bg(D),
    ]

def wifi(name, pos, t, D):
    arcs = []
    for i, r in enumerate((60, 120, 180)):
        pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (-135, -112, -90, -68, -45)]
        arcs.append(G(f"Arc {i}", smooth(pts), stroke(C["light"], 26, cap="round")))
    dot = G("Dot", ell([34, 34], [0, -10]), fill(C["light"]))
    slash = G("Slash", path([(-170, -230), (170, 70)]), trim(0, A(K(t + 0.5, 0), K(t + 0.85, 100))), stroke(C["red"], 26))
    return shape(name, [slash, dot] + arcs, pos, t, D, scale=pop(t))

def ticket(name, n, y, t, D):
    card = G("Card", rect([560, 110], r=22), fill(C["light"]))
    tick = G("Tick", ell([44, 44], [220, 0]), fill(C["green"]))
    L = shape(name, [tick, card], [CX, y], t, D)
    return [appear(text(name + " Label", f"Order #{n}   paid", [CX - 50, y + 16], 44, C["ink"], t, D, font=SANS_B), t, dx=-200, dy=0),
            appear(L, t, dx=-200, dy=0)]

def s2_offline(D):
    L = [caption("Head", "Wi-Fi down?", 360, 0.05, D, 84),
         wifi("WiFi", [CX, 720], 0.1, D)]
    for i, n in enumerate((41, 42, 43)):
        L += ticket(f"Ticket {n}", n, 980 + i * 140, 1.0 + i * 0.35, D)
    L += [caption("Cap", "Sales keep going.", 1560, 1.0, D, 70, C["orange"]), bg(D)]
    return L

def s3_precise(D):
    x0, x1 = CX - 230, CX + 230
    rows = [("Latte", "$65.00"), ("Croissant", "$42.50"), ("Extra shot", "$12.00")]
    L = []
    for i, (a, b) in enumerate(rows):
        y, t = 700 + i * 110, 0.5 + i * 0.25
        L += [appear(text(f"Item {i}", a, [x0, y], 50, C["ink"], t, D, font=SANS, just="left"), t, dy=20),
              appear(text(f"Price {i}", b, [x1, y], 50, C["ink"], t, D, font=SANS, just="right"), t, dy=20)]
    t = 1.5
    L += [appear(text("Total", "Total", [x0, 1080], 64, C["navy"], t, D, just="left"), t, dy=20),
          appear(text("Total Price", "$119.50", [x1, 1080], 64, C["navy"], t, D, just="right"), t, dy=20),
          shape("Check", [G("Mark", path([(-34, 2), (-8, 28), (38, -24)]), stroke(C["white"], 14)), G("Disc", ell([120, 120]), fill(C["green"]))],
                [CX + 250, 560], 2.0, D, scale=pop(2.0)),
          shape("Rule", [G("Rule", path([(x0, 980), (x1, 980)]), trim(0, A(K(1.2, 0), K(1.6, 100))), stroke(C["muted"], 5))], [0, 0], 0, D),
          appear(shape("Receipt", [G("Paper", rect([620, 760], r=30), fill(C["white"]))], [CX, 880], 0.15, D), 0.15, dy=120),
          caption("Cap", "Exact to the centavo.", 1460, 2.3, D, 70, C["orange"]),
          caption("Sub", "Totals and taxes always match.", 1560, 2.6, D, 46, C["light"], SANS),
          bg(D)]
    return L

def s4_setup(D):
    t0, t1 = 0.5, 1.6
    bar = shape("Bar Fill", [G("Fill", rect([600, 60], [300, 0], r=30), fill(C["orange"]))], [CX - 300, 900], 0, D,
                scale=A(K(t0, [0, 100]), K(t1, [100, 100])))
    track = shape("Bar Track", [G("Track", rect([600, 60], r=30), fill(C["navy2"]))], [CX, 900], 0, D)
    return [
        caption("Ready", "Ready!", 780, t1, D, 90, C["orange"]),
        bar, track,
        caption("Head", "Set up in seconds.", 520, 0.05, D, 84),
        caption("Sub1", "No servers.", 1150, 2.0, D, 60, C["light"], SANS),
        caption("Sub2", "No tech skills.", 1240, 2.3, D, 60, C["light"], SANS),
        bg(D),
    ]

def s5_cta(D):
    line = shape("Underline", [G("Line", path([(-300, 0), (300, 0)]), trim(0, A(K(0.6, 0), K(1.1, 100))), stroke(C["orange"], 14))],
                 [CX, 1040], 0, D)
    return [
        caption("Tag", "Made for coffee.", 1180, 0.8, D, 72, C["white"]),
        line,
        wordmark("Wordmark", [CX, 990], 0.05, D, 200),
        cup("Cup", [CX, 640], 0.3, D, 0.8),
        bg(D),
    ]

def band(name, t):
    # vertical push: an orange band sweeps bottom -> top across the cut
    t0, t1 = t - 0.3, t + 0.3
    return shape(name, [G("Band", rect([W + 200, 700]), fill(C["orange"]))], A(K(t0, [CX, H + 400], "easeInOut"), K(t1, [CX, -400], "easeInOut")), t0, t1)

def build():
    scenes = [("S1_Hook", 3.65, s1_hook), ("S2_Offline", 2.8, s2_offline), ("S3_Precise", 4.5, s3_precise),
              ("S4_Setup", 3.65, s4_setup), ("S5_CTA", 3.4, s5_cta)]
    comps, main, wipes, t = [], [], [], 0.0
    for idx, (cname, d, fn) in enumerate(scenes):
        layers = fn(d)
        names = [l["name"] for l in layers]
        assert len(names) == len(set(names)), (cname, names)
        assert all(l["out"] > l["in"] for l in layers), cname
        comps.append({"name": cname, "width": W, "height": H, "fps": FPS, "duration": d, "backgroundColor": C["navy"], "layers": layers})
        main.insert(0, {"name": cname, "type": "precomp", "source": cname, "startTime": t, "in": t, "out": t + d,
                        "transform": {"scale": A(KS(t, [100, 100]), KS(t + d, [104, 104]))}})
        if idx:
            wipes.insert(0, band(f"Wipe {idx}", t))
        t += d
    vo = {"name": "VO", "type": "audio", "source": "vo", "startTime": VO_AT, "in": VO_AT, "out": t}
    master = {"name": "TinyPOS_Story", "width": W, "height": H, "fps": FPS, "duration": t, "backgroundColor": C["navy"],
              "layers": [vo] + wipes + main}
    return {"$schema": "../motion.schema.json", "file": "tinypos_story.aep", "expressionEngine": "javascript-1.0",
            "assets": [{"id": "vo", "name": "tinypos_story_vo.wav", "type": "file", "file": os.path.join(HERE, "tinypos_story_vo.wav")}],
            "compositions": [master] + comps}

if __name__ == "__main__":
    proj = build()
    zero_tangents(proj)
    with open(os.path.join(HERE, "tinypos_story.json"), "w", encoding="utf-8") as f:
        json.dump(proj, f, indent=1, ensure_ascii=False)
    print("total", proj["compositions"][0]["duration"])
