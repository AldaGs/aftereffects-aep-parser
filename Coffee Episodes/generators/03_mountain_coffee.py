"""Generator for episode 3, "Why Mountain Coffee Tastes Different" (scripts/03_mountain_coffee_script.md).

    python "Coffee Episodes/generators/03_mountain_coffee.py"      # writes ../json/03_mountain_coffee.json

One mountain (base coordinates, 0.4 px per metre) serves S1/S9 (zoomed Z about the 1,200 m point Q), S2 and S8.
The shared altitude scale (S2, S6, S7, S8) sits at x = SCALE_X; in S6/S7 it rides a rig that cancels the master
push-in so its ticks land on the same pixels across cuts. No fades: cut_pass turns every exit into a cut or a pop.

Follows episode 1's rules: 24 fps, every in/out animation a whole number of 12-frame beats (write(..., beats=True)),
and its drawn vectors: the coffee cherry and its cross-section (S3, S4; the push into the seed turns the camera
upright), the section's seed shape for the big seeds, coffee-shrub icons, and egg-shaped calendar cherries.
"""
import math, random

from coffee_common import *  # noqa: F401,F403
from coffee_families import _rot

ICE, SAGE = "#A7CFEA", "#8FA88A"
BASE_Y, PPM, SCALE_X = 960, 0.4, 300
X0, PEAK = 380, (1000, 120)            # left foot and peak of the mountain
Z = 3.0                                # S1/S9 hillside zoom
COATEPEC, SOCONUSCO = (-96.96, 19.45), (-92.20, 15.15)
P78, MK = (1300, 480), 150             # S7 -> S8 Coatepec dot on screen, map px per degree


def ay(m):
    return BASE_Y - m * PPM


def fx(m):
    """x of the mountain's left flank at altitude m."""
    return X0 + (PEAK[0] - X0) * m / 2100


Q = (fx(1200), ay(1200))               # (734, 480)


def blend(c0, c1, u):
    a, b = [int(c0[i:i + 2], 16) for i in (1, 3, 5)], [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * u):02X}" for x, y in zip(a, b))


def hold_rig(name, D):
    """Null that cancels the master push-in (linear 100 -> HS*100 over the scene)."""
    return null(name, [CX, CY], 0, D, scale=X(f"var k = 100 / (1 + {HS - 1:.3f} * time / {D}); [k, k]"))


# ---------------------------------------------------------------------
# art
# ---------------------------------------------------------------------
# a coffee bush in a hillside row: a lumpy dome, leaf tips poking out, on a short stem (about 20 x 16 px)
MINI_BUSH = smooth([(-11, -4), (-12, -9), (-8, -14), (-3, -13), (0, -18), (4, -14), (9, -15), (12, -9), (10, -4), (0, -3)], True, corners=(0, 8))


def mountain(prefix, t0, t1, rig, dx=0, right=1700, draw=None, shrubs=True, col=LINE, lw=3):
    """Outline mountain plus a row of Mexico-green shrubs along the left flank (900-1,600 m)."""
    out = []
    if shrubs:
        gs = []
        for k, m in enumerate(range(900, 1650, 50)):
            x, y = fx(m) + dx, ay(m)
            gs.append(G(f"Shrub {k + 1}", G("Bush", MINI_BUSH, fill(MX)), G("Stem", path([(0, 0), (0, -5)]), stroke(STEM, 2)),
                        tr={"position": [x, y]}))
        out.append(shape(f"{prefix} Shrubs", gs, [0, 0], t0, t1, parent=rig))
    tr = [trim(0, A(K(draw, 0), K(draw + 1.4, 100)))] if draw is not None else []
    out.append(shape(f"{prefix} Mountain", [G("M", path([(X0 + dx, BASE_Y), (PEAK[0] + dx, PEAK[1]), (right + dx, BASE_Y)]), *tr, stroke(col, lw))],
                     [0, 0], t0, t1, parent=rig))
    return out


def grade_line(name, t0, t1, rig, lw=2, x0=SCALE_X, x1=1500):
    return shape(name, [G("Dash", path([(x0, Q[1]), (x1, Q[1])]), stroke(INK, lw, cap="butt", dashes=(7, 5)))], [x0, 0], t0, t1, parent=rig,
                 anchorPoint=[x0, 0], scale=A(K(t0, [0, 100]), K(t0 + 1.0, [100, 100])))


def alt_scale(prefix, t, t1, rig=None):
    out = [shape(f"{prefix}Scale Axis", [G("A", path([(SCALE_X, BASE_Y), (SCALE_X, ay(2000))]), trim(0, A(K(t, 0), K(t + 0.8, 100))), stroke(INK, 3))],
                 [0, 0], t, t1)]
    out.append(shape(f"{prefix}Scale Ticks", [G("T", *[path([(SCALE_X - 8, ay(m)), (SCALE_X, ay(m))]) for m in range(0, 2001, 200)], stroke(INK, 3))],
                     [0, 0], t + 0.4, t1))
    for m in range(0, 2001, 400):
        out.append(caps(f"{prefix}Scale {m}", f"{m:,}", [SCALE_X - 16, ay(m) + 6], t + 0.4, t1, size=14, color=INK, just="right"))
    out.append(caps(f"{prefix}Scale Title", "ALTITUDE, M", [SCALE_X - 16, ay(2000) - 36], t + 0.4, t1, size=14, just="left"))
    if rig:
        parent_all(out, rig)
    return out


def thermo(name, pos, t0, t1, col=None, level=None, **tr):
    """Small thermometer standing on pos: tube, ice column, 30 px bulb."""
    col = col if col is not None else ICE
    lv = level if level is not None else [100, 100]
    items = [G("Column", rect([8, 60], [0, -30]), fill(col), tr={"anchorPoint": [0, 0], "position": [0, -20], "scale": lv}),
             G("Bulb", ell([30, 30], [0, -15]), stroke(INK, 3), fill(col)),
             G("Tube", rect([18, 80], [0, -60], 9), stroke(INK, 3), fill(WHITE))]
    return shape(name, items, pos, t0, t1, **tr)


def jar(prefix, pos, size, t_fill0, t_fill1, t0, t1, col=ICE, refill=None, **tr):
    """Degree-day jar: outline plus a fill that rises over [t_fill0, t_fill1]. refill: (t0, t1) for a second, empty-again pour."""
    w, h = size
    lv = [KL(t_fill0, [100, 0]), KL(t_fill1, [100, 100])]
    if refill:
        lv += [KS(refill[0] - 0.4, [100, 100]), KL(refill[0], [100, 0]), KL(refill[1], [100, 100])]
    return [shape(f"{prefix} Jar", [G("Glass", rect([w, h], None, 12), stroke(INK, 4)),
                                    G("Fill", rect([w - 12, h - 12], [0, -(h - 12) / 2]), fill(col),
                                      tr={"anchorPoint": [0, 0], "position": [0, (h - 12) / 2], "scale": A(*lv)})],
                  pos, t0, t1, **tr)]


def bracket(name, a, b, t, t1, label=None, side=1, col=INK, size=15, lab_off=None):
    """Bracket between points a and b (vertical if same x, else horizontal), with an optional label."""
    if abs(a[0] - b[0]) < 1:
        p = path([(a[0] - 12 * side, a[1]), a, b, (b[0] - 12 * side, b[1])])
        lp = [a[0] + 16 * side, (a[1] + b[1]) / 2 + 6]
        just = "left" if side > 0 else "right"
    else:
        p = path([(a[0], a[1] + 12 * side), a, b, (b[0], b[1] + 12 * side)])
        lp = [(a[0] + b[0]) / 2, a[1] - 14 * side]
        just = "center"
    out = [shape(name, [G("B", p, trim(0, A(K(t, 0), K(t + 0.5, 100))), stroke(col, 3))], [0, 0], t, t1)]
    if label:
        out.append(caps(name + " Label", label, lab_off or lp, t + 0.3, t1, size=size, color=col, just=just))
    return out


SEED_PTS = [(5, -74), (36, -66), (60, -30), (64, 8), (52, 48), (28, 72), (5, 76)]       # coffee_section's right seed
PARCH_PTS = [(2, -84), (40, -76), (70, -34), (74, 10), (60, 56), (30, 82), (2, 86)]


def seed_path(h, s=1, pts=SEED_PTS):
    k = h / 150
    return smooth([(s * x * k, y * k) for x, y in pts], True, corners=(0, len(pts) - 1))


SEED_H = 500
SEED_K = SEED_H / 150
SEED_O = (CX - 40 * SEED_K, CY)        # where coffee_section's right seed lands after the push-in (camera turned upright)
SEED_A = _rot((40, 0), CH_ROT)           # that seed point in the tilted section


def seed_cells(rnd, h, fill_frac):
    """Hex cells and their food dots inside a D-shaped seed of height h (origin on the flat side)."""
    k = h / 144
    r = 20
    cells, dots = [], []
    x = 6 * k + r * 0.6
    c = 0
    while x < 6 * k + 60 * k:
        y = -h / 2 + (r * 0.9 if c % 2 else 0)
        while y < h / 2:
            hx = [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
            cells.append(path(hx, True))
            dots.append((x, y))
            y += r * math.sqrt(3)
        x += r * 1.5
        c += 1
    rnd.shuffle(dots)
    return cells, dots[:int(len(dots) * fill_frac)]


def seed_layers(prefix, pos, t0, t1, rig, fill_frac, wall, dots_t, zig_t=None, rnd=None):
    """Big seed: matte + honeycomb (cells, dots), body, optional zigzag cut. wall: strokeWidth (number or keyframes)."""
    cells, dots = seed_cells(rnd, SEED_H, fill_frac)
    dg = [G(f"D{j}", ell([12, 12], list(p)), fill(SEED_LINE), tr={"opacity": A(K(dots_t[0] + (dots_t[1] - dots_t[0]) * j / max(1, len(dots)), 0),
                                                                              K(dots_t[0] + (dots_t[1] - dots_t[0]) * j / max(1, len(dots)) + 0.1, 100))})
          for j, p in enumerate(dots)]
    out = []
    if zig_t is not None:
        zz = [(30, -200 + j * 40) for j in range(11)]
        zz = [(x + (10 if j % 2 else -10), y) for j, (x, y) in enumerate(zz)]
        out.append(shape(f"{prefix} Cut", [G("Z", path(zz), trim(0, A(K(zig_t, 0), K(zig_t + 1.2, 100))), stroke(INK, 5))], pos, zig_t, t1, parent=rig))
    elif zig_t is None and fill_frac < 0.5:
        out.append(shape(f"{prefix} Cut", [G("Z", path([(30, -200), (30, 200)]), stroke(INK, 4))], pos, t0, t1, parent=rig))
    out += [shape(f"{prefix} Matte", [G("M", seed_path(SEED_H), fill(WHITE))], pos, t0, t1, parent=rig, enabled=False),
            shape(f"{prefix} Cells", [G("Dots", *dg), G("Cells", *cells, stroke(GREY2, wall))], pos, t0, t1, parent=rig,
                  trackMatte={"target": f"{prefix} Matte", "type": "Alpha"}),
            shape(f"{prefix} Seed", [G("S", seed_path(SEED_H), stroke(SEED_LINE, 6), fill(SEED))], pos, t0, t1, parent=rig)]
    return out


def hat_icon(name, pos, t, t1):
    return shape(name, [G("Hat", path([(-22, 0), (-18, -22), (18, -22), (22, 0)], True), ell([80, 14]), fill(INK))], pos, t, t1, scale=grow(t))


def jacket_icon(name, pos, t, t1):
    p = path([(-30, -30), (-10, -36), (0, -24), (10, -36), (30, -30), (40, 10), (28, 12), (26, -6), (26, 34), (-26, 34), (-26, -6), (-28, 12), (-40, 10)], True)
    return shape(name, [G("Zip", path([(0, -24), (0, 34)]), stroke(WHITE, 3)), G("Jacket", p, fill(INK))], pos, t, t1, scale=grow(t))


def shrub_icon(name, pos, t, t1, col=GREY):
    return shape(name, icon_shrub(col, True), [pos[0], pos[1] - 30], t, t1, scale=grow(t))


def cherry_dot(name, pos, t, t1, size=26, **tr):
    """Calendar cherry: episode 1's egg on a short stalk, size = body width."""
    k = size / CH_W
    return shape(name, [G("Stalk", path([(0, -CH_H * k / 2 + 2), (2, -CH_H * k / 2 - 8)]), stroke(STEM, 3)),
                        G("Skin", egg(CH_W * k, CH_H * k), fill(ARA))], pos, t, t1, rotation=CH_ROT, **tr)


def shade_tree(name, pos, t, t1, **tr):
    """Inga-like shade tree: a wide, flat umbrella crown on a leaning trunk."""
    crown = smooth([(-120, -140), (-100, -176), (-56, -196), (-10, -214), (40, -208), (86, -190), (116, -160), (100, -138), (40, -128), (-40, -126), (-96, -128)],
                   True)
    return shape(name, [G("Crown", crown, fill(SAGE)),
                        G("Branches", path([(-4, -110), (-50, -134)]), path([(-4, -110), (46, -132)]), stroke(STEM, 5)),
                        G("Trunk", path([(0, 0), (-6, -130)]), stroke(STEM, 8))], pos, t, t1, **tr)


def map_layer(name, k, center, o, t0, t1, **tr):
    """Land, state fills and white state borders in one layer (one matte covers it all)."""
    s = lambda ll: screen(ll, k, center, o)
    st = [path([s(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    land = []
    for r in GEO["land"]:
        lo, la = [p[0] for p in r], [p[1] for p in r]
        if max(lo) < -110 or min(lo) > -80 or max(la) < 5 or min(la) > 30:
            continue
        land.append(path([s(p) for p in r], True))
    return shape(name, [G("Borders", *st, stroke(WHITE, 2)), G("Land", *land, fill(LAND))], [0, 0], t0, t1, **tr)


def tag(name, s, pos, t, t1, size=16, color=INK, just="center"):
    return appear(caps(name, s, pos, t, t1, size=size, color=color, just=just), t)


# =====================================================================
# SCENE 1 - THE LINE ON THE HILLSIDE (21 s)
# =====================================================================
def hillside(D, prefix, rig, draw=None):
    out = [grade_line(f"{prefix}Grade Line", 3.6 if draw is not None else 0, D, rig)]
    out += mountain(f"{prefix}Hill", 0, D, rig, draw=draw)
    return out


def s1_line(D):
    L = []
    rig = "Hill Rig"
    tags_out = 16.6
    L.append(caps("Place", "ABOVE COATEPEC, VERACRUZ", [90, 90], 0.6, D, size=18, color=INK, just="left"))
    L.append(tag("Tag Height", "≈ 1,200 M", [1650, 470], 4.6, D, size=18))
    L.append(tag("Tag Above", "ESTRICTAMENTE ALTURA ↑", [1480, 380], 8.0, tags_out, color=MX))
    L.append(tag("Tag Below", "ALTURA ↓", [1480, 600], 9.0, tags_out, color=INK))
    for l in L[-2:]:
        add_out(l, tags_out)
    L += wipe_text("Question", "Why would height set the grade?", [CX, 1000], 44, INK, 17.0, D)
    hl = marker("Line Swipe", 80, inv((0, Q[1]))[1] + 12, 1760, 12.6, D, size=40)
    L += hillside(D, "", rig, draw=0.2)
    L.append(hl)
    L.append(null(rig, list(Q), 0, D, position=inv((CX, Q[1])), scale=[Z / HS * 100] * 2))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - UP THE SLOPE (21 s)
# =====================================================================
BULB_D = 30


def s2_slope(D):
    L = []
    rig = "Hill Rig"
    a1 = 2.6
    d0 = 17.6
    # B: the thermometer walks up the slope, one notch per 200 m
    steps = list(range(0, 1201, 200))
    pos, lv, col = [], [], []
    t = a1 + 1.0
    for j, m in enumerate(steps):
        p = [fx(m) - 26, ay(m)]
        pos += [K(t, p), K(t + 0.5, p)] if j else [K(t, p)]
        lv.append(K(t, [100, 100 - j * 9]))
        col.append(K(t, blend(WHITE, ICE, 0.3 + 0.7 * j / 6)))
        t += 0.7
    th = thermo("Thermo", A(*pos), a1 + 1.0, d0, col=A(*col), level=A(*lv))
    L.append(th)
    L.append(tag("Lapse", "≈ 0.65 °C COOLER PER 100 M", [1240, 300], a1 + 2.4, d0, color=INK))
    # C: two pins, the bracket, a sun hat and a jacket
    c0 = 9.6
    L.append(disc("Port Pin", [X0, BASE_Y], 18, INK, c0, d0, sh=0, scale=grow(c0)))
    L.append(tag("Port Label", "PORT OF VERACRUZ · ≈ 25.5 °C", [X0 + 30, BASE_Y - 24], c0 + 0.2, d0, just="left"))
    L.append(disc("Coatepec Pin", list(Q), 18, MX, c0 + 0.5, D, sh=0, scale=grow(c0 + 0.5)))
    L.append(tag("Coatepec Label", "COATEPEC · ≈ 19 °C", [Q[0] - 40, Q[1] - 20], c0 + 0.7, d0, just="right"))
    L += bracket("Lapse Bracket", (1260, Q[1]), (1260, BASE_Y), c0 + 1.2, d0, "≈ 6 °C", lab_off=[1290, 726])
    L.append(hat_icon("Hat", [1440, 900], c0 + 1.8, d0))
    L.append(jacket_icon("Jacket", [1440, 540], c0 + 2.2, d0))
    L.append(src("Src Slope", "SOURCE: ICAO STANDARD ATMOSPHERE; ERA5 VIA OPEN-METEO, 2015–2024", c0, d0))
    L += alt_scale("", a1, d0)
    for l in L:
        if l["out"] > d0 and l["name"] != "Coatepec Pin":
            add_out(l, d0)
    add_out(L[[l["name"] for l in L].index("Coatepec Pin")], d0)
    # D: the bulb slides to the centre and grows (2->3 handoff)
    bp = [Q[0] - 26, Q[1] - 15]
    L.append(disc("Bulb Out", A(K(d0, bp), K(d0 + 1.6, inv((CX, CY)))), BULB_D, ICE, d0, D, sh=0, line=INK,
                  scale=A(K(d0, [100, 100]), K(d0 + 1.6, [90 / BULB_D / HS * 100] * 2))))
    hill = hillside(D, "", rig)
    for l in hill:
        add_out(l, d0)
    L += hill
    L.append(null(rig, list(Q), 0, D, position=A(K(0, [CX, Q[1]]), K(a1, list(Q))), scale=A(K(0, [Z * 100] * 2), K(a1, [100, 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - THE HEAT BUDGET (26 s)
# =====================================================================
CAL_Y, CAL_X0, PX_MONTH = 960, 360, 100
JAR_FAST, JAR_SLOW = (700, 560), (1220, 560)
CH_D = 90                              # cherry icon on the calendar


def cal_x(m):
    return CAL_X0 + PX_MONTH * m


def s3_heat(D):
    L = []
    b0, fill0 = 5.0, 6.4
    t_fast, t_slow = fill0 + 6.0, fill0 + 11.0
    # A: the bulb sinks into one tall jar
    L.append(disc("Bulb", A(K(0.4, [CX, CY]), K(1.2, [CX, CY + 200])), 90, ICE, 0, b0, sh=0, line=INK,
                  scale=A(K(0.4, [100, 100]), K(1.2, [40, 40]))))
    L += jar("One", [CX, CY], [200, 440], 1.2, 4.4, 0.8, b0, scale=A(K(0.8, [100, 0]), K(1.4, [100, 100])))
    L.append(tag("Budget", "FLOWER → RIPE CHERRY ≈ 2,500 DEGREE-DAYS", [CX, 250], 1.6, b0))
    # B: two jars on a shared calendar
    L.append(tag("Farm", "A COLOMBIAN RESEARCH FARM", [CX, 120], b0, 22.4, color=INK))
    for k, (p, nm, t1f) in enumerate(((JAR_FAST, "1,100 M · 23 °C", t_fast), (JAR_SLOW, "1,900 M · 17 °C", t_slow))):
        pre = ("Fast", "Slow")[k]
        L += jar(pre, list(p), [160, 340], fill0, t1f, b0, t1f + 0.2, scale=A(K(b0, [0, 0]), K(b0 + 0.5, [100, 100])),
                 position=A(K(b0, [CX, CY]), K(b0 + 0.6, list(p))))
        L.append(tag(f"{pre} Label", nm, [p[0], p[1] + 230], b0 + 0.6, 22.4))
        L.append(shrub_icon(f"{pre} Shrub", [p[0] - 120, p[1] + 200], b0 + 0.8, 22.4))
        L.append(disc(f"{pre} Marker", A(KL(fill0, [cal_x(0), CAL_Y]), KL(t1f, [cal_x((t1f - fill0)), CAL_Y])), 18, INK, fill0, t1f + 0.2, sh=0))
    L.append(shape("Calendar", [G("A", path([(cal_x(0), CAL_Y), (cal_x(12), CAL_Y)]), trim(0, A(K(b0, 0), K(b0 + 0.8, 100))), stroke(INK, 3)),
                                G("T", *[path([(cal_x(m), CAL_Y - 8), (cal_x(m), CAL_Y + 8)]) for m in range(13)], stroke(INK, 3))], [0, 0], b0, 22.4))
    L.append(caps("Cal 0", "FLOWER", [cal_x(0), CAL_Y + 40], b0 + 0.4, 22.4, size=14, color=INK))
    L.append(caps("Cal Title", "MONTHS", [cal_x(12), CAL_Y + 40], b0 + 0.4, 22.4, size=14, color=INK))
    for m in (6, 11):
        L.append(caps(f"Cal {m}", str(m), [cal_x(m), CAL_Y + 40], b0 + 0.4, 22.4, size=14, color=INK))
    # C: each jar becomes a cherry on the calendar
    rigs = []
    for pre, t1f, m in (("Fast", t_fast, 6), ("Slow", t_slow, 11)):
        rg = f"{pre} Cherry Rig"
        L += coffee_cherry(f"{pre} Cherry", t1f + 0.2, D, rg, branch_t=t1f + 0.2, detail_t=t1f + 0.2, flutter=False)
        rigs.append((rg, t1f, m))
    L += bracket("Months", (cal_x(6), 780), (cal_x(11), 780), t_slow + 0.6, 22.4, "≈ 5 MONTHS", side=-1, lab_off=[cal_x(8.5), 750])
    L.append(src("Src Heat", "SOURCE: CENICAFÉ", b0, 22.4))
    # D: follow the slow cherry (3->4 handoff: 420 px at centre)
    d0 = 22.6
    for rg, t1f, m in rigs:
        s0 = CH_D / CHERRY_D * 100
        p0 = [cal_x(m), 860]
        if m == 6:
            L.append(null(rg, p0, t1f + 0.2, D, anchor=[CX, CY], scale=A(K(t1f + 0.2, [0, 0]), K(t1f + 0.7, [s0, s0]))))
            for l in L:
                if l["name"].startswith("Fast Cherry ") and l["type"] != "null":
                    add_out(l, d0)
        else:
            L.append(null(rg, A(K(d0, p0), K(D - 0.3, inv((CX, CY)))), t1f + 0.2, D, anchor=[CX, CY],
                          scale=A(K(t1f + 0.2, [0, 0]), K(t1f + 0.7, [s0, s0]), K(d0, [s0, s0]), K(D - 0.3, [420 / CHERRY_D / HS * 100] * 2))))
    for l in L:
        if l["out"] > d0 and "Cherry" not in l["name"]:
            add_out(l, d0)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - INSIDE THE SLOW CHERRY (26 s)
# =====================================================================
def s4_seed(D):
    L = []
    rnd = random.Random(4)
    crig, srig, frig = "Cherry Rig", "Slow Rig", "Fast Rig"
    s0 = 420 / CHERRY_D * 100
    p0, p1 = 1.0, 2.6
    cut_t = p1 + 2.0
    # A/B: open, push into the right seed until it is 500 px tall
    L.append(coffee_section("Cherry", p0, None, cut_t, crig))
    L += coffee_cherry("Cherry", 0, cut_t, crig, branch_t=-1.5, detail_t=-1.0, flutter=False)  # already grown at the cut from S3
    a0 = [CX + SEED_A[0] * s0 / 100, CY + SEED_A[1] * s0 / 100]
    L.append(null(crig, a0, 0, cut_t, anchor=[CX + SEED_A[0], CY + SEED_A[1]], position=A(K(p1, a0), K(cut_t, [CX, CY])),
                  scale=A(K(p0, [s0, s0]), K(p1, [s0, s0]), K(cut_t, [SEED_K * 100] * 2)), rotation=A(K(p1, 0), K(cut_t, -CH_ROT))))
    c0, d0, z0, e0 = 12.0, 15.6, 20.6, 24.0
    so = list(SEED_O)
    sc = SEED_O[0] + 110                     # visual centre of the seed
    L += seed_layers("Slow", so, cut_t, e0, srig, 0.95, A(K(cut_t, 2), K(c0, 7)), (cut_t + 0.6, c0 - 1.0), zig_t=z0 + 0.6, rnd=rnd)
    # the seed's parchment, kept for the first beat after the cut so the section's ring does not vanish
    L.append(shape("Slow Parchment", [G("P", seed_path(SEED_H, pts=PARCH_PTS), stroke("#E6D3AE", 2 * SEED_K), fill("#FFF8EA"))], list(SEED_O),
                   cut_t, cut_t + 1.0, parent=srig))
    L.append(shape("Clock", [G("Hand", path([(0, 0), (0, -26)]), stroke(INK, 4), tr={"rotation": X("time * 240")}),
                             G("Face", ell([70, 70]), stroke(INK, 4), fill(WHITE))], [1560, 200], cut_t + 0.4, c0))
    L.append(leader("Food Leader", (sc + 40, CY - 120), (1300, 360), cut_t + 1.8, c0, col=INK))
    L.append(caps("Food", "FOOD FOR A SEEDLING", [1310, 340], cut_t + 2.0, c0, size=18, color=INK, just="left"))
    L.append(leader("Wall Leader", (sc + 20, CY + 140), (1300, 720), cut_t + 4.0, c0, col=INK))
    L.append(caps("Walls", "CELL WALLS", [1310, 726], cut_t + 4.2, c0, size=18, color=INK, just="left"))
    # C: the fast seed beside it
    fp = [SEED_O[0] + 380, CY]
    L += seed_layers("Fast", fp, c0, z0, frig, 0.4, 2, (c0, c0 + 0.6), rnd=rnd)
    L.append(tag("Slow Tag", "SLOW CHERRY", [sc - 300, 900], c0 + 0.6, d0))
    L.append(tag("Fast Tag", "FAST CHERRY", [sc + 380 - 40, 900], c0 + 0.6, d0))
    # D: both drop into water; the slow seed sinks first
    gl = (CX, 760)
    L.append(shape("Glass", [G("G", path([(-260, -190), (-260, 190), (260, 190), (260, -190)]), stroke(INK, 5))], list(gl), d0, z0,
                   position=A(K(d0, [gl[0], gl[1] + 700]), K(d0 + 0.6, list(gl)))))
    L.append(shape("Water", [G("W", rect([516, 300], [0, 38]), fill(WATER, 55))], list(gl), d0, z0,
                   position=A(K(d0, [gl[0], gl[1] + 700]), K(d0 + 0.6, list(gl)))))
    L.append(tag("Denser", "DENSER", [CX - 110, 520], d0 + 2.6, z0, size=20))
    L.append(src("Src Seed", "SOURCE: CASSAMO ET AL. 2022; AGUILAR RUIZ 1999", d0, e0))
    # E: the slow seed comes back up with its zigzag cut, then lies down (4->5 handoff)
    L.append(tag("Zig", "GRADERS' SIGN OF A HIGH-GROWN BEAN: A CLOSED, ZIGZAG CUT", [CX, 140], z0 + 1.2, e0, size=18))
    L.append(shape("Seed Outline", [G("S", seed_path(SEED_H), stroke(INK, 6))], so, e0, D, parent=srig))
    L.append(null(srig, [sc, CY], cut_t, D, position=A(K(c0, [sc, CY]), K(c0 + 0.6, [sc - 300, CY]), K(d0 + 0.6, [sc - 300, CY]),
                                                      K(d0 + 1.4, [CX - 110, 600]), K(d0 + 2.6, [CX - 110, 880]),
                                                      K(z0, [CX - 110, 880]), K(z0 + 0.8, [CX, CY]), K(e0, [CX, CY]), K(D - 0.4, inv((CX, CY)))),
                  scale=A(K(d0 + 0.6, [100, 100]), K(d0 + 1.4, [28, 28]), K(z0, [28, 28]), K(z0 + 0.8, [100, 100]), K(e0, [100, 100]),
                          K(D - 0.4, [80 / HS, 80 / HS])),
                  rotation=A(K(e0, 0), K(D - 0.4, 90))))
    L.append(null(frig, [sc + 380, CY], c0, z0, position=A(K(d0 + 0.6, [sc + 380, CY]), K(d0 + 1.4, [CX + 110, 600]), K(z0, [CX + 110, 700])),
                  scale=A(K(c0, [0, 0]), K(c0 + 0.5, [100, 100]), K(d0 + 0.6, [100, 100]), K(d0 + 1.4, [28, 28]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - WHAT THE COLD CHANGES (24 s)
# =====================================================================
ISLAND = [(-210, -20), (-160, -120), (-50, -165), (80, -150), (180, -80), (215, 30), (150, 140), (10, 168), (-120, 135), (-195, 70)]
IS_POS, IS_S = (520, 520), 70
CH = dict(x0=900, x1=1700, y0=780, y1=300)


def s5_reunion(D):
    L = []
    rnd = random.Random(5)
    irig = "Island Rig"
    d0, e0 = 19.6, 22.0
    # A: the island and sixteen plots, cold (ice) to warm (ink)
    pts = []
    while len(pts) < 16:
        p = (rnd.uniform(-170, 170), rnd.uniform(-120, 120))
        if (p[0] / 180) ** 2 + (p[1] / 130) ** 2 < 1:
            pts.append(p)
    pts.sort(key=lambda p: math.hypot(p[0] + 20, p[1] + 30))    # the centre is high and cold
    cold = None
    isl = []
    for j, p in enumerate(pts):
        t = 1.4 + j * 0.12
        d = disc(f"Plot {j + 1}", [CX + p[0], CY + p[1]], 26, blend(ICE, INK, j / 15), t, D, sh=0, scale=grow(t), parent=irig)
        if j == 0:
            cold = d
        else:
            isl.append(d)
    isl.append(shape("Island", [G("I", path(ISLAND, True), stroke(INK, 5))], [CX, CY], 0, D, parent=irig))
    L.append(tag("Island Name", "RÉUNION · 16 PLOTS", [IS_POS[0], 290], 1.6, d0))
    # B: the chart
    b0 = 4.6
    x0, x1, y0, y1 = CH["x0"], CH["x1"], CH["y0"], CH["y1"]
    ch = [shape("Axes", [G("A", path([(x0, y1), (x0, y0), (x1, y0)]), trim(0, A(K(b0, 0), K(b0 + 0.8, 100))), stroke(INK, 3))], [0, 0], b0, d0),
          caps("X Title", "MEAN TEMPERATURE WHILE THE SEED FILLS →", [x1, y0 + 40], b0 + 0.4, d0, size=14, color=INK, just="right"),
          shape("Cold End", [G("C", rect([200, 10], [x0 + 100, y0 + 14]), fill(ICE))], [0, 0], b0 + 0.4, d0)]
    ch.append(shape("Acidity", [G("L", path([(x0 + 20, y1 + 60), (x1 - 40, y0 - 120)], False, i=[(0, 0), (-300, -40)], o=[(300, 40), (0, 0)]),
                                  trim(0, A(K(b0 + 1.6, 0), K(b0 + 3.2, 100))), stroke(INK, 6))], [0, 0], b0 + 1.6, d0))
    ch.append(caps("Acidity Label", "ACIDITY", [x0 + 40, y1 + 30], b0 + 1.8, d0, size=16, color=INK, just="left"))
    ch.append(shape("Earthy", [G("L", path([(x0 + 20, y0 - 60), (x1 - 40, y1 + 80)], False, i=[(0, 0), (-200, 160)], o=[(300, 0), (0, 0)]),
                                 trim(0, A(K(b0 + 4.0, 0), K(b0 + 5.6, 100))), stroke(GREY, 6))], [0, 0], b0 + 4.0, d0))
    ch.append(caps("Earthy Label", "EARTHY DEFECTS", [x1 - 40, y1 + 50], b0 + 4.2, d0, size=16, color=GREY, just="right"))
    ch.append(src("Src Chart", "SOURCE: BERTRAND ET AL. 2012, FOOD CHEMISTRY", b0, 13.0))
    # C: total sugar, same
    c0 = 13.0
    for k, (nm, col, x) in enumerate((("COLD PLOTS", ICE, 380), ("WARM PLOTS", INK, 620))):
        ch.append(shape(f"Sugar {k + 1}", [G("B", rect([110, 120], [0, -60]), fill(col))], [x, 960], c0 + 0.4 + k * 0.3, d0,
                        scale=A(K(c0 + 0.4 + k * 0.3, [100, 0]), K(c0 + 0.9 + k * 0.3, [100, 100]))))
        ch.append(caps(f"Sugar Label {k + 1}", nm, [x, 1000], c0 + 0.4, d0, size=14, color=INK))
    ch.append(caps("Sugar Title", "TOTAL SUGAR: SAME", [500, 790], c0 + 0.2, d0, size=18, color=INK))
    ch.append(word_marker("Same Swipe", "TOTAL SUGAR: SAME", "SAME", 500, 790, 18, c0 + 1.4, d0, font=LAB))
    ch.append(src("Src Sugar", "SOURCE: JOËT ET AL. 2010", c0, d0))
    # D: grey everything but the coldest dot
    for l in ch:
        l["out"] = e0
    veil = shape("Veil", [G("V", rect([W + 200, H + 200]), fill(WHITE))], [CX, CY], d0, e0, opacity=75)
    L = [cold, veil] + L + ch + isl
    for l in L:
        if l["out"] > e0 and l["name"] != cold["name"] and l["type"] != "null":
            add_out(l, e0)
    L.append(null(irig, [CX, CY], 0, D, position=A(K(0.4, [CX, CY]), K(1.2, list(IS_POS)))
                  , scale=A(K(0.4, [100, 100]), K(1.2, [IS_S, IS_S]))))
    # the cold dot leaves the island for the foot of the altitude scale (5->6 handoff)
    cp = [IS_POS[0] + pts[0][0] * IS_S / 100, IS_POS[1] + pts[0][1] * IS_S / 100]
    cold.pop("parent")
    cold["transform"]["position"] = A(K(1.2, cp), K(e0, cp), K(D - 0.3, inv((SCALE_X, BASE_Y))))
    cold["transform"]["scale"] = A(K(1.4, [0, 0]), K(1.85, [IS_S, IS_S]), K(e0, [IS_S, IS_S]), K(D - 0.3, [18 / 26 / HS * 100] * 2))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 6 - DENSITY BECOMES A GRADE (24 s)
# =====================================================================
RAILS = [("COSTA RICA", 560, 1200), ("GUATEMALA", 820, 1350), ("COLOMBIA", 1080, None), ("MEXICO", 1340, 1200)]
RAIL_W, LAD_X = 44, 700


def rail(prefix, x, t, t1, rig):
    return shape(f"{prefix} Rail", [G("R", rect([RAIL_W, BASE_Y - ay(2000)], [0, (BASE_Y + ay(2000)) / 2]), stroke(GREY2, 3))], [x, 0], t, t1, parent=rig)


def band(prefix, x, m0, col, t, t1, rig, w=RAIL_W, **tr):
    h = ay(m0) - ay(2000)
    return shape(f"{prefix} Band", [G("B", rect([w, h], [0, -h / 2]), fill(col))], [x, ay(m0)], t, t1, parent=rig,
                 scale=tr.pop("scale", A(K(t, [100, 0]), K(t + 0.5, [100, 100]))), **tr)


def s6_grades(D):
    L = []
    rig = "Scale Rig"
    c0 = 20.4
    # A: the marker climbs the scale and steps onto Costa Rica's rail
    mk = disc("Marker", A(K(0.8, [SCALE_X, BASE_Y]), K(3.0, [SCALE_X, Q[1]]), K(3.6, [560, Q[1]])), 18, ICE, 0, c0, sh=0, line=INK, parent=rig)
    L.append(mk)
    for k, (nm, x, m0) in enumerate(RAILS):
        t = 0.4 + k * 0.15
        r = rail(nm, x, t, D, rig)
        lb = caps(f"{nm} Name", nm, [x, BASE_Y + 40], t, D, size=14, color=MX if nm == "MEXICO" else INK, parent=rig)
        L += [r, lb]
        if nm != "MEXICO":
            for l in (r, lb):
                p = l["transform"]["position"]
                l["transform"]["position"] = A(K(c0, p), K(c0 + 0.8, [p[0] - 1800, p[1]]))
        else:
            for l in (r, lb):
                p = l["transform"]["position"]
                l["transform"]["position"] = A(K(c0, p), K(c0 + 0.8, [LAD_X - x + p[0], p[1]]))
    bands = [band("Costa Rica", 560, 1200, INK, 3.8, D, rig), caps("CR SHB", "SHB ≈ 1,200 M", [560, Q[1] - 20], 4.0, D, size=13, color=INK, parent=rig, just="center")]
    # B: Guatemala; two names; Colombia's sieve; Mexico last
    b0 = 7.4
    bands.append(band("Guatemala", 820, 1350, INK, b0, D, rig))
    bands.append(caps("GT SHB", "SHB ≈ 1,350 M", [820, ay(1350) - 20], b0 + 0.2, D, size=13, color=INK, parent=rig))
    bands.append(text("Names", "STRICTLY HARD BEAN  ·  STRICTLY HIGH GROWN", [CX, 92], 20, INK, b0 + 1.4, D, font=LAB, tracking=100, parent=rig))
    bands.append(caps("One Claim", "TWO NAMES, ONE CLAIM: THIS SEED GREW SLOWLY", [CX, 126], b0 + 2.4, D, size=14, color=INK, parent=rig))
    bands.append(leader("Names Leader", (820, 140), (820, ay(2000) + 10), b0 + 2.4, D, parent=rig))
    sv = shape("Sieve", [G("Holes", *[ell([10, 10], [x, y]) for x in (-20, 0, 20) for y in (-20, 0, 20)], fill(INK)),
                         G("Rim", ell([84, 84]), stroke(INK, 4), fill(WHITE))], [1080, 560], b0 + 4.0, D, parent=rig, scale=grow(b0 + 4.0))
    bands += [sv, caps("Sieve Label", "GRADED BY BEAN SIZE", [1080, 640], b0 + 4.2, D, size=13, color=INK, parent=rig)]
    mx = band("Mexico", 1340, 1200, MX, b0 + 6.8, D, rig)
    for l in bands:
        p = l["transform"]["position"]
        if isinstance(p, dict):
            continue
        l["transform"]["position"] = A(K(c0, p), K(c0 + 0.8, [p[0] - 1800, p[1]]))
    for l in bands:
        l["out"] = min(l["out"], c0 + 0.8)
    L += bands
    mx["transform"]["position"] = A(K(c0, [1340, ay(1200)]), K(c0 + 0.8, [LAD_X, ay(1200)]))
    L.append(mx)
    L.append(src("Src Grades", "SOURCE: ANACAFÉ; ICAFE; FNC", b0, c0))
    add_out(mk, c0)
    L += alt_scale("", 0, D, rig)
    L.append(hold_rig(rig, D))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - MEXICO'S LADDER (26 s)
# =====================================================================
LAD_W = 420
RUNGS = [("BUEN LAVADO", 0, 400), ("PRIMA LAVADO", 400, 800), ("ALTURA", 800, 1200), ("ESTRICTAMENTE ALTURA", 1200, 2000)]


def s7_ladder(D):
    L = []
    rig = "Scale Rig"
    c0, e0 = 17.0, 22.6
    w = LAD_W / RAIL_W * 100
    widen = A(K(0.4, [100, 100]), K(1.4, [w, 100]))
    lad = [rail("Mexico", LAD_X, 0, D, rig), band("Mexico", LAD_X, 1200, MX, 0, D, rig, scale=widen, opacity=A(K(0.4, 100), K(1.4, 30)))]
    h = BASE_Y - ay(2000)
    lad[0]["shapes"][0]["items"][0]["size"] = A(K(0.4, [RAIL_W, h]), K(1.4, [LAD_W, h]))
    for k, (nm, m0, m1) in enumerate(RUNGS):
        t = 1.6 + k * 0.5
        if m0:
            col, lw = (INK, 4) if m0 == 1200 else (GREY2, 3)
            lad.append(shape(f"Rung {m0}", [G("R", path([(-LAD_W / 2, 0), (LAD_W / 2, 0)]), stroke(col, lw))], [LAD_X, ay(m0)], t, D, parent=rig,
                             scale=A(K(t, [0, 100]), K(t + 0.4, [100, 100]))))
        lad.append(caps(f"Rung {nm}", nm, [LAD_X, (ay(m0) + ay(m1)) / 2 + 6], t + 0.2, D, size=16, color=INK, parent=rig))
    lad.append(caps("Top Line", "≈ 1,200 M", [LAD_X + LAD_W / 2 + 20, Q[1] + 6], 4.0, D, size=16, color=INK, just="left", parent=rig))
    lad.append(caps("Washed", "LAVADO = WASHED", [LAD_X, BASE_Y + 44], 6.6, D, size=14, color=INK, parent=rig))
    L += lad
    # B: the manual
    b0 = 8.4
    pg = doc("Manual", [("Tomando Café", 22, HEAD), ("Buen Lavado", 18, BODY), ("Prima Lavado", 18, BODY), ("Altura", 18, BODY),
                        ("Estrictamente Altura", 20, BODY)], (1450, 540), (480, 380), b0, c0, hl_line=4,
             credit="AGUILAR RUIZ, TOMANDO CAFÉ (1999), ONE COMMON SCALE")
    L += pg
    # C: the map wipes in on the right, a leader from the top line to Coatepec (7->8 handoff)
    k7 = MK / HS
    o7 = inv(P78)
    mrig = "Map Matte"
    L.append(disc("Coatepec Dot", o7, 22 / HS, MX, c0 + 0.6, D, sh=0, scale=grow(c0 + 0.6)))
    L.append(leader("Coatepec Leader", (LAD_X + LAD_W / 2, Q[1]), (o7[0] - 16, o7[1]), c0 + 1.0, e0, col=MX, dot=False))
    L.append(caps("Coatepec Name", "COATEPEC", [o7[0], o7[1] - 30], c0 + 0.8, e0, size=16, color=INK))
    L.append(shape(mrig, [G("M", rect([W, H + 400], [W / 2, 0]), fill(WHITE))], [1000, CY], c0, D, enabled=False,
                   position=A(K(e0, [1000, CY]), K(e0 + 1.0, [-200, CY]))))
    L.append(map_layer("Map", k7, COATEPEC, o7, c0, D, trackMatte={"target": mrig, "type": "Alpha"}))
    for l in lad:
        p = l["transform"]["position"]
        if not isinstance(p, dict):
            l["transform"]["position"] = A(K(e0, p), K(e0 + 1.0, [p[0] - 1400, p[1]]))
        l["out"] = e0 + 1.0
    L += alt_scale("", 0, e0 + 1.0, rig)
    for l in L:
        if "Scale" in l["name"] and l["name"] != rig:
            p = l["transform"]["position"]
            l["transform"]["position"] = A(K(e0, p), K(e0 + 1.0, [p[0] - 1400, p[1]]))
    L.append(hold_rig(rig, D))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - SAME RUNG, DIFFERENT COLD (42 s, the turn)
# =====================================================================
DX_CHI = 770                            # the Chiapas mountain is the same mountain, shifted right
SOC = (fx(1200) + DX_CHI, Q[1])         # (1504, 480)
SOC19 = (fx(1400) + DX_CHI, ay(1400))   # (1563, 400)
DAY_X0, PX_DAY, DAY_Y = 700, 900 / 270, 1040


def dx_(days):
    return DAY_X0 + PX_DAY * days


def s8_same(D):
    L = []
    hrig, crig = "Hill Rig", "Chiapas Rig"
    b0, c0, d0, e0 = 7.0, 16.0, 26.0, 37.0
    # A: pull out from Coatepec until the Soconusco enters
    co_a = (700, 380)
    k1 = 70
    so_a = screen(SOCONUSCO, k1, COATEPEC, co_a)
    mp = map_layer("Map", MK, COATEPEC, P78, 0, b0, anchorPoint=list(P78),
                   position=A(K(0.6, list(P78)), K(4.0, list(co_a))), scale=A(K(0.6, [100, 100]), K(4.0, [k1 / MK * 100] * 2)))
    dots = [disc("Coatepec Dot", A(K(0.6, list(P78)), K(4.0, list(co_a)), K(b0, list(co_a)), K(b0 + 1.0, list(Q))), 22, MX, 0, e0, sh=0),
            disc("Soconusco Dot", A(K(4.0, so_a), K(b0, so_a), K(b0 + 1.0, list(SOC))), 22, MX, 4.0, d0, sh=0, scale=grow(4.0))]
    tags = [tag("Coatepec Tag", "COATEPEC, VERACRUZ · 1,200 M · ESTRICTAMENTE ALTURA", [co_a[0] + 24, co_a[1] - 24], 4.4, b0, size=14, just="left"),
            tag("Soconusco Tag", "SOCONUSCO, CHIAPAS · 1,200 M · ESTRICTAMENTE ALTURA", [so_a[0] + 24, so_a[1] + 40], 4.6, b0, size=14, just="left")]
    for l in tags:
        add_out(l, b0)
    # B: two profiles on one scale, thermometers, the 19 °C isotherm
    L += dots + tags
    th = [thermo("Coatepec Thermo", [Q[0] - 26, Q[1]], b0 + 1.6, e0, scale=grow(b0 + 1.6)),
          thermo("Soconusco Thermo", [SOC[0] - 26, SOC[1]], b0 + 1.8, d0, col=blend(ICE, INK, 0.25), scale=grow(b0 + 1.8))]
    L += th
    L.append(tag("Coatepec Temp", "COATEPEC ≈ 19 °C", [Q[0] - 50, Q[1] - 60], b0 + 2.0, e0, just="right"))
    L.append(tag("Soconusco Temp", "SOCONUSCO ≈ 20 °C", [SOC[0] - 50, SOC[1] - 60], b0 + 2.2, d0, just="right"))
    L.append(caps("Veracruz Name", "VERACRUZ", [PEAK[0], BASE_Y + 40], b0 + 1.0, e0, size=16, color=INK))
    L.append(caps("Chiapas Name", "CHIAPAS", [PEAK[0] + DX_CHI, BASE_Y + 40], b0 + 1.0, d0, size=16, color=INK, parent=crig))
    iso_t = b0 + 3.4
    L.append(shape("Iso Bend", [G("I", path([(1100, Q[1]), SOC19], False, i=[(0, 0), (-200, 0)], o=[(200, 0), (0, 0)]),
                                  trim(0, A(K(iso_t + 1.0, 0), K(iso_t + 2.0, 100))), stroke(ICE, 6))], [0, 0], iso_t + 1.0, d0, parent=crig))
    L += bracket("Iso Bracket", (1640, SOC19[1]), (1640, Q[1]), iso_t + 2.2, d0, "≈ 200 M")
    for l in L[-2:]:
        l["parent"] = crig
    L.append(tag("Iso Label", "19 °C", [SCALE_X + 60, Q[1] - 16], iso_t + 0.2, e0, color=INK, just="left"))
    L.append(src("Src ERA5", "SOURCE: ERA5 VIA OPEN-METEO, 2015–2024", b0 + 2.0, d0))
    # C: two heat jars and a shared calendar
    jf = 16.6
    t_chi, t_coa = jf + 238 / 36, jf + 256 / 36
    L += jar("Chiapas", [SOC[0], 780], [70, 170], jf, t_chi, c0, d0, scale=grow(c0), parent=crig)
    L += jar("Coatepec", [Q[0], 780], [70, 170], jf, t_coa, c0, e0, scale=grow(c0), refill=(d0 + 1.8, d0 + 1.8 + 286 / 36))
    cal = [shape("Days", [G("A", path([(dx_(0), DAY_Y), (dx_(290), DAY_Y)]), trim(0, A(K(c0, 0), K(c0 + 0.8, 100))), stroke(INK, 3))], [0, 0], c0, e0),
           caps("Days Label", "DAYS FROM 1 APRIL →", [dx_(0) - 20, DAY_Y + 6], c0 + 0.2, e0, size=13, color=INK, just="right")]
    cal.append(disc("Chi Marker", A(KL(jf, [dx_(0), DAY_Y]), KL(t_chi, [dx_(238), DAY_Y])), 16, INK, jf, d0, sh=0, parent=crig))
    cal.append(disc("Coa Marker", A(KL(jf, [dx_(0), DAY_Y]), KL(t_coa, [dx_(256), DAY_Y])), 16, MX, jf, e0, sh=0))
    cal.append(cherry_dot("Chi Cherry", [dx_(238), DAY_Y], t_chi, d0, scale=grow(t_chi), parent=crig))
    cal.append(cherry_dot("Coa Cherry", [dx_(256), DAY_Y], t_coa, e0, scale=grow(t_coa)))
    cal += bracket("Weeks", (dx_(238), 1004), (dx_(256), 1004), t_coa + 0.4, d0, "≈ 2 WEEKS SOONER", side=-1, lab_off=[dx_(200), 990])
    cal[-1]["text"]["justification"] = "right"
    for l in cal[-2:]:
        l["parent"] = crig
    L += cal
    # D: the Chiapas mountain leaves; a shade tree slows the Coatepec cherry
    L.append(shade_tree("Shade Tree", [Q[0] + 40, Q[1] - 4], d0 + 0.8, e0, scale=grow(d0 + 0.8, d=0.7)))
    t_sh = d0 + 1.8 + 286 / 36
    L.append(disc("Shade Marker", A(KL(d0 + 1.8, [dx_(0), DAY_Y]), KL(t_sh, [dx_(286), DAY_Y])), 16, SAGE, d0 + 1.8, e0, sh=0))
    L.append(cherry_dot("Shade Cherry", [dx_(286), DAY_Y], t_sh, e0, scale=grow(t_sh)))
    L += bracket("Month", (dx_(256), 1004), (dx_(286), 1004), t_sh + 0.3, e0, "UP TO ≈ 1 MONTH LATER, SAME SPOT", side=-1, lab_off=[dx_(240), 990])
    L[-1]["text"]["justification"] = "right"
    L.append(src("Src Shade", "SOURCE: VAAST ET AL. 2006 (COSTA RICA)", d0 + 0.8, e0))
    L.append(null(crig, [CX, CY], 0, D, position=A(K(d0, [CX, CY]), K(d0 + 0.8, [CX + 1000, CY]))))
    # E: back to the Coatepec hillside with the isotherm on the 1,200 m line (8->9 handoff)
    L.append(shape("Iso Main", [G("I", path([(SCALE_X, Q[1]), (1100, Q[1])]), trim(0, A(K(iso_t, 0), K(iso_t + 1.0, 100))), stroke(ICE, 6))],
                   [0, 0], iso_t, D, parent=hrig))
    L += mountain("Chiapas", b0 + 1.0, d0 + 0.8, crig, dx=DX_CHI, right=1880, draw=b0 + 1.0)
    L += mountain("Veracruz", b0 + 1.0, D, hrig, right=1100, draw=b0 + 1.0)
    sc = alt_scale("", b0 + 0.6, e0)
    L += sc
    L.append(mp)
    for l in L:
        if l["out"] > e0 and l.get("parent") not in (hrig,) and l["type"] != "null":
            add_out(l, e0)
    L.append(null(hrig, list(Q), 0, D, position=A(K(e0 + 0.6, list(Q)), K(D - 0.4, inv((CX, Q[1])))),
                  scale=A(K(e0 + 0.6, [100, 100]), K(D - 0.4, [Z / HS * 100] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - THE LINE STAYS, THE COLD MOVES (28 s)
# =====================================================================
def s9_close(D):
    L = []
    rig = "Hill Rig"
    b0, lift = 5.6, 7.4
    up = 150 * PPM
    L.append(caps("Place", "ABOVE COATEPEC, VERACRUZ", [90, 90], 0.2, D, size=18, color=INK, just="left"))
    L.append(tag("Tag Above", "ESTRICTAMENTE ALTURA ↑", [1480, 380], 0.4, D, color=MX))
    L.append(tag("Tag Below", "ALTURA ↓", [1480, 600], 0.6, D, color=INK))
    L.append(tag("Tag Height", "≈ 1,200 M", [1650, 470], 0.2, D, size=18))
    L.append(text("Plus", "+ 1 °C", [260, 300], 56, INK, b0, D, font=HEAD, scale=grow(b0)))
    sy0, sy1 = Q[1], Q[1] - up * Z
    L += bracket("Climb", (380, sy1), (380, sy0), lift + 2.6, D, "≈ 150 M · ABOUT A 45-STOREY TOWER", side=-1, lab_off=[400, (sy0 + sy1) / 2 + 6])
    L[-1]["text"]["justification"] = "left"
    L.append(src("Src Lapse", "SOURCE: ICAO STANDARD ATMOSPHERE (0.65 °C / 100 M)", lift, D))
    L += wipe_text("End Title", "Why Mountain Coffee Tastes Different", [CX, 1000], 60, INK, 19.0, D)
    L.append(word_marker("End Swipe", "Why Mountain Coffee Tastes Different", "Different", CX, 1000, 60, 19.8, D))
    L.append(shape("Isotherm", [G("I", path([(SCALE_X - 400, Q[1]), (1600, Q[1])]), stroke(ICE, 6 / Z))], [0, 0], 0, D, parent=rig,
                   position=A(K(lift, [0, 0]), K(lift + 2.4, [0, -up]))))
    L.append(tag("Iso Label", "19 °C", [1650, 410], 0.4, D, color=INK, just="center"))
    L[-1]["transform"]["position"] = A(K(0.4, [1650, 440]), K(lift, [1650, 440]), K(lift + 2.4, [1650, 440 - up * Z]))
    L += hillside(D, "", rig)
    L.append(null(rig, list(Q), 0, D, position=[CX, Q[1]], scale=[Z * 100] * 2))
    L.append(bg(D))
    return L


SCENES = [("S1_Line", 21.0, s1_line), ("S2_Slope", 21.0, s2_slope), ("S3_HeatBudget", 26.0, s3_heat), ("S4_Seed", 26.0, s4_seed),
          ("S5_Reunion", 24.0, s5_reunion), ("S6_Grades", 24.0, s6_grades), ("S7_Ladder", 26.0, s7_ladder),
          ("S8_SameRung", 42.0, s8_same), ("S9_Close", 28.0, s9_close)]

if __name__ == "__main__":
    write(SCENES, "Mountain_Coffee", "03_mountain_coffee", beats=True)
