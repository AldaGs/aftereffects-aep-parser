"""Generator for episode 9, "Who Gets Paid for Your Coffee" (scripts/09_who_gets_paid_script.md).

    python "Coffee Episodes/generators/09_who_gets_paid.py"      # writes ../json/09_who_gets_paid.json

Uses episode 8's camera (cam/finish): content coordinates are screen pixels and the master push-in is cancelled.
The C-price chart is one content drawing (1962-2026); scenes frame it with a Chart Rig null. No fades.

Follows episode 1's rules: 24 fps, every in/out animation a whole number of 12-frame beats (write(..., beats=True)),
and drawn vectors: episode 1's coffee cherry and cross-section in the close, bean outlines on the pans, a rounded
latte cup, jute sacks with a gathered neck.
"""
import importlib, math, random

from coffee_common import *  # noqa: F401,F403

_e8 = importlib.import_module("08_roasting")
cam, finish, tag, arrow = _e8.cam, _e8.finish, _e8.tag, _e8.arrow

C = (CX, CY)
SLIVER = (CX, 820)          # 1->2, 10->: the 15c sliver, 300 x 24
LATTE_TOP = 32


def hold(D):
    return cam(D, name="Hold")


def hatch(name, pos, t0, t1, w=90, h=20, q=True, **tr):
    lines = [path([(x, h / 2), (x + h, -h / 2)]) for x in range(int(-w / 2), int(w / 2) - h + 1, 14)]
    return shape(name, [G("H", *lines, stroke(INK, 1.5)), G("B", rect([w, h]), stroke(INK, 2), fill(GREY2))], pos, t0, t1, **tr)


def latte_bar(t0, t1, grow_t=None, sliver_t=None):
    h = SLIVER[1] + 12 - LATTE_TOP
    out = []
    if sliver_t is not None:
        out.append(shape("Sliver", [G("S", rect([300, 24]), fill(INK))], list(SLIVER), sliver_t, t1, scale=A(K(sliver_t, [100, 0]), K(sliver_t + 0.4, [100, 100]))))
    out.append(text("Latte Total", "$5.00", [CX - 180, LATTE_TOP + 40], 40, INK, t0, t1, font=HEAD, just="right"))
    sc = A(K(grow_t, [100, 0]), K(grow_t + 0.6, [100, 100])) if grow_t is not None else [100, 100]
    out.append(shape("Latte Bar", [G("B", rect([300, h], [0, -h / 2]), stroke(INK, 2), fill(LINE))], [CX, SLIVER[1] + 12], t0, t1, scale=sc))
    return out


def cup(name, pos, t0, t1, **tr):
    return shape(name, [G("Foam", ell([150, 30], [0, -70]), fill(KRAFT)),
                        G("Handle", ell([50, 60], [92, -10]), stroke(INK, 5)),
                        G("Cup", smooth([(-92, -70), (92, -70), (84, 0), (60, 46), (28, 62), (-28, 62), (-60, 46), (-84, 0)], True, corners=(0, 1)),
                          stroke(INK, 5), fill(WHITE)),
                        G("Saucer", ell([300, 40], [0, 70]), stroke(INK, 5), fill(WHITE))], pos, t0, t1, **tr)


def person(name, pos, t0, t1, **tr):
    return shape(name, [G("Head", ell([40, 40], [0, -70]), stroke(INK, 4), fill(WHITE)),
                        G("Body", path([(-34, 30), (-34, -20), (34, -20), (34, 30)], False, i=[(0, 0), (0, 20), (-20, 0), (0, 0)], o=[(0, -20), (20, 0), (0, 20), (0, 0)]),
                          stroke(INK, 4))], pos, t0, t1, **tr)


def snowflake(name, pos, t0, t1):
    return shape(name, [G("F", *[path([(-22 * math.cos(a), -22 * math.sin(a)), (22 * math.cos(a), 22 * math.sin(a))]) for a in (0, math.pi / 3, 2 * math.pi / 3)],
                          stroke(INK, 4))], pos, t0, t1, scale=grow(t0))


def sun(name, pos, t0, t1):
    rays = [path([(26 * math.cos(a), 26 * math.sin(a)), (36 * math.cos(a), 36 * math.sin(a))]) for a in [k * math.pi / 4 for k in range(8)]]
    return shape(name, [G("R", *rays, stroke(INK, 4)), G("S", ell([36, 36]), stroke(INK, 4), fill(HL))], pos, t0, t1, scale=grow(t0))


def sack(name, pos, t0, t1, col=KRAFT, s=100, **tr):
    return shape(name, [G("Tie", path([(-8, -26), (8, -26)]), stroke(INK, 3)),
                        G("S", smooth([(-10, -26), (-6, -22), (6, -22), (10, -26), (18, -10), (24, 14), (18, 25), (0, 27), (-18, 25), (-24, 14), (-18, -10)], True,
                                      corners=(0, 3)), stroke(INK, 3), fill(col))], pos, t0, t1,
                 scale=tr.pop("scale", [s, s]), **tr)


# ---------------------------------------------------------------------
# rail (S3, S4)
# ---------------------------------------------------------------------
RAIL = [("EXCHANGE", 460), ("EXPORTER", 820), ("COYOTE", 1180), ("FARM", 1540)]
RAIL_Y = 990


def rail(t0, t1, fills):
    out = []
    for j, (nm, x) in enumerate(RAIL):
        ft = fills.get(j)
        out.append(caps(f"Rail {nm}", f"{j + 1} {nm}", [x + 22, RAIL_Y + 6], t0, t1, size=13, color=INK, just="left"))
        if ft is not None:
            out.append(shape(f"Rail Fill {j + 1}", [G("F", ell([18, 18]), fill(INK))], [x, RAIL_Y], ft, t1, scale=grow(ft, 100, 0.3)))
        out.append(shape(f"Rail Stop {j + 1}", [G("S", ell([26, 26]), stroke(INK, 3), fill(WHITE))], [x, RAIL_Y], t0, t1))
    out.append(shape("Rail Line", [G("L", path([(RAIL[0][1], RAIL_Y), (RAIL[-1][1], RAIL_Y)]), stroke(GREY2, 3))], [0, 0], t0, t1))
    return out


# ---------------------------------------------------------------------
# the C-price chart (S5, S6, S7, S9), content coordinates 1962-2026
# ---------------------------------------------------------------------
PRICE = [(1962, 34), (1963, 34), (1964, 46), (1965, 42), (1966, 40), (1967, 38), (1968, 38), (1969, 40), (1970, 52), (1971, 45), (1972, 50),
         (1973, 63), (1974, 66), (1975, 72), (1976, 142), (1977, 230), (1978, 155), (1979, 170), (1980, 155), (1981, 125), (1982, 130),
         (1983, 132), (1984, 142), (1985, 135), (1986, 175), (1987, 110), (1988, 120), (1989, 85), (1990, 70), (1991, 65), (1992, 53),
         (1993, 62), (1994, 140), (1995, 145), (1996, 120), (1997, 180), (1998, 130), (1999, 100), (2000, 85), (2001, 45), (2002, 50),
         (2003, 60), (2004, 75), (2005, 105), (2006, 108), (2007, 120), (2008, 135), (2009, 125), (2010, 165), (2011, 270), (2012, 185),
         (2013, 125), (2014, 175), (2015, 135), (2016, 140), (2017, 140), (2018, 115), (2019, 100), (2020, 111), (2021, 170), (2022, 215),
         (2023, 175), (2024, 260), (2024.6, 396), (2025.5, 360), (2026, 300)]
LOW01, FEB25 = (2001, 45), (2024.6, 396)


def yx(year):
    return 200 + (year - 1962) * 23.75


def py(p):
    return 820 - p * 0.9


PTS = [(yx(y), py(p)) for y, p in PRICE]
_CL = [0.0]
for a, b in zip(PTS, PTS[1:]):
    _CL.append(_CL[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))


def frac(year):
    """Trim percentage of the price line at a year."""
    for j in range(len(PRICE) - 1):
        if PRICE[j + 1][0] >= year:
            u = (year - PRICE[j][0]) / (PRICE[j + 1][0] - PRICE[j][0])
            return round((_CL[j] + (_CL[j + 1] - _CL[j]) * u) / _CL[-1] * 100, 3)
    return 100.0


def ax_frac(year):
    return round((year - 1962) / 64 * 100, 3)


def chart(t0, t1, rg, start=0, end=100, axis_start=0, decades_t=None):
    """start/end: trim of the price line (number or animated); axis_start: trim start of axis and grid."""
    out = [shape("Price Line", [G("L", path(PTS), trim(start, end), stroke(INK, 4))], [0, 0], t0, t1, parent=rg)]
    for p in (100, 200, 300, 400):
        out.append(caps(f"Grid {p}", f"{p}¢", [yx(2026) + 12, py(p) + 5], t0, t1, size=12, color=GREY, just="left", parent=rg))
    out.append(caps("Unit", "C PRICE, ¢ / LB", [yx(2026), py(440)], t0, t1, size=13, color=INK, just="right", parent=rg))
    out.append(shape("Grid", [G("G", *[path([(yx(1962), py(p)), (yx(2026), py(p))]) for p in (100, 200, 300, 400)], trim(axis_start, 100), stroke(LINE, 2))],
                     [0, 0], t0, t1, parent=rg))
    out.append(shape("Time Axis", [G("A", path([(yx(1962), 820), (yx(2026), 820)]), trim(axis_start, 100), stroke(INK, 3))], [0, 0], t0, t1, parent=rg))
    for y in range(1970, 2030, 10):
        t = t0 if y >= 1990 or decades_t is None else decades_t
        out.append(caps(f"Year {y}", str(y), [yx(y), 850], t, t1, size=13, color=INK, parent=rg))
    if decades_t is not None:
        out.append(caps("Year 1962", "1962", [yx(1962), 850], decades_t, t1, size=13, color=INK, parent=rg))
    return out


S5_S = 1.38
S5_P = (620 - yx(1990) * S5_S, 860 - 820 * S5_S)


def chart_rig(D, keys=None):
    keys = keys or [(0, (0, 0), 1)]
    return null("Chart Rig", [0, 0], 0, D, anchor=[0, 0], position=A(*[K(t, list(P)) for t, P, s in keys]),
                scale=A(*[K(t, [s * 100, s * 100]) for t, P, s in keys]))


# corridor bands (year0, year1, low, high) and which ones are the suspensions
BANDS = [(1963, 1972.9, 28, 62), (1972.9, 1980.8, 50, 90), (1980.8, 1986.1, 110, 150), (1986.1, 1987.8, 100, 140), (1987.8, 1989.5, 100, 140)]
GAPS = (1, 3)


def bands(t0, t1, rg, cut=None, drop=None):
    out = []
    for j, (a, b, lo, hi) in enumerate(BANDS):
        tr = {}
        out_t = t1
        if cut is not None and j in GAPS:
            out_t = cut
        if drop is not None:
            tr["position"] = A(K(drop + j * 0.15, [0, 0]), K(drop + j * 0.15 + 1.0, [0, 600], {"inInfluence": 10, "outInfluence": 70, "inSpeed": 0, "outSpeed": 0}))
            out_t = min(out_t, drop + j * 0.15 + 1.0)
        out.append(shape(f"Band {j + 1}", [G("B", rect([yx(b) - yx(a), (hi - lo) * 0.9], [(yx(a) + yx(b)) / 2, py((lo + hi) / 2)]), fill(GREY2))],
                         [0, 0], t0, out_t, parent=rg, **tr))
    return out


# ---------------------------------------------------------------------
# Mexico map (S8, S9), content coordinates at MK px per degree
# ---------------------------------------------------------------------
MK, MC, MO = 22, (-102, 23.5), (760, 130)
UCIRI = (-95.03, 16.56)


def mpt(ll):
    return screen(ll, MK, MC, MO)


def mexico(name, t0, t1, world=False):
    st = [path([mpt(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    out = [shape(name, [G("Borders", *st, stroke(WHITE, 1.5)), G("States", *st, fill(LAND))], [0, 0], t0, t1)]
    if world:
        land = [path([mpt(p) for p in r], True) for r in GEO["land"]
                if not (max(p[0] for p in r) < -130 or min(p[0] for p in r) > 30 or max(p[1] for p in r) < -10 or min(p[1] for p in r) > 72)]
        out.append(shape(f"{name} World", [G("Land", *land, fill(LAND))], [0, 0], t0, t1))
    return out


def in_rings(rings, lon, lat):
    hit = False
    for r in rings:
        n = len(r)
        for i in range(n):
            (x1, y1), (x2, y2) = r[i], r[(i + 1) % n]
            if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                hit = not hit
    return hit


def state_points(name, n, rnd):
    rings = GEO["mexico"][name]
    lo = [p[0] for r in rings for p in r]
    la = [p[1] for r in rings for p in r]
    pts = []
    while len(pts) < n:
        p = (rnd.uniform(min(lo), max(lo)), rnd.uniform(min(la), max(la)))
        if in_rings(rings, *p):
            pts.append(p)
    return pts


# =====================================================================
# SCENE 1 - A NUMBER IN NEW YORK (20 s)
# =====================================================================
def s1_ticker(D):
    L = []
    b0, c0, d0 = 5.0, 9.0, 14.0
    tick = [text("Ticker", 'COFFEE "C"  ≈ 295 ¢/LB', [CX, 250], 64, INK, 0.3, d0, font=HEAD),
            caps("Ticker Run", "KC · ICE FUTURES U.S. · NEW YORK", [CX, 320], 0.6, d0, size=14, color=INK),
            shape("Board", [G("B", rect([1100, 180], [CX, 270], 6), stroke(INK, 4))], [0, 0], 0.2, d0, scale=grow(0.2)),
            src("Src ICE", "SOURCE: ICE FUTURES U.S., 7 OCT 2026", 0.8, c0)]
    chi = mpt_small(state_centroid("Chiapas"))
    mx = [shape("Leader Drop", [G("L", path([(560, 362), list(chi)]), trim(0, A(K(b0, 0), K(b0 + 0.8, 100))), stroke(INK, 2.5))], [0, 0], b0, d0),
          disc("Chiapas Dot", list(chi), 24, MX, b0 + 0.8, d0, sh=0, scale=grow(b0 + 0.8)),
          tag("Chiapas Label", "CHIAPAS", [chi[0] + 24, chi[1] + 6], b0 + 1.0, d0, size=14, just="left"),
          shape("Mexico Small", [G("M", *[path([mpt_small(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings], fill(LAND))], [0, 0], b0, d0)]
    latte = [tag("Receipt", "LATTE ≈ $5.00", [1420, 820], c0 + 0.8, d0, size=22),
             src("Src Square", "SOURCE: SQUARE CAFÉ PRICE DATA, 2026", c0, D),
             cup("Cup", [1420, 640], c0, d0, scale=grow(c0))]
    L += tick + mx + latte
    for l in L:
        if l["name"] != "Src Square":
            add_out(l, min(l["out"], d0))
    L.append(tag("Sliver Label", "≈ 15¢: THE COFFEE", [CX + 180, SLIVER[1] + 8], d0 + 2.0, D, size=18, just="left"))
    L += latte_bar(d0, D, grow_t=d0, sliver_t=d0 + 1.6)
    return finish(L, D)


def mpt_small(ll):
    return screen(ll, 9, (-102, 23.5), (520, 640))


# =====================================================================
# SCENE 2 - TWENTY-TWO GRAMS (24 s)
# =====================================================================
GRID = [(CX - 285 + (j % 20) * 30, 480 + (j // 20) * 30) for j in range(100)]
INK3 = (97, 98, 99)


def pan(prefix, x, t0, t1, col, grams, n, rnd, **tr):
    out = [text(f"{prefix} Readout", grams, [x, 930], 36, INK, t0 + 2.4, t1, font=HEAD)]
    for j in range(n):
        t = t0 + 0.4 + j * 0.08
        p = [round(x + rnd.uniform(-110, 110), 1), round(SLIVER[1] - 22 - rnd.uniform(0, 40) * (1 - abs(j / n - 0.5)), 1)]
        out.append(shape(f"{prefix} Bean {j + 1}", [G("Cut", smooth([(-12, 0), (-4, -2), (4, 2), (12, 0)], False), stroke(INK, 1.5, 60)), G("B", _e8.bean_shape(34, 24), stroke(INK, 2), fill(col))], A(K(t, [p[0], 300]), K(t + 0.5, p)), t, t1,
                         rotation=rnd.uniform(-40, 40)))
    out.append(shape(f"{prefix} Scale", [G("Rim", rect([300, 24]), fill(INK)), G("Base", rect([200, 110], [0, 85], 8), stroke(INK, 4), fill(WHITE))],
                     [x, SLIVER[1]], t0, t1, **tr))
    return out


def s2_grams(D):
    L = []
    s0, b0, c0 = 3.0, 12.0, 16.0
    rnd = random.Random(9)
    L.append(tag("Sixth", "THE ROAST TAKES ABOUT A SIXTH OF THE WEIGHT", [CX, 300], s0 + 3.0, c0, size=16))
    L.append(src("Src Illy", "SOURCE: ILLY & VIANI, ESPRESSO COFFEE (2005)", s0 + 3.0, b0))
    L.append(tag("Price Tag", "≈ $3.00 / LB, OCT 2026", [1280, 620], b0, b0 + 2.2, size=18))
    L.append(tag("Cents Tag", "≈ 15¢", [1280, 620], b0 + 2.2, c0, size=26))
    L += pan("Green", 1280, s0, c0, SEED, "22 g", 22, rnd, scale=grow(s0))
    roast = pan("Roast", CX, 0, c0, ROAST[3], "18 g", 18, rnd)
    sc = roast[-1]
    sc["transform"]["position"] = A(K(s0 - 0.6, list(SLIVER)), K(s0, [640, SLIVER[1]]))
    sc["shapes"][1]["transform"] = {"opacity": fade_in(0.2)}
    for l in roast[:-1]:
        p = l["transform"]["position"]
        if isinstance(p, dict):
            for k in p["keyframes"]:
                k["value"] = [k["value"][0] - CX + 640, k["value"][1]]
        else:
            l["transform"]["position"] = [p[0] - CX + 640, p[1]]
        l["in"] = max(l["in"], s0)
        l["out"] = c0
    for l in roast[1:-1]:
        l["in"] = s0 + 0.1
        p = l["transform"]["position"]["keyframes"]
        dt = s0 + 0.1 - p[0]["time"]
        for k in p:
            k["time"] = round(k["time"] + dt, 3)
    roast[0]["in"] = s0 + 2.4
    L += roast
    for l in L:
        if l["out"] == c0:
            add_out(l, c0 - 0.3)
    # B: the strip of 100
    L.append(tag("Pct", "3 %", [CX + 330, 545], c0 + 1.4, D, size=28, just="left"))
    L.append(src("Src ICE", "SOURCE: ICE FUTURES U.S.", c0 + 0.4, D))
    for j, p in enumerate(GRID):
        t = c0 + 0.2 + j * 0.008
        ink = j in INK3
        L.append(shape(f"Cell {j + 1}", [G("C", rect([24, 24]), stroke(INK, 1.5), fill(A(K(c0 + 1.2, LINE), K(c0 + 1.4, INK)) if ink else LINE))],
                       list(p), t, D, scale=grow(t, 100, 0.2)))
    return finish(L, D)


# =====================================================================
# SCENE 3 - THE C PRICE (23 s)
# =====================================================================
START3 = (360, 560)
JAG = [(360, 560), (460, 520), (540, 590), (640, 470), (740, 540), (840, 430), (940, 500), (1040, 420), (1140, 470), (1240, 380), (1340, 450), (1440, 400)]
UP, DOWN = (1500, 300), (1560, 520)


def s3_exchange(D):
    L = []
    a1, b0, c0, d0 = 1.2, 7.0, 12.0, 19.0
    f0, h0 = c0 + 1.0, c0 + 3.6
    cum = [0.0]
    for a, b in zip(JAG, JAG[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    keys = [K(a1 + (b0 - 1.2 - a1) * c / cum[-1], list(p), None) for p, c in zip(JAG, cum)]
    dot_pos = A(*keys, K(f0, list(JAG[-1]), None), K(f0 + 0.6, list(UP), None), K(h0, list(UP), None), K(h0 + 0.6, list(DOWN), None))
    L.append(disc("Line Dot", list(START3), 24, INK, a1, d0, sh=0, position=dot_pos))
    L.append(shape("Jump", [G("J", path([JAG[-1], UP, DOWN]), trim(0, A(K(f0, 0), K(f0 + 0.6, 42), K(h0, 42), K(h0 + 0.6, 100))), stroke(INK, 5))], [0, 0], f0, d0))
    L.append(shape("Jagged", [G("J", path(JAG), trim(0, A(*[K(k["time"], round(c / cum[-1] * 100, 2), None) for k, c in zip(keys, cum)])), stroke(INK, 5))], [0, 0], a1, d0))
    for j, p in enumerate(GRID[97:]):
        L.append(shape(f"Square {j + 1}", [G("S", rect([24, 24]), fill(INK))], A(K(0, list(p)), K(a1, list(START3))), 0, a1 + 0.1))
    L.append(tag("Board Label", 'COFFEE "C" FUTURES · ICE · NEW YORK', [CX, 230], a1, d0, size=18))
    L.append(shape("Board", [G("B", rect([1400, 420], [CX, 470], 6), stroke(INK, 4))], [0, 0], 0.4, d0, scale=grow(0.4)))
    # B: traders who never touch a sack
    L.append(person("Trader 1", [760, 830], b0, d0, scale=grow(b0)))
    L.append(person("Trader 2", [1060, 830], b0 + 0.3, d0, scale=grow(b0 + 0.3)))
    L.append(shape("Slip", [G("S", rect([40, 28], None, 3), stroke(INK, 3), fill(WHITE))], A(K(b0 + 1.0, [800, 790]), K(b0 + 2.2, [1020, 790])), b0 + 1.0, d0))
    L.append(sack("Sack", [1300, 850], b0 + 1.4, d0, s=140, opacity=A(K(b0 + 1.4, 0), K(b0 + 1.7, 35))))
    L.append(tag("Never", "MOST NEVER TOUCH A BEAN", [1300, 930], b0 + 2.4, d0, size=13))
    # C: Brazil frost and harvest; Chiapas dips with the fall
    L.append(tag("Brazil", "BRAZIL", [1680, 330], f0 - 0.4, d0, size=14))
    L.append(snowflake("Frost", [1680, 270], f0 - 0.2, h0))
    L.append(sack("Harvest", [1680, 270], h0 - 0.2, d0, col=MX, scale=grow(h0 - 0.2)))
    L.append(disc("Chiapas", [1680, 820], 24, MX, h0, d0, sh=0, scale=grow(h0), position=A(K(h0 + 0.2, [1680, 760]), K(h0 + 1.0, [1680, 840]))))
    L.append(tag("Chiapas Label", "CHIAPAS", [1680, 890], h0 + 0.2, d0, size=13))
    L.append(leader("Fall Leader", DOWN, (1670, 750), h0 + 0.6, d0, dot=False))
    for l in L:
        add_out(l, min(l["out"], d0))
    L.append(shape("Price Bar", [G("B", rect([1400, 20], [700, 0]), fill(INK))], [260, 300], d0 + 0.4, D, scale=A(K(d0 + 0.4, [0, 100]), K(d0 + 1.2, [100, 100]))))
    L += rail(0.6, D, {0: a1 + 0.4})
    return finish(L, D)


# =====================================================================
# SCENE 4 - THE TRIP BACK UP THE HILL (44 s)
# =====================================================================
STOPS = [("NEW YORK", 260), ("VERACRUZ PORT", 620), ("DRY MILL", 900), ("ROADHEAD", 1220), ("HILLSIDE, CHIAPAS", 1560)]
ROUTE_Y = 680
FULL = 1400


def s4_chain(D):
    L = []
    a0, b0, c0, d0, e0, x0 = 1.0, 9.0, 17.0, 24.0, 30.0, 41.0
    w1 = (FULL - 360) / FULL * 100
    w2 = (FULL - 450) / FULL * 100
    w3 = 812 / FULL * 100
    # A: the differential
    for l in [tag("Diff", "C ± DIFFERENTIAL", [CX, 260], a0 + 0.6, b0, size=18),
              tag("Par", "MEXICO: AT PAR ON THE EXCHANGE", [CX, 370], a0 + 2.0, b0, size=16),
              tag("Real", "A REAL SHIPMENT: ABOVE OR BELOW, BY QUALITY", [CX, 404], a0 + 3.4, b0, size=14),
              src("Src Rules", 'SOURCE: ICE COFFEE "C" RULES', a0 + 2.0, b0)]:
        L.append(add_out(l, b0))
    # B, C: the exporter's four unknowns and the coyote's one drop off the bar's end
    names = ["MILLING", "SHIPPING", "FINANCE", "MARGIN"]
    for j, nm in enumerate(names):
        t = b0 + 1.0
        x0b = 260 + FULL - 360 + 45 + 90 * j
        dst = (STOPS[1][1] + 140 * (j - 1.5) + 140, 470) if False else (700 + 100 * j, 470)
        L.append(caps(f"Q {nm}", "?", [dst[0], dst[1] - 18], t + 1.0, e0, size=16, color=INK))
        L.append(caps(f"N {nm}", nm, [dst[0], dst[1] + 34], t + 1.2, e0, size=11, color=INK))
        L.append(hatch(f"Cut {nm}", list(dst), t, e0, position=A(K(t, [x0b, 300]), K(t + 1.0, list(dst)))))
    L.append(tag("Exporter", "EXPORTER", [850, 560], b0 + 2.0, e0, size=14))
    L.append(caps("Q Coyote", "?", [1220, 452], c0 + 2.0, e0, size=16, color=INK))
    L.append(hatch("Cut Coyote", [1220, 470], c0 + 1.0, e0, position=A(K(c0 + 1.0, [260 + FULL - 405, 300]), K(c0 + 2.0, [1220, 470]))))
    L.append(tag("Coyote", "COYOTE", [1220, 620], c0 + 0.6, e0, size=14))
    L.append(truck("Truck", [1220, 580], c0 + 0.4, e0, scale=grow(c0 + 0.4)))
    L.append(shape("Track", [G("T", path([(1270, ROUTE_Y), (1540, ROUTE_Y)]), trim(0, A(K(c0 + 2.6, 0), K(c0 + 3.4, 100))), stroke(INK, 3, dashes=(12, 10)))],
                   [0, 0], c0 + 2.6, e0))
    # D: the peso dial
    L.append(tag("Dial Label", "$ → MXN", [1560, 470], d0 + 0.4, e0, size=14))
    L.append(caps("Dial Strong", "STRONGER PESO", [1660, 540], d0 + 0.8, e0, size=11, color=INK, just="left"))
    L.append(shape("Dial", [G("N", path([(0, 0), (0, -40)]), stroke(INK, 4), tr={"rotation": A(K(d0 + 1.2, -50), K(d0 + 3.0, 50))}),
                            G("D", ell([100, 100]), stroke(INK, 4), fill(WHITE))], [1560, 560], d0, e0, scale=grow(d0)))
    # the route
    rt = [shape("Route", [G("R", path([(STOPS[0][1], ROUTE_Y), (STOPS[3][1], ROUTE_Y)]), trim(0, A(K(0.4, 0), K(1.4, 100))), stroke(INK, 3))], [0, 0], 0.4, D)]
    for j, (nm, x) in enumerate(STOPS):
        rt.append(caps(f"Stop {j + 1}", nm, [x, ROUTE_Y + 40], 0.6 + j * 0.2, D, size=12, color=INK))
        rt.append(shape(f"Stop Dot {j + 1}", [G("D", ell([14, 14]), fill(INK))], [x, ROUTE_Y], 0.6 + j * 0.2, D))
    rl = rail(0, D, {0: -1, 1: a0, 2: c0, 3: d0})
    for l in rl:
        l["in"] = max(l["in"], 0)
    for l in L:
        add_out(l, min(l["out"], e0))
    L += rt + rl
    dim([l for l in L if l["out"] > e0], e0)
    # E: the remainder turns green; cherries to green coffee; the share
    for l in L:
        add_out(l, min(l["out"], x0))
    e = [tag("Ratio", "≈ 6 KG CHERRY → 1 KG GREEN", [CX, 600], e0 + 2.4, e0 + 5.6, size=16),
         sack("Green Sack", [1060, 470], e0 + 2.0, e0 + 5.8, col=SEED, s=200, scale=grow(e0 + 2.0, 200))]
    for j in range(6):
        t = e0 + 0.8 + j * 0.15
        e.append(disc(f"Cherry {j + 1}", A(K(t, [600 + 50 * j, 470]), K(e0 + 2.4 + j * 0.1, [1060, 470])), 40, ARA, t, e0 + 2.4 + j * 0.1, sh=0, scale=grow(t)))
    for l in e:
        add_out(l, min(l["out"], e0 + 5.6))
    h0 = e0 + 6.0
    e += [tag("Share", "≈ ½ TO ⅔ OF THE NEW YORK PRICE (2020)", [CX, 250], h0 + 0.4, x0, size=16),
          src("Src SIAP", "SOURCE: SIAP PRECIO MEDIO RURAL, CAFÉ CEREZA 2020; ICE; BANXICO", h0 + 0.4, x0),
          shape("Ghost", [G("G", rect([FULL, 20], [FULL / 2, 0]), stroke(GREY, 2, dashes=(10, 8)))], [260, 300], h0, x0),
          tag("Farmer Cents", "≈ 8–10¢", [CX + 180, 438], h0 + 2.6, x0, size=18, just="left"),
          shape("Farmer Part", [G("F", rect([180, 14], [90, 0]), fill(MX))], [CX - 150, 430], h0 + 2.6, x0, scale=A(K(h0 + 2.6, [0, 100]), K(h0 + 3.0, [100, 100]))),
          shape("Mini Sliver", [G("S", rect([300, 24]), fill(INK))], [CX, 430], h0 + 2.0, x0, scale=grow(h0 + 2.0)),
          tag("Mini Label", "≈ 15¢", [CX - 180, 438], h0 + 2.2, x0, size=16, just="right")]
    for l in e[-7:]:
        add_out(l, min(l["out"], x0))
    L = e + L
    L.insert(0, disc("Chiapas Dot", [1560, 300], 24, MX, x0, D, sh=0, position=A(K(x0 + 0.4, [CX, 300]), K(D - 0.6, list(C))), scale=grow(x0, 100, 0.3)))
    bar = shape("Price Bar", [G("B", rect([FULL, 20], [FULL / 2, 0]), fill(A(K(e0 + 0.4, INK), K(e0 + 1.0, MX))))], [260, 300], 0, x0 + 0.4,
                scale=A(K(b0 + 0.4, [100, 100]), K(b0 + 1.0, [w1, 100]), K(c0 + 1.0, [w1, 100]), K(c0 + 1.6, [w2, 100]),
                        K(d0 + 1.2, [w2, 100]), K(d0 + 3.0, [w3, 100]), K(x0, [w3, 100]), K(x0 + 0.4, [0, 100])))
    L.insert(1, bar)
    return finish(L, D)


# =====================================================================
# SCENE 5 - ONE FARM, TWO PRICES (25 s)
# =====================================================================
PLOT = (200, 150, 240)


def s5_swing(D):
    L = []
    a1, b0, m1, m2, x0 = 1.0, 6.0, 10.0, 15.0, 22.0
    rg = "Chart Rig"
    x, y, s = PLOT
    col = [tag("Plot Label", "2 HA", [x + s / 2, y + s + 52], a1 + 0.6, x0, size=26),
           tag("Pitch Label", "≈ 3 FOOTBALL PITCHES", [x + s / 2, 560], a1 + 2.0, x0, size=12),
           tag("Yield Label", "≈ 700 KG GREEN A YEAR", [x + s / 2, 1000], a1 + 3.6, b0 + 3.0, size=12),
           src("Src USDA", "SOURCE: USDA FAS MX2026-0026 (≈ 0.36 T/HA)", a1 + 3.4, b0 + 3.0),
           shape("Plot", [G("P", path([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], True), trim(0, A(K(a1, 0), K(a1 + 0.8, 100))), stroke(MX, 4))], [0, 0], a1, x0)]
    for j in range(3):
        col.append(shape(f"Pitch {j + 1}", [G("P", rect([72, 46]), stroke(GREY, 2))], [x + 40 + 80 * j, 510], a1 + 1.6 + j * 0.2, x0, scale=grow(a1 + 1.6 + j * 0.2)))
    for j in range(12):
        t = a1 + 2.6 + j * 0.08
        col.append(sack(f"Sack {j + 1}", [x + 20 + (j % 6) * 40, 960 - (j // 6) * 52], t, b0 + 3.0, col=SEED, s=70, scale=grow(t, 70)))
    bh = A(K(b0 + 3.0, [100, 0]), K(b0 + 3.4, [100, 100]), K(m2, [100, 100]), K(m2 + 1.4, [100, 790]))
    col += [shape("Value Bar", [G("B", rect([120, 38], [0, -19]), fill(MX))], [x + s / 2, 980], b0 + 3.0, x0, scale=bh),
            tag("Value Low", "≈ $770", [x + s / 2 + 80, 960], b0 + 3.4, m2, size=16, just="left"),
            tag("Value High", "≈ $6,100", [x + s / 2 + 80, 690], m2 + 1.4, x0, size=16, just="left"),
            tag("Before", "AT THE NEW YORK PRICE, BEFORE ANY DEDUCTIONS", [1210, 1010], m2 + 2.0, x0, size=12),
            src("Src ICO", "SOURCE: ICE; ICO", b0, x0)]
    for l in col:
        add_out(l, min(l["out"], x0))
    L += col
    L.append(disc("Corner", A(K(0, list(C)), K(a1, [x, y])), 24, MX, 0, x0, sh=0))
    # B: the chart, framed on 1990-2026
    lx, ly = PTS[[p[0] for p in PRICE].index(LOW01[0])]
    fx, fy = PTS[[p[0] for p in PRICE].index(FEB25[0])]
    L.append(tag("Low", "< 50¢ / LB", [lx, ly + 50], m1, D, size=14, parent=rg))
    L.append(shape("Low Ring", [G("R", ell([20, 20]), stroke(INK, 3))], [lx, ly], m1 - 0.2, D, parent=rg, scale=grow(m1 - 0.2)))
    L.append(tag("Feb25", "≈ $4 / LB (MONTHLY AVERAGE)", [fx - 20, fy + 6], m2 + 1.0, D, size=14, just="right", parent=rg))
    L.append(shape("Feb Ring", [G("R", ell([20, 20]), stroke(INK, 3))], [fx, fy], m2 + 0.8, D, parent=rg, scale=grow(m2 + 0.8)))
    L += chart(b0, D, rg, start=frac(1990), end=A(K(b0, frac(1990)), K(m1, frac(2001.5)), K(m2 - 2.0, frac(2001.5)), K(m2 + 0.8, 100)), axis_start=ax_frac(1990),
               decades_t=1e9)
    L = [l for l in L if not (l["in"] > 1e8)]
    L.append(chart_rig(D, [(0, S5_P, S5_S)]))
    return finish(L, D)


# =====================================================================
# SCENE 6 - A TREATY THAT CAME AND WENT (32 s)
# =====================================================================
ICA = [("INTERNATIONAL COFFEE", 20, LAB), ("AGREEMENT, 1962", 20, LAB), ("", 10, BODY), ("Members shall operate a system", 16, BODY),
       ("of export quotas", 16, BODY), ("to keep prices stable.", 16, BODY)]


def s6_treaty(D):
    L = []
    rg = "Chart Rig"
    s1, a0, b0, q1, c0, d0 = 3.0, 3.6, 9.5, 11.0, 17.0, 23.0
    L += doc("ICA", ICA, [430, 420], (440, 360), a0, b0, hl_line=4, credit="INTERNATIONAL COFFEE AGREEMENT, 1962, RECREATED")
    for l in L:
        p = l["transform"]["position"]
        if isinstance(p, list) and not l["name"].endswith("Credit"):
            l["transform"]["position"] = A(K(a0, [p[0] - 700, p[1]]), K(a0 + 0.6, p), K(b0 - 0.6, p), K(b0, [p[0] - 800, p[1]]))
    L.append(tag("Quotas", "QUOTAS IN FORCE", [yx(1967), py(85)], b0 + 1.0, D, size=14, parent=rg))
    # quota bar on the right edge
    qb = [("BRAZIL, THE LARGEST", 0.32, GREY), ("MEXICO", 0.06, MX), ("EVERYONE ELSE", 0.62, GREY2)]
    y = 800
    for j, (nm, f, col) in enumerate(qb):
        h = 460 * f
        L.append(caps(f"Quota {j + 1} Label", nm, [1800, y - h / 2 + 5], q1 + 0.6, c0, size=11, color=MX if col == MX else INK, just="right"))
        y -= h
    y = 800
    for j, (nm, f, col) in enumerate(qb):
        h = 460 * f
        L.append(shape(f"Quota {j + 1}", [G("Q", rect([50, h], [0, -h / 2]), stroke(INK, 2), fill(col))], [1840, y], q1, c0,
                       position=A(K(q1, [2100, y]), K(q1 + 0.6, [1840, y]), K(13.0, [1840, y]), K(14.0, [1840, 800 - (800 - y) * 0.8]),
                                  K(c0 - 0.6, [1840, 800 - (800 - y) * 0.8]), K(c0, [2100, 800 - (800 - y) * 0.8])),
                       scale=A(K(13.0, [100, 100]), K(14.0, [100, 80]))))
        y -= h
    # C: the two suspensions
    for j, (a, b, s) in enumerate(((1972.9, 1980.8, "DEC 1972 – OCT 1980"), (1986.1, 1987.8, "FEB 1986 – OCT 1987"))):
        L.append(caps(f"Gap {j + 1}", s, [(yx(a) + yx(b)) / 2, 885 + 26 * j], c0 + 0.6 + j * 1.2, D, size=12, color=INK, parent=rg))
    L.append(snowflake("Frost", [yx(1975.5), 300], c0 + 2.6, D))
    L[-1]["parent"] = rg
    L.append(sun("Drought", [yx(1985.6), 300], c0 + 3.4, D))
    L[-1]["parent"] = rg
    L.append(src("Src Bates", "SOURCE: ICO; BATES, OPEN-ECONOMY POLITICS (1997)", c0 + 0.6, D))
    L.append(tag("Came Back", "CAME BACK", [yx(1988.6), py(160)], d0 + 1.0, D, size=14, parent=rg))
    L.append(marker("Came Back Swipe", yx(1988.6) - tw("CAME BACK", 14, LAB, 140) / 2 - 8, py(160), tw("CAME BACK", 14, LAB, 140) + 16, d0 + 1.6, D, size=14, parent=rg))
    bd = bands(b0, D, rg, cut=c0)
    for j, l in enumerate(bd):
        t = b0 + 0.4 * j if j not in GAPS else b0 + 0.4 * j
        l["in"] = t
        if j in (2, 4):  # redraws after each gap
            l["in"] = c0 + 1.0 + (j - 2) * 2.0
        l["transform"]["scale"] = A(K(l["in"], [0, 100]), K(l["in"] + 0.6, [100, 100]))
        l["transform"]["anchorPoint"] = [yx(BANDS[j][0]), 0]
        l["transform"]["position"] = [yx(BANDS[j][0]), 0]
    L += chart(0, D, rg, start=A(K(0.4, frac(1990)), K(s1, 0)), axis_start=A(K(0.4, ax_frac(1990)), K(s1, 0)), decades_t=s1 - 0.6)
    L += bd
    L.append(chart_rig(D, [(0.4, S5_P, S5_S), (s1, (0, 0), 1)]))
    return finish(L, D)


# =====================================================================
# SCENE 7 - 4 JULY 1989 (23 s)
# =====================================================================
P89 = (yx(1989), py(85))
Z7 = 2.5
RING_SCREEN = (CX, 400)


def s7_crash(D):
    L = []
    rg = "Chart Rig"
    a0, s0, b0, p0 = 0.6, 2.8, 7.0, 17.0
    L += wipe_text("Date Chip", "4 JULY 1989", [yx(1989), 330], 32, INK, a0, p0, parent=rg)
    L.append(shape("Date Tick", [G("T", path([(yx(1989), 350), (yx(1989), P89[1] - 14)]), stroke(INK, 2, dashes=(6, 6)))], [0, 0], a0, p0, parent=rg))
    # the quota bar spills and goes
    for j, (f, col) in enumerate(((0.32, GREY), (0.06, MX), (0.62, GREY2))):
        h = 368 * f
        y0 = 800 - 368 * sum(x for x, _ in ((0.32, 0), (0.06, 0), (0.62, 0))[:j])
        L.append(shape(f"Quota {j + 1}", [G("Q", rect([50, h], [0, -h / 2]), stroke(INK, 2), fill(col))], [1840, y0], s0, s0 + 3.0,
                       position=A(K(s0, [2100, y0]), K(s0 + 0.6, [1840, y0]), K(s0 + 1.4, [1840 + (j - 1) * 60, y0]), K(s0 + 2.6, [1840 + (j - 1) * 120, 1300])),
                       rotation=A(K(s0 + 1.4, 0), K(s0 + 2.6, (j - 1) * 50 + 20))))
    # B: two five-year averages
    for j, (a, b, p, s) in enumerate(((1984.5, 1989.5, 134, "≈ $1.34"), (1989.5, 1994.5, 77, "≈ 77¢"))):
        t = b0 + 1.0 + j * 1.6
        L.append(tag(f"Avg {j + 1} Label", s, [(yx(a) + yx(b)) / 2, py(p) - 18], t + 0.4, p0, size=16, parent=rg))
        L.append(shape(f"Avg {j + 1}", [G("A", rect([yx(b) - yx(a), 8], [(yx(b) - yx(a)) / 2, 0]), fill(INK))], [yx(a), py(p)], t, p0,
                       scale=A(K(t, [0, 100]), K(t + 0.5, [100, 100])), parent=rg))
    L.append(src("Src ICO Avg", "SOURCE: ICO INDICATOR PRICE, FIVE-YEAR AVERAGES", b0 + 1.0, p0))
    L.append(tag("Never", "NO CORRIDOR CAME BACK", [yx(2000), py(250)], b0 + 4.6, p0, size=14, parent=rg))
    for l in L:
        add_out(l, min(l["out"], p0))
    L.append(shape("Ring", [G("R", ell([40 / Z7, 40 / Z7]), stroke(INK, 4 / Z7))], list(P89), p0, D, parent=rg, scale=grow(p0)))
    L += chart(0, D, rg)
    L += bands(0, D, rg, cut=-1, drop=a0 + 0.4)
    L = [l for l in L if l["out"] > l["in"]]
    L.append(chart_rig(D))
    return finish(L, D, [(0, C, C, 1), (p0 + 0.6, C, C, 1), (D - 0.4, P89, RING_SCREEN, Z7)])


# =====================================================================
# SCENE 8 - MEXICO LOSES ITS BUYER (28 s)
# =====================================================================
TL_Y = 400            # content y of the timeline; the camera drops it to y = 900 on screen
TL_K = 24.5


def tlx(year):
    return CX + (year - 1989) * TL_K


def s8_inmecafe(D):
    L = []
    pan_t, b0, c0, d0, z0 = 2.0, 4.0, 12.0, 18.0, 22.0
    rnd = random.Random(58)
    DY = 500
    L.append(caps("Timeline Title", "INMECAFE (INSTITUTO MEXICANO DEL CAFÉ)", [tlx(1958), TL_Y - 40], 0.6, d0, size=14, color=INK, just="left"))
    for y in (1958, 1970, 1980, 1993):
        L.append(caps(f"TL {y}", str(y), [tlx(y), TL_Y + 34], 0.4, d0, size=12, color=INK))
    L.append(caps("TL 1989", "1989", [tlx(1989), TL_Y + 50], 0.4, d0, size=14, color=INK))
    L.append(tag("Founded", "FOUNDED", [tlx(1958), TL_Y - 72], 1.0, d0, size=13, just="left"))
    L.append(tag("Liquidated", "LIQUIDATED 1993", [tlx(1993) + 20, TL_Y - 72], c0 + 5.0, d0, size=13, just="left"))
    L.append(shape("Timeline", [G("T", path([(tlx(1958), TL_Y), (tlx(1993), TL_Y)]), stroke(INK, 3)),
                                G("Ticks", *[path([(tlx(y), TL_Y - 8), (tlx(y), TL_Y + 8)]) for y in (1958, 1970, 1980, 1993)], stroke(INK, 3))], [0, 0], 0, d0))
    L.append(shape("Ring 89", [G("R", ell([40, 40]), stroke(INK, 4))], [tlx(1989), TL_Y], 0, d0))
    # B: the map and the buying centres
    cy0 = -DY
    off = lambda p: [p[0], p[1] + cy0]
    dots = []
    for s, n in (("Chiapas", 8), ("Veracruz", 7), ("Oaxaca", 6), ("Puebla", 3)):
        dots += state_points(s, n, rnd)
    rnd.shuffle(dots)
    for j, ll in enumerate(dots):
        t = b0 + 0.6 + j * 0.1
        gone = c0 + j * 0.2 if j < len(dots) - 1 else c0 + 5.0
        L.append(disc(f"Centre {j + 1}", off(mpt(ll)), 12, INK, t, gone, sh=0, scale=grow(t, 100, 0.2)))
    L.append(tag("Bought", "≈ 44 % OF THE CROP BOUGHT, 1982–83", [1500, 940 + cy0], b0 + 2.4, d0, size=13))
    L.append(shape("Crop Fill", [G("F", rect([60, 400 * 0.44], [0, -200 * 0.44]), fill(INK))], [1500, 880 + cy0], b0 + 2.0, d0,
                   scale=A(K(b0 + 2.0, [100, 0]), K(b0 + 2.8, [100, 100]))))
    L.append(shape("Crop Outline", [G("O", rect([60, 400], [0, -200]), stroke(INK, 2))], [1500, 880 + cy0], b0 + 1.8, d0))
    L.append(src("Src UAM", "SOURCE: UAM, SOCIOLÓGICA; LIMINAR (CESMECA)", b0 + 2.0, d0))
    for l in L:
        add_out(l, min(l["out"], d0 + 0.4))
    # D: coyotes and the C price are what is left; find UCIRI
    for j, ll in enumerate(((-93.0, 16.5), (-96.6, 17.1), (-96.8, 19.6))):
        L.append(truck(f"Coyote {j + 1}", off(mpt(ll)), d0 + 0.4 + j * 0.3, D, s=22, scale=grow(d0 + 0.4 + j * 0.3, 22)))
    L.append(shape("C Line", [G("L", path([(260 + 70 * j, cy0 + 40 + (24 if j % 2 else 0) - j * 3) for j in range(14)]),
                                trim(0, A(K(d0 + 0.6, 0), K(d0 + 2.0, 100))), stroke(INK, 3))], [0, 0], d0 + 0.6, z0))
    L.append(caps("C Line Label", 'C PRICE', [1260, cy0 + 30], d0 + 1.6, z0, size=13, color=INK, just="left"))
    u = off(mpt(UCIRI))
    L.append(disc("UCIRI", u, 24 / 4, MX, d0 + 2.6, D, sh=0, scale=A(K(d0 + 2.6, [0, 0]), K(d0 + 3.0, [400, 400]), K(z0, [400, 400]), K(D - 0.4, [100, 100]))))
    L += mexico("Mexico", b0, D)
    for l in L[-1:]:
        l["transform"]["position"] = [0, cy0]
    return finish(L, D, [(0, C, C, 1), (0.6, C, C, 1), (pan_t, (CX, TL_Y), (CX, 900), 1), (z0, (CX, TL_Y), (CX, 900), 1), (D - 0.4, u, C, 4)])


# =====================================================================
# SCENE 9 - A FLOOR FROM OAXACA (41 s)
# =====================================================================
NL = (4.9, 52.4)
FLOOR = 180
DOT9 = (yx(1962), py(FLOOR))


def s9_floor(D):
    L = []
    z1, b0, c0, d0, r0 = 2.0, 9.5, 20.0, 31.0, 38.0
    u = mpt(UCIRI)
    nl = mpt(NL)
    Z_W = 0.3
    hl = [tag("UCIRI Label", "UCIRI", [CX, CY + 70], 0.4, z1 - 0.2, size=22, parent="Hold"),
          tag("UCIRI Sub", "A COOPERATIVE OF INDIGENOUS GROWERS", [CX, CY + 104], 0.8, z1 - 0.2, size=13, parent="Hold"),
          tag("Pack Date", "15 NOV 1988: FIRST FAIR-TRADE LABEL", [CX, 960], b0 + 1.4, c0, size=18, parent="Hold"),
          src("Src Havelaar", "SOURCE: STICHTING MAX HAVELAAR; SOLIDARIDAD", b0 + 1.0, c0)]
    hl[-1]["parent"] = "Hold"
    pack = doc("Pack", [("KOFFIE", 30, HEAD), ("MEXICO", 16, LAB), ("", 10, BODY), ("Coöperatie UCIRI, Oaxaca", 15, BODY),
                        ("eerlijke prijs", 15, SCI), ("250 g", 15, BODY)], [1380, 480], (340, 420), b0, c0)
    for l in pack:
        l["parent"] = "Hold"
        p = l["transform"]["position"]
        l["transform"]["position"] = A(K(b0, [p[0] + 700, p[1]]), K(b0 + 0.7, p))
    hl += pack
    for l in hl:
        add_out(l, min(l["out"], c0))
    L += hl
    # A: the map zooms out and an arc crosses the Atlantic
    mid = ((u[0] + nl[0]) / 2, (u[1] + nl[1]) / 2 - 500)
    L.append(shape("Atlantic", [G("A", path([u, nl], False, i=[(0, 0), ((mid[0] - nl[0]) * 0.66, (mid[1] - nl[1]) * 0.66)], o=[((mid[0] - u[0]) * 0.66, (mid[1] - u[1]) * 0.66), (0, 0)]),
                                  trim(0, A(K(z1 + 2.6, 0), K(z1 + 4.6, 100))), stroke(INK, 3 / Z_W, dashes=(14 / Z_W, 10 / Z_W)))], [0, 0], z1 + 2.6, c0))
    L.append(disc("NL Dot", list(nl), 24 / Z_W, INK, z1 + 4.6, c0, sh=0, scale=grow(z1 + 4.6)))
    L.append(caps("NL Label", "THE NETHERLANDS", [nl[0], nl[1] - 50 / Z_W], z1 + 4.8, b0, size=14 / Z_W, color=INK))
    L.append(disc("UCIRI Map", list(u), 6, MX, 0, c0, sh=0, scale=A(K(0, [100, 100]), K(z1 + 2.4, [100 / Z_W * 4 / 4 * 1.0, 100 / Z_W]))))
    L[-1]["transform"]["scale"] = A(K(z1, [100, 100]), K(z1 + 2.4, [4 / Z_W * 100 / 4, 4 / Z_W * 100 / 4]))
    L += mexico("Map", 0, c0, world=True)
    mp = [l for l in L if l["out"] <= c0 + 0.01 and l.get("parent") != "Hold"]
    # C: the chart and the floor (on a Chart Rig that ignores the map camera)
    rg = "Chart Rig"
    ch = [tag("Floor Label", "FAIRTRADE MINIMUM, WASHED ARABICA (SINCE 2023)", [yx(1963), py(FLOOR) - 46], c0 + 2.6, r0, size=13, just="left", parent=rg),
          tag("Floor Price", "$1.80 / LB", [yx(1963), py(FLOOR) - 20], c0 + 2.4, r0, size=16, just="left", parent=rg),
          src("Src Fairtrade", "SOURCE: FAIRTRADE INTERNATIONAL", c0 + 2.4, d0)]
    for j, (a, b) in enumerate(((1998.6, 2004.3), (2017.6, 2020.8))):
        seg = [(yx(y), py(p)) for y, p in PRICE if a <= y <= b]
        poly = [(yx(a), py(FLOOR))] + seg + [(yx(b), py(FLOOR))]
        ch.append(shape(f"Shortfall {j + 1}", [G("H", path(poly, True), fill(GREY2))], [0, 0], c0 + 4.0 + j * 0.8, r0, parent=rg))
    ch.append(shape("Floor", [G("F", path([DOT9, (yx(2026), py(FLOOR))]), trim(0, A(K(c0 + 0.8, 0), K(c0 + 2.4, 100))), stroke(INK, 3, dashes=(14, 10)))],
                    [0, 0], c0 + 0.8, D, parent=rg))
    # D: 100 sacks of the world's coffee
    st = [tag("Strip Label", "≈ 2 IN 100 SOLD ON FAIRTRADE TERMS (2023)", [CX, 925], d0 + 1.4, r0, size=14, parent=rg),
          src("Src FT Impact", "SOURCE: FAIRTRADE COFFEE IMPACT 2025 (202,979 T); FAO (≈ 11 M T)", d0 + 0.6, r0)]
    for j in range(100):
        t = d0 + 0.2 + j * 0.01
        x = 210 + j * 15.2
        ft = j in (40, 71)
        st.append(shape(f"Bag {j + 1}", [G("B", rect([11, 16], None, 2), stroke(INK, 1.5, dashes=(3, 2)) if ft else fill(GREY2))], [x, 975], t, r0, parent=rg,
                        scale=grow(t, 100, 0.2)))
    ch += st
    for l in ch:
        add_out(l, min(l["out"], r0))
        if l.get("parent") is None:
            l["parent"] = rg
    L += ch
    L += [l for l in chart(c0, r0 + 0.4, rg)]
    L.append(disc("Floor Dot", list(DOT9), 24, MX, c0, D, sh=0, parent=rg, scale=grow(c0, 100, 0.3)))
    for l in L:
        if l["name"] in ("Price Line", "Grid", "Time Axis") or l["name"].startswith(("Grid ", "Year ", "Unit")):
            l["out"] = r0
    L.append(null(rg, [0, 0], 0, D, anchor=[0, 0], position=A(K(r0, [0, 0]), K(D - 0.6, [CX - DOT9[0], SLIVER[1] - DOT9[1]]))))
    L[-1]["parent"] = "Hold"
    for l in mp:
        pass
    parent_all([l for l in L if l.get("parent") is None], "Cam")
    q_w = ((u[0] + nl[0]) / 2, (u[1] + nl[1]) / 2)
    return L + [cam(D, [(0, u, C, 4), (z1, u, C, 4), (z1 + 2.4, q_w, C, Z_W)]), hold(D), bg(D)]


# =====================================================================
# SCENE 10 - CLOSE (22 s)
# =====================================================================
def s10_close(D):
    L = []
    a0, b0, c0, e0 = 0.2, 9.0, 11.0, 15.0
    L += wipe_text("End Title", "Who Gets Paid for Your Coffee", [CX, 975], 64, INK, e0, D)
    L.append(word_marker("End Swipe", "Who Gets Paid for Your Coffee", "Paid", CX, 975, 64, e0 + 0.8, D))
    L.append(tag("Coffee Label", "≈ 15¢ THE COFFEE", [CX + 180, SLIVER[1] - 4], 1.4, b0, size=16, just="left"))
    L.append(tag("Farmer Label", "≈ 8–10¢ THE FARMER", [CX + 180, SLIVER[1] + 24], 2.2, b0, size=16, just="left", color=MX))
    L.append(shape("Farmer", [G("F", rect([24, 14]), fill(MX))], list(SLIVER), 0, c0,
                   position=A(K(a0, list(SLIVER)), K(a0 + 1.2, [CX - 60, SLIVER[1]]), K(c0 - 1.4, [CX - 60, SLIVER[1]]), K(c0 - 0.4, [CX - 60, CY])),
                   scale=A(K(a0, [100, 171]), K(a0 + 1.2, [750, 100]), K(c0 - 0.4, [750, 100]), K(c0, [0, 0]))))
    sl = shape("Sliver", [G("S", rect([300, 24]), fill(INK))], list(SLIVER), 0, c0,
               position=A(K(c0 - 1.4, list(SLIVER)), K(c0 - 0.4, [CX, CY])), scale=A(K(c0 - 0.4, [100, 100]), K(c0, [0, 0])))
    L.append(sl)
    bar = latte_bar(0, b0)
    L += bar
    L.append(cup("Cup", [CX, 620], b0, c0 - 0.6, scale=grow(b0)))
    L.append(coffee_section("End", e0 - 2.0, None, D, "Cherry Rig"))
    L += coffee_cherry("End", c0 - 0.2, D, "Cherry Rig", grow_t=c0 - 0.2, branch_t=c0, detail_t=c0 + 0.3)
    L.append(null("Cherry Rig", [CX, CY], 0, D, scale=[140, 140], position=[CX, 520]))
    return finish(L, D)


SCENES = [("S1_Ticker", 20.0, s1_ticker), ("S2_Grams", 24.0, s2_grams), ("S3_Exchange", 23.0, s3_exchange), ("S4_Chain", 44.0, s4_chain),
          ("S5_Swing", 25.0, s5_swing), ("S6_Treaty", 32.0, s6_treaty), ("S7_Crash", 23.0, s7_crash), ("S8_Inmecafe", 28.0, s8_inmecafe),
          ("S9_Floor", 41.0, s9_floor), ("S10_Close", 22.0, s10_close)]

if __name__ == "__main__":
    write(SCENES, "Who_Gets_Paid", "09_who_gets_paid", beats=True)
