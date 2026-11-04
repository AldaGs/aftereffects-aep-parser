"""Generator for episode 10, "Café de Olla and the Instant Nation" (scripts/10_cafe_de_olla_script.md).

    python "Coffee Episodes/generators/10_cafe_de_olla.py"      # writes ../json/10_cafe_de_olla.json

Uses episode 8's camera (content coordinates are screen pixels, master push-in cancelled) and episode 9's sack,
cup and coyote truck. Instant coffee is mid grey with an ink outline. No fades.

Follows episode 1's rules: 24 fps, every in/out animation a whole number of 12-frame beats (write(..., beats=True)),
and drawn vectors: coffee shrubs on the hillside, an instant-coffee jar with shoulders and a label, bean outlines,
a water drop, a clay olla with neck and lip.
"""
import importlib, math, random

from coffee_common import *  # noqa: F401,F403

_e8 = importlib.import_module("08_roasting")
_e9 = importlib.import_module("09_who_gets_paid")
cam, finish, tag, arrow, gauge = _e8.cam, _e8.finish, _e8.tag, _e8.arrow, _e8.gauge
sack, side_cup = _e9.sack, _e9.cup

C = (CX, CY)
JAR = (700, 660)
BAG10 = (920, 630)
TABLE_Y = 760
WIN = (1150, 180, 1650, 560)
SAND = SEED_LINE
COFFEE_STATES = ["Chiapas", "Veracruz", "Oaxaca", "Puebla", "Guerrero", "Hidalgo", "San Luis Potosí", "Nayarit"]
PORT = (-96.13, 19.2)


# ---------------------------------------------------------------------
# art
# ---------------------------------------------------------------------
def tree(name, pos, t0, t1, s=100, picked=None):
    """A coffee bush on the hillside with cherries."""
    items = [G("Cherries", *[egg(8, 10, rot=CH_ROT, o=(x, y)) for x, y in ((-10, -12), (9, -16), (-2, -26))], fill(ARA),
               tr={"position": A(K(picked, [0, 0]), K(picked + 0.8, [30, 60])) if picked else [0, 0]}),
             G("Bush", smooth([(-20, -4), (-22, -18), (-15, -30), (-6, -28), (0, -38), (8, -30), (17, -32), (22, -18), (18, -6), (0, -4)], True, corners=(0, 8)),
               stroke(INK, 2), fill(MX)),
             G("Trunk", path([(0, 0), (0, -8)]), stroke(STEM, 4))]  # a rounded coffee bush, as on episode 3's hillside
    return shape(name, items, list(pos), t0, t1, scale=grow(t0, s, 0.3))


SLOPE = [(WIN[0], 520), (WIN[2], 280)]


def kitchen(t0, t1, label_t=None, picked=None):
    out = []
    if label_t is not None:
        out += wipe_text("Place", "COATEPEC, VERACRUZ", [WIN[0], WIN[1] - 30], 22, INK, label_t, t1, font=LAB, just="left")
    for j in range(6):
        u = (j + 0.5) / 6
        x = SLOPE[0][0] + (SLOPE[1][0] - SLOPE[0][0]) * u
        y = SLOPE[0][1] + (SLOPE[1][1] - SLOPE[0][1]) * u
        out.append(tree(f"Tree {j + 1}", (x, y + 6), t0 + 0.8 + j * 0.12, t1, picked=picked if j == 3 else None))
    out.append(shape("Hill", [G("H", path(SLOPE), trim(0, A(K(t0 + 0.4, 0), K(t0 + 1.0, 100))), stroke(INK, 3))], [0, 0], t0, t1))
    out.append(shape("Window", [G("W", rect([WIN[2] - WIN[0], WIN[3] - WIN[1]], [(WIN[0] + WIN[2]) / 2, (WIN[1] + WIN[3]) / 2]),
                                  path([((WIN[0] + WIN[2]) / 2, WIN[1]), ((WIN[0] + WIN[2]) / 2, WIN[3])]), stroke(INK, 5))], [0, 0], t0, t1))
    out.append(shape("Table", [G("T", path([(200, TABLE_Y), (1720, TABLE_Y)]), trim(0, A(K(t0, 0), K(t0 + 0.6, 100))), stroke(INK, 5))], [0, 0], t0, t1))
    return out


def jar(name, pos, t0, t1, **tr):
    """Instant coffee jar: ribbed lid, rounded shoulders, a paper label band."""
    body = smooth([(-62, -96), (62, -96), (84, -70), (86, 70), (76, 94), (-76, 94), (-86, 70), (-84, -70)], True, corners=(0, 1))
    return shape(name, [G("Ribs", *[path([(x, -124), (x, -102)]) for x in range(-60, 61, 20)], stroke(INK, 2)),
                        G("Lid", rect([136, 30], [0, -112], 6), stroke(INK, 4), fill(GREY)),
                        G("Label", rect([172, 70], [0, 4]), stroke(INK, 3), fill(WHITE)),
                        G("Body", body, stroke(INK, 4), fill(GREY))], pos, t0, t1, **tr)


def cup_top(name, pos, d, t0, t1, col=None, **tr):
    items = []
    if col is not None:
        items.append(G("Coffee", ell([d * 0.78, d * 0.78]), fill(col), tr=tr.pop("fill_tr", None)))
    items.append(G("Rim", ell([d, d]), stroke(INK, max(3, d * 0.03)), fill(WHITE)))
    return shape(name, items, pos, t0, t1, **tr)


def factory(name, pos, t0, t1, col=GREY, s=100, **tr):
    roof = [(-100, 0), (-100, -60), (-60, -90), (-60, -60), (-20, -90), (-20, -60), (20, -90), (20, -60), (100, -60), (100, 0)]
    items = [G("Chimney", rect([20, 70], [70, -95]), stroke(INK, 4), fill(col)),
             G("F", path(roof, True), stroke(INK, 4), fill(col))]
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def cdmx_square(name, pos, t0, t1, **tr):
    return shape(name, [G("Q", rect([64, 64], None, 10), stroke(INK, 3))], pos, t0, t1, **tr)


def mex(name, t0, t1, k=34, o=(760, 560), green_t=None):
    sp = lambda ll: screen(ll, k, (-102, 23.5), o)
    st = [path([sp(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    out = []
    if green_t is not None:
        gs = [path([sp(p) for p in r], True) for s in COFFEE_STATES for r in GEO["mexico"][s]]
        out.append(shape(f"{name} Coffee", [G("C", *gs, stroke(WHITE, 2), fill(MX))], [0, 0], green_t, t1))
    out.append(shape(name, [G("B", *st, stroke(WHITE, 2)), G("S", *st, fill(LAND))], [0, 0], t0, t1))
    return out, sp


ROW = [(420 + 120 * j, 540) for j in range(10)]


def cups_row(t0, t1, grey_t=None, green_t=None, rig=None):
    out = []
    for j, p in enumerate(ROW):
        if j < 6:
            col = GREY if grey_t is None else A(K(grey_t + j * 0.15, WHITE), K(grey_t + j * 0.15 + 0.2, GREY))
        else:
            col = WHITE if green_t is None else A(K(green_t + (j - 6) * 0.3, WHITE), K(green_t + (j - 6) * 0.3 + 0.3, MX))
        out.append(cup_top(f"Cup {j + 1}", list(p), 90, t0, t1, col=col, parent=rig))
    return out


# =====================================================================
# SCENE 1 - A JAR IN COFFEE COUNTRY (21 s)
# =====================================================================
def s1_jar(D):
    L = []
    b0, c0, d0 = 5.0, 10.0, 16.0
    L.append(tag("Chip Ha", "≈ 670,000 HA OF COFFEE", [(WIN[0] + WIN[2]) / 2, WIN[3] + 50], c0, d0, size=16))
    L.append(tag("Chip Cups", "≈ 6 IN 10 CUPS", [JAR[0], 500], c0 + 1.0, d0, size=16))
    L.append(src("Src USDA", "SOURCE: USDA FAS MX2026-0026", c0, d0))
    L.append(shape("Spoon", [G("S", path([(0, 0), (60, -60)]), ell([22, 14], [0, 0]), stroke(INK, 4))], [930, 640], b0 + 1.6, d0,
                   rotation=X(f"time > {b0 + 2} ? Math.sin(time * 9) * 8 : 0")))
    L.append(side_cup("Cup", [960, 700], b0 + 1.2, d0, scale=grow(b0 + 1.2, 50)))
    L.append(jar("Jar", list(JAR), b0, d0, position=A(K(b0, [JAR[0] - 900, JAR[1]]), K(b0 + 0.8, list(JAR)))))
    L += kitchen(0, d0, label_t=2.0)
    for l in L:
        add_out(l, min(l["out"], d0))
    L.insert(0, cup_top("Lid Top", [JAR[0], 548], 220, d0, D, col=GREY, position=A(K(d0, [JAR[0], 548]), K(d0 + 1.6, list(C))),
                        scale=A(K(d0, [68, 68]), K(d0 + 1.6, [100, 100]))))
    return finish(L, D)


# =====================================================================
# SCENE 2 - SIX CUPS IN TEN (14 s)
# =====================================================================
def s2_cups(D):
    L = []
    b0, x0 = 6.5, 13.0
    rig = "Row Rig"
    L.append(tag("Six", "≈ 6 IN 10 CUPS ARE INSTANT", [CX, 650], 2.4, b0, size=18))
    L.append(src("Src USDA Cups", "SOURCE: USDA FAS MX2026-0026 (1.82 OF 3.16 M BAGS)", 2.4, b0))
    L.append(cup_top("Lid", list(C), 220, 0, 1.4, col=GREY, position=A(K(0.2, list(C)), K(1.2, list(ROW[0]))), scale=A(K(0.2, [100, 100]), K(1.2, [41, 41]))))
    row = cups_row(1.2, x0, grey_t=1.6, rig=rig)
    for l in row[1:]:
        l["in"] = 1.3
        l["transform"]["scale"] = grow(1.3 + 0.05 * row.index(l))
    L += row
    for l in L:
        add_out(l, min(l["out"], x0))
    L.append(tag("Area", "≈ 670,000 HA ≈ MEXICO CITY × 4.5", [1560, 860], b0 + 3.0, x0, size=14))
    L.append(src("Src INEGI", "SOURCE: USDA FAS MX2026-0026; INEGI", b0 + 3.0, x0))
    L.append(caps("CDMX Label", "MEXICO CITY", [1500, 690], b0 + 1.6, x0, size=12, color=INK))
    for j in range(5):
        t = b0 + 2.0 + j * 0.25
        L.append(shape(f"CDMX {j + 1}", [G("Q", rect([64 if j < 4 else 32, 64], [-16 if j == 4 else 0, 0], 6), stroke(INK, 3))], [1380 + 72 * j, 760], t, x0,
                       scale=grow(t, 100, 0.2)))
    for l in L[-6:]:
        add_out(l, x0)
    m, _ = mex("Map", b0, D, green_t=b0 + 1.0)
    L += m
    L.append(null(rig, list(C), 0, D, position=A(K(b0 - 0.6, list(C)), K(b0, [CX, 140]))))
    return finish(L, D)


# =====================================================================
# SCENE 3 - GROWN TO LEAVE (26 s)
# =====================================================================
GRADE = [("CAFÉ VERDE · CLASIFICACIÓN", 16, LAB), ("", 10, BODY), ("Grado exportación: grano entero", 15, BODY),
         ("Rechazo: quebrado y con defectos", 15, BODY), ("Destino: mercado nacional", 15, BODY)]
HEAP = (1180, 820)


def s3_export(D):
    L = []
    b0, b1, c0, d0 = 6.0, 13.5, 14.0, 21.0
    m, sp = mex("Map", 0, D, green_t=0)
    pt = sp(PORT)
    L.append(tag("Port", "VERACRUZ PORT", [pt[0] + 20, pt[1] + 30], 0.6, d0, size=13, just="left"))
    for j, (dst, w) in enumerate((((760, 120), 14), ((1900, 260), 7), ((1900, 520), 4))):
        L.append(shape(f"Export {j + 1}", [G("A", arc(pt, dst, -0.25), trim(0, A(K(0.8 + j * 0.6, 0), K(2.4 + j * 0.6, 100))), stroke(INK, w))],
                       [0, 0], 0.8 + j * 0.6, d0))
    L.append(tag("US", "UNITED STATES", [760, 90], 2.4, d0, size=14))
    L += doc("Grade", GRADE, [1500, 520], (520, 380), b0, b1, hl_line=3, credit="EXPORT GRADING SHEET, RECREATED")
    # C: the sieve
    sv = (1180, 640)
    L.append(tag("Home", "HOME MARKET", [HEAP[0], HEAP[1] + 70], c0 + 3.0, d0, size=14))
    L.append(src("Src Nolasco", "SOURCE: NOLASCO, CAFÉ Y SOCIEDAD EN MÉXICO (1985)", c0 + 1.0, d0))
    rnd = random.Random(3)
    for j in range(10):
        t = c0 + 0.6 + j * 0.25
        good = j % 3 != 0
        dst = [1460, 640] if good else [HEAP[0] + rnd.uniform(-20, 20), HEAP[1]]
        L.append(shape(f"Grain {j + 1}", [G("B", _e8.bean_shape(20, 14), stroke(INK, 2), fill(ROAST[0] if good else GREY))], [sv[0], sv[1] - 120], t, t + 1.0,
                       position=A(K(t, [sv[0], sv[1] - 120]), K(t + 0.4, list(sv)), K(t + 1.0, dst))))
    L.append(sack("Ship Sack", [1460, 640], c0, d0, col=SEED, s=140, scale=grow(c0, 140)))
    L.append(shape("Sieve", [G("S", path([(-90, 0), (90, 0)]), *[path([(x, -8), (x, 8)]) for x in range(-70, 80, 20)], stroke(INK, 4))], list(sv), c0, d0, scale=grow(c0)))
    for l in L:
        add_out(l, min(l["out"], d0))
    L.insert(0, shape("Heap", [G("H", ell([110, 44]), stroke(INK, 3), fill(GREY))], list(HEAP), c0 + 1.6, D,
                      scale=A(K(c0 + 1.6, [0, 0]), K(c0 + 3.0, [100, 100]), K(d0 + 0.4, [100, 100]), K(d0 + 2.4, [27, 68])),
                      position=A(K(d0 + 0.4, list(HEAP)), K(d0 + 2.4, [360, 540]))))
    for l in m:
        add_out(l, d0)
    L += m
    return finish(L, D)


# =====================================================================
# SCENE 4 - A SWISS ANSWER TO A BRAZILIAN SURPLUS (23 s)
# =====================================================================
TL = [(1930, 360), (1938, 640), (1949, 960), ("TODAY", 1400)]
FAC4, FAC_S = (1400, 420), 100


def s4_nescafe(D):
    L = []
    for j, (y, x) in enumerate(TL):
        L.append(caps(f"Year {y}", str(y), [x, 590], 0.4 + j * 0.2, D, size=14, color=INK))
    L.append(shape("Timeline", [G("T", path([(360, 540), (1600, 540)]), trim(0, A(K(0.3, 0), K(1.3, 100))), stroke(INK, 3)),
                                G("Ticks", *[path([(x, 530), (x, 550)]) for _, x in TL], stroke(INK, 3))], [0, 0], 0.3, D))
    # A: Brazil's surplus
    for j in range(10):
        r = 0 if j < 4 else (1 if j < 7 else (2 if j < 9 else 3))
        c = [0, 1, 2, 3, 0, 1, 2, 0, 1, 0][j]
        n = [4, 3, 2, 1][r]
        L.append(sack(f"Surplus {j + 1}", [360 + (c - (n - 1) / 2) * 44, 470 - r * 46], 1.0 + j * 0.08, D, col=GREY, s=60, scale=grow(1.0 + j * 0.08, 60)))
    L.append(tag("Surplus", "BRAZIL: UNSOLD SURPLUS", [360, 260], 1.8, D, size=13))
    L.append(tag("Vevey", "NESTLÉ, VEVEY", [560, 200], 3.0, D, size=13, just="left"))
    L.append(leader("Vevey Leader", (420, 300), (550, 210), 2.8, D))
    # B, C
    L.append(jar("Jar", [640, 420], 6.0, D, scale=grow(6.0, 45)))
    L.append(tag("Launched", "NESCAFÉ LAUNCHED", [640, 330], 6.4, D, size=13))
    L.append(src("Src Nescafe", "SOURCE: NESCAFÉ COMPANY HISTORY; MERCA2.0", 6.4, 14.0))
    L.append(disc("Mexico Pin", [960, 440], 24, MX, 10.0, D, sh=0, scale=grow(10.0)))
    L.append(tag("Arrives", "ARRIVES IN MEXICO", [960, 400], 10.4, D, size=13))
    # D: Toluca
    L.append(tag("Buyer", "NESTLÉ SAYS: BIGGEST COFFEE BUYER IN MEXICO", [1400, 250], 14.0, D, size=13))
    L.append(caps("Toluca", "TOLUCA", [1400, 480], 15.0, D, size=12, color=INK))
    L.append(tag("Expand", "2013: +30 %", [1560, 330], 17.6, D, size=13, just="left"))
    L.append(shape("Factory 2013", [G("F", path([(-100, 0), (-100, -60), (-60, -90), (-60, -60), (-20, -90), (-20, -60), (20, -90), (20, -60), (100, -60), (100, 0)], True),
                                      stroke(INK, 3, dashes=(10, 8)))], [FAC4[0], FAC4[1] + 30], 17.0, 20.0, scale=grow(17.0, 130)))
    L.append(src("Src Fin", "SOURCE: EL FINANCIERO (4 AUG 2013)", 17.0, D))
    for l in L:
        if l["name"] not in ("Timeline",):
            add_out(l, min(l["out"], 20.4))
    L.insert(0, factory("Factory", [FAC4[0], FAC4[1] + 30], 14.6, D, scale=grow(14.6)))
    return finish(L, D)


# =====================================================================
# SCENE 5 - HOW A BEAN BECOMES POWDER (45 s)
# =====================================================================
COLS = [440 + 100 * j for j in range(6)]
COL_TOP, COL_BOT = 360, 720


def s5_soluble(D):
    L = []
    f0, a0, b0, c0, d0, e0, x0 = 1.6, 2.0, 8.0, 20.0, 27.0, 31.0, 37.0
    stage = {}
    # A: roast and grind
    st = [tag("Roast", "ROAST", [220, 430], a0 + 0.4, x0, size=13),
          tag("Grind", "GRIND", [220, 850], a0 + 3.0, x0, size=13),
          shape("Grinder", [G("G", path([(-50, -40), (50, -40), (10, 30), (-10, 30)], True), stroke(INK, 4), fill(WHITE))], [220, 760], a0 + 2.6, x0, scale=grow(a0 + 2.6)),
          shape("Drum", [G("Spokes", path([(-40, 0), (40, 0)]), stroke(INK, 3), tr={"rotation": X("time * 120")}),
                         G("D", ell([130, 130]), stroke(INK, 4), fill(WHITE))], [220, 560], a0, x0, scale=grow(a0))]
    for j in range(5):
        t = a0 + 0.6 + j * 0.4
        st.insert(0, shape(f"Bean {j + 1}", [G("B", _e8.bean_shape(26, 18), stroke(INK, 2), fill(A(K(t + 0.6, SEED), K(t + 1.2, ROAST[4]))))], [220, 440], t, t + 2.4,
                           position=A(K(t, [100, 440]), K(t + 0.6, [220, 560]), K(t + 1.6, [220, 560]), K(t + 2.4, [220, 760]))))
    stage["a"] = st
    # B: the columns
    st = [tag("Temp", "≈ 180 °C", [1120, 300], b0 + 7.0, x0, size=18, just="left"),
          tag("Kettle Label", "KETTLE: 100 °C", [1120, 700], b0 + 7.6, x0, size=13, just="left"),
          shape("Kettle", [G("K", path([(-40, 30), (-30, -30), (30, -30), (40, 30)], True), path([(40, -10), (70, -30)]), stroke(GREY, 3, dashes=(8, 6)))],
                [1060, 640], b0 + 7.4, x0),
          shape("Thermo", [G("Fill", rect([14, 240], [0, -120]), fill(INK), tr={"scale": A(K(b0 + 3.0, [100, 10]), K(b0 + 7.0, [100, 100]))}),
                           G("Mark", path([(-20, -133), (20, -133)]), stroke(GREY, 2, dashes=(4, 4))),
                           G("Tube", rect([26, 250], [0, -125], 13), stroke(INK, 3))], [1060, 520], b0 + 2.8, x0, scale=grow(b0 + 2.8)),
          gauge("Gauge", [690, 270], b0 + 2.6, x0, A(K(b0 + 2.6, -80), K(b0 + 7.0, 50))),
          src("Src Clarke", "SOURCE: CLARKE & VITZTHUM, COFFEE: RECENT DEVELOPMENTS (2001)", b0 + 3.0, c0)]
    snake = []
    for j, x in enumerate(reversed(COLS)):
        snake += [(x, COL_TOP + 20), (x, COL_BOT - 20)] if j % 2 == 0 else [(x, COL_BOT - 20), (x, COL_TOP + 20)]
    snake = [(COLS[-1] + 80, COL_TOP + 20)] + snake
    st.append(shape("Water", [G("W", path(snake), trim(0, A(K(b0 + 2.0, 0), K(b0 + 6.0, 100))), stroke(WATER, 6))], [0, 0], b0 + 2.0, x0))
    st.append(shape("Grounds", [G("G", *[rect([50, COL_BOT - COL_TOP - 20], [x, (COL_TOP + COL_BOT) / 2]) for x in COLS], fill(ROAST[4]))], [0, 0], b0 + 0.8, x0))
    st.append(shape("Columns", [G("C", *[rect([64, COL_BOT - COL_TOP], [x, (COL_TOP + COL_BOT) / 2], 10) for x in COLS], stroke(INK, 4), fill(WHITE))], [0, 0], b0, x0))
    stage["b"] = st
    # C: how much ends up dissolved
    st = [tag("Pot Bar Label", "KITCHEN POT ≈ 20 %", [1270, 900], c0 + 0.6, x0, size=11),
          tag("Col Bar Label", "COLUMNS ≈ 45 %", [1430, 900], c0 + 1.4, x0, size=11),
          shape("Pot Bar", [G("B", rect([80, 100], [0, -50]), stroke(INK, 2), fill(GREY2))], [1270, 860], c0 + 0.4, x0, scale=A(K(c0 + 0.4, [100, 0]), K(c0 + 0.8, [100, 100]))),
          shape("Col Bar", [G("B", rect([80, 225], [0, -112.5]), stroke(INK, 2), fill(GREY))], [1430, 860], c0 + 1.2, x0, scale=A(K(c0 + 1.2, [100, 0]), K(c0 + 1.8, [100, 100]))),
          tag("Dissolved", "OF THE GROUNDS' WEIGHT, DISSOLVED", [1350, 590], c0 + 0.4, x0, size=11),
          src("Src SCA", "SOURCE: SCA BREWING CONTROL CHART; CLARKE & VITZTHUM (2001)", c0 + 0.4, d0)]
    stage["c"] = st
    # D: evaporator; E: spray tower or freeze
    st = [tag("Evap", "CONCENTRATED", [1330, 190], d0 + 0.6, x0, size=12),
          shape("Evaporator", [G("E", ell([110, 150]), stroke(INK, 4), fill(A(K(d0 + 0.6, "#6B4226"), K(d0 + 2.6, ROAST[4]))))], [1330, 300], d0, x0, scale=grow(d0)),
          arrow("To Evap", (COLS[0] - 20, COL_TOP - 30), (1260, 300), d0 + 0.2, x0, w=3)]
    stage["d"] = st
    rnd = random.Random(5)
    st = [arrow("To Spray", (1390, 280), (1560, 240), e0, x0, w=3), arrow("To Freeze", (1390, 330), (1560, 620), e0 + 0.4, x0, w=3),
          tag("Spray", "SPRAYED INTO HOT AIR", [1640, 140], e0 + 0.8, x0, size=11),
          tag("Freeze", "FROZEN, DRIED UNDER VACUUM", [1640, 560], e0 + 1.6, x0, size=11),
          shape("Granules", [G("G", *[rect([12, 12], [rnd.uniform(-60, 60), rnd.uniform(-10, 10)]) for _ in range(9)], fill(GREY))], [1640, 700], e0 + 3.0, x0),
          shape("Slab", [G("S", rect([160, 30]), stroke(WATER, 3), fill(GREY2))], [1640, 640], e0 + 1.4, e0 + 3.0, scale=grow(e0 + 1.4))]
    for j in range(8):
        t = e0 + 1.0 + j * 0.25
        x = 1640 + rnd.uniform(-25, 25)
        st.append(disc(f"Drop {j + 1}", A(K(t, [x, 200]), K(t + 1.2, [x, 400], None)), 10, GREY, t, t + 1.2, sh=0))
    st.append(shape("Tower", [G("T", rect([90, 260], [0, 0], 10), stroke(INK, 4))], [1640, 300], e0 + 0.6, x0, scale=grow(e0 + 0.6)))
    stage["e"] = st
    order = ["a", "b", "c", "d", "e"]
    starts = [a0, b0, c0, d0, e0]
    for j, k in enumerate(order):
        if j + 1 < len(order):
            dim(stage[k], starts[j + 1])
        for l in stage[k]:
            add_out(l, min(l["out"], x0))
        L += stage[k]
    # F: two grams of powder, five of green, ten for a pot
    p0 = x0 + 0.4
    L.insert(0, sack("Sack", list(C), D - 2.4, D, col=SEED, s=140, scale=grow(D - 2.4, 140)))
    L.insert(1, src("Src Ratio", "SOURCE: SCA GOLDEN CUP RATIO; NESTLÉ SERVING SIZE", p0, D))
    for j, (s, x, h, col, t) in enumerate((("2 G POWDER", 560, 30, GREY, p0), ("≈ 5 G GREEN", CX, 70, SEED, p0 + 1.0), ("≈ 10 G GREEN", 1360, 140, SEED, p0 + 2.0))):
        o = D - 2.6 if j == 1 else D
        L.insert(0, tag(f"Pile {j + 1} Label", s, [x, 680], t + 0.3, min(o, D - 2.6) if j == 1 else D, size=16))
        L.insert(0, shape(f"Pile {j + 1}", [G("P", path([(-h * 1.3, 0), (0, -h), (h * 1.3, 0)], True), stroke(INK, 3), fill(col))], [x, 620], t, D - 2.4 if j == 1 else D,
                          scale=grow(t), position=A(K(D - 3.2, [x, 620]), K(D - 2.4, list(C))) if j == 1 else [x, 620]))
    for l in L[:6]:
        if l["name"].startswith(("Pile 1", "Pile 3")):
            add_out(l, D - 2.6)
    # the factory frame: the S4 outline scales up and drops its fill
    L.append(shape("Frame", [G("F", rect([1800, 860], [CX, 540], 12), stroke(INK, 4))], [0, 0], f0, x0))
    L.append(factory("Factory", [FAC4[0], FAC4[1] + 30], 0, f0, col=A(K(0.2, GREY), K(1.0, WHITE)),
                     position=A(K(0.2, [FAC4[0], FAC4[1] + 30]), K(f0, [CX, CY])), scale=A(K(0.2, [100, 100]), K(f0, [600, 600]))))
    return finish(L, D)


# =====================================================================
# SCENE 6 - COFFEE COMING IN (30 s)
# =====================================================================
PIV = (CX, 420)


def s6_imports(D):
    L = []
    b0, c0, d0, e0 = 10.0, 15.0, 21.0, 26.0
    br = "Balance Rig"
    bal = [tag("In", "≈ 2.0 M BAGS IN", [600, 650], 4.4, c0, size=16, parent=br),
           tag("Out", "≈ 1.8 M BAGS OUT", [1320, 650], 7.0, c0, size=16, parent=br),
           tag("Forecast", "GREEN COFFEE, 2025/26 FORECAST", [CX, 140], 1.0, c0, size=14),
           src("Src USDA", "SOURCE: USDA FAS MX2026-0026", 1.0, c0)]
    for side, n, x, t0 in (("Imports", 20, 600, 0.4), ("Exports", 18, 1320, 5.0)):
        bal.append(caps(f"{side} Label", side.upper(), [x, 610], t0, c0, size=13, color=INK, parent=br))
        for j in range(n):
            r, c = divmod(j, 5)
            t = t0 + j * 0.12
            p = [x - 88 + c * 44, 480 - r * 46]
            pos = A(K(0, list(C)), K(0.8, p)) if side == "Imports" and j == 0 else p
            bal.append(sack(f"{side} Sack {j + 1}", p, t if j else 0, c0, col=SEED, s=60, position=pos, parent=br,
                            scale=A(K(0, [140, 140]), K(0.8, [60, 60])) if side == "Imports" and j == 0 else grow(t, 60, 0.2)))
        bal.append(shape(f"{side} Pan", [G("P", path([(-130, 0), (130, 0)]), stroke(INK, 5))], [x, 510], 0, c0, parent=br))
    bal.append(shape("Beam", [G("B", path([(600, PIV[1]), (1320, PIV[1])]), path([(600, PIV[1]), (600, 510)]), path([(1320, PIV[1]), (1320, 510)]), stroke(INK, 5))],
                     [0, 0], 0, c0, parent=br))
    bal.append(shape("Post", [G("P", path([PIV, (CX, 860)]), path([(CX - 80, 860), (CX + 80, 860)]), stroke(INK, 5))], [0, 0], 0, c0))
    bal.append(tag("Robusta", "MUCH OF IT ROBUSTA", [420, 300], b0 + 1.4, c0, size=14, color=ROB))
    bal.append(tag("Origins", "FROM BRAZIL AND VIETNAM", [420, 260], b0 + 0.4, c0, size=13))
    bal.append(arrow("Origin Arrow", (300, 200), (560, 340), b0, c0))
    bal.append(src("Src DataMx", "SOURCE: DATA MÉXICO (SECRETARÍA DE ECONOMÍA)", b0, c0))
    for l in bal:
        add_out(l, min(l["out"], c0))
    L += bal
    # C, D: the robusta crop and the new plant
    m, sp = mex("Map", c0, e0, k=26, o=(760, 560))
    ver = sp((-96.6, 18.6))
    L.append(tag("Rob Crop", "≈ 0.5 M BAGS, ≈ 1 IN 8 OF THE CROP", [ver[0] + 260, ver[1] - 150], c0 + 1.6, e0, size=14, just="left"))
    L.append(tag("Tonnes", "≈ 30,000 T", [ver[0] + 260, ver[1] - 116], d0 + 1.0, e0, size=14, just="left"))
    for j in range(5):
        t = c0 + 0.8 + j * 0.15
        L.append(sack(f"Rob {j + 1}", [ver[0] + 120 + j * 30, ver[1] - 60], t, e0, col=ROB, s=56, scale=grow(t, 56, 0.2)))
    L.append(shape("Rob Ghost", [G("G", rect([100, 50]), stroke(GREY, 2, dashes=(6, 5)))], [ver[0] + 170, ver[1] - 50], c0 + 1.2, e0))
    L.append(tag("Plant", "NEW PLANT, 2022: ≈ 40,000 T A YEAR", [ver[0] - 30, ver[1] + 110], d0 + 0.6, e0, size=14, just="right"))
    L.append(tag("Protest", "GROWER PROTESTS, 2019", [ver[0] - 30, ver[1] + 144], d0 + 2.0, e0, size=13, just="right"))
    L.append(src("Src Plant", "SOURCE: NESTLÉ MÉXICO (2022); MILENIO", d0, e0))
    L.append(factory("Plant Icon", list(ver), d0, e0, s=50, scale=grow(d0, 50)))
    L.append(src("Src Crop", "SOURCE: USDA FAS MX2026-0026", c0 + 1.0, d0))
    L += m
    for l in L:
        add_out(l, min(l["out"], e0))
    L.insert(0, cup_top("Instant", list(C), 300, e0 + 0.4, D, col=GREY, scale=grow(e0 + 0.4),
                        fill_tr={"scale": A(K(e0 + 1.8, [100, 100]), K(D - 0.4, [0, 0]))}))
    L.append(null(br, list(PIV), 0, D, rotation=A(K(5.0, 0), K(8.6, -6)), position=A(K(c0 - 0.8, list(PIV)), K(c0, [PIV[0] - 1500, PIV[1]]))))
    return finish(L, D)


# =====================================================================
# SCENE 7 - AN EASY WAY IN (36 s)
# =====================================================================
POT = (640, 620)
MOUTH = (POT[0], 440)
STICK = [G("Curl", path([(-180, -4), (180, -4)]), stroke(INK, 2, 50)), G("Stick", rect([400, 34], None, 17), stroke(INK, 3), fill(CIN))]
OLLA = [("Café de olla", 26, HEAD), ("", 10, BODY), ("Cuenta la leyenda que las", 17, BODY), ("soldaderas lo preparaban", 17, BODY),
        ("para las tropas.", 17, BODY)]


def s7_olla(D):
    L = []
    t0, b0, c0, d0, e0, f0 = 2.6, 4.0, 14.0, 21.0, 27.0, 32.0
    ing = [("WATER", WATER, b0), ("GROUND COFFEE", ROAST[4], b0 + 2.4), ("PILONCILLO · RAW CANE SUGAR", ROAST[2], b0 + 4.8), ("CANELA · CINNAMON", CIN, b0 + 7.2)]
    for j, (s, col, t) in enumerate(ing):
        L.append(tag(f"Ing {j + 1}", s, [1000, 300 + 44 * j], t + 0.6, c0, size=14, just="left"))
        L.append(disc(f"Swatch {j + 1}", [970, 295 + 44 * j], 20, col, t + 0.6, c0, sh=0, scale=grow(t + 0.6)))
        if j < 3:
            if j == 0:    # a drop of water
                shp = smooth([(0, -24), (10, -4), (14, 8), (8, 18), (0, 20), (-8, 18), (-14, 8), (-10, -4)], True, corners=(0,))
            elif j == 1:  # a spoonful of ground coffee
                shp = smooth([(-28, 12), (-18, -2), (-6, -12), (8, -10), (20, -2), (28, 12)], True, corners=(0, 5))
            else:         # piloncillo, a cone of raw cane sugar
                shp = path([(-28, 22), (0, -28), (28, 22)], True)
            L.append(shape(f"Drop {j + 1}", [G("D", shp, stroke(INK, 2), fill(col))], [MOUTH[0], 120], t, t + 1.0,
                           position=A(K(t, [MOUTH[0] + 20 * j, 120]), K(t + 1.0, [MOUTH[0], MOUTH[1] + 20], None))))
    L.append(shape("Steam", [G("S", *[path([(x, 0), (x + 10, -40), (x - 10, -80), (x, -120)], False) for x in (-50, 0, 50)], stroke(INK, 2.5),
                               tr={"position": X("[0, -Math.abs(Math.sin(time)) * 10]")})], [MOUTH[0], MOUTH[1] - 30], b0 + 1.0, f0))
    # C: the legend
    L += doc("Olla Doc", OLLA, [1400, 560], (480, 320), c0, d0, hl_line=2, credit="MÉXICO DESCONOCIDO, RECREATED")
    # D: the pot's solids by weight
    segs = [("COFFEE", 1.0, ROAST[4]), ("PILONCILLO", 2.5, ROAST[2]), ("CANELA", 0.12, CIN)]
    tot, x = sum(s[1] for s in segs), 1000
    for j, (s, w, col) in enumerate(segs):
        px = 760 * w / tot
        t = d0 + 0.4 + j * 0.4
        L.append(caps(f"Seg {s} Label", s, [x + px / 2 if j < 2 else x + px + 10, 930], t + 0.3, f0, size=11, color=INK, just="center" if j < 2 else "left"))
        L.append(shape(f"Seg {s}", [G("S", rect([px, 40], [px / 2, 0]), stroke(INK, 2), fill(col))], [x, 880], t, f0, scale=A(K(t, [0, 100]), K(t + 0.4, [100, 100]))))
        x += px
    L.append(tag("Seg Title", "SOLIDS IN THE POT, BY WEIGHT", [1000, 830], d0 + 0.4, f0, size=13, just="left"))
    L.append(src("Src Recipe", "SOURCE: MÉXICO DESCONOCIDO RECIPE", d0 + 0.4, e0))
    # E: the sugar-roasted bag
    L.append(caps("Bag Line", "mezclado con azúcar caramelizada", [1380, 520], e0, f0, size=0.1, color=WHITE))
    L.pop()
    L.append(text("Bag Fine", "café tostado mezclado", [1380, 530], 18, INK, e0 + 0.2, f0))
    L.append(text("Bag Fine 2", "con azúcar caramelizada", [1380, 556], 18, INK, e0 + 0.2, f0))
    L.append(marker("Bag Swipe", 1380 - tw("con azúcar caramelizada", 18, BODY) / 2 - 8, 556, tw("con azúcar caramelizada", 18, BODY) + 16, e0 + 1.2, f0, size=18))
    L.append(text("Bag Name", "CAFÉ TOSTADO", [1380, 420], 34, INK, e0 + 0.2, f0, font=HEAD))
    L.append(shape("Sugar Bag", [G("B", rect([340, 420], None, 8), stroke(INK, 4), fill(KRAFT))], [1380, 480], e0, f0))
    for l in L[-5:]:
        p = l["transform"]["position"]
        l["transform"]["position"] = A(K(e0, [p[0] + 700, p[1]]), K(e0 + 0.7, p))
    L.append(src("Src NMX", "NMX-F-173-SCFI-2020", e0 + 0.6, f0))
    for l in L:
        add_out(l, min(l["out"], f0))
    # the stick: in the pot, then out and flat across the frame
    L.insert(0, shape("Stick", STICK, [MOUTH[0] + 40, MOUTH[1] - 50], b0 + 7.2, D, rotation=A(K(b0 + 7.8, -70), K(f0 + 0.4, -70), K(D - 1.0, 0)),
                      position=A(K(b0 + 7.2, [MOUTH[0] + 40, 100]), K(b0 + 7.8, [MOUTH[0] + 40, MOUTH[1] - 50]), K(f0 + 0.4, [MOUTH[0] + 40, MOUTH[1] - 50]), K(D - 1.0, list(C))),
                      scale=A(K(b0 + 7.2, [40, 40]), K(f0 + 0.4, [40, 40]), K(D - 1.0, [100, 100]))))
    flame = smooth([(-42, 0), (-34, -30), (-18, -50), (-12, -22), (0, -66), (12, -24), (20, -56), (34, -28), (42, 0)], True, corners=(0, 2, 4, 6, 8))
    # olla de barro: a round clay belly, a narrow neck and a flared lip, two loop handles on the shoulders
    olla = smooth([(-150, -180), (150, -180), (124, -160), (118, -130), (170, -90), (205, 0), (180, 110), (110, 175), (0, 190), (-110, 175), (-180, 110),
                   (-205, 0), (-170, -90), (-118, -130), (-124, -160)], True, corners=(0, 1))
    pot = [shape("Flame", [G("F", flame, stroke(INK, 3))], [POT[0], 880], t0, f0),
           shape("Pot", [G("Handle", smooth([(-150, -110), (-200, -96), (-186, -50), (-176, -60)], False), smooth([(150, -110), (200, -96), (186, -50), (176, -60)], False),
                           stroke(INK, 5)),
                         G("Band", smooth([(-196, -20), (0, 0), (196, -20)], False), stroke(INK, 3, 50)),
                         G("Body", olla, stroke(INK, 5), fill(SAND))], list(POT), t0, f0)]
    L += pot
    L.append(cup_top("Mouth", list(C), 300, 0, t0, col=SAND, fill_tr={"scale": A(K(0.4, [0, 0]), K(1.2, [128, 128]))}))
    return finish(L, D)


# =====================================================================
# SCENE 8 - THE CINNAMON'S ISLAND (17 s)
# =====================================================================
WK, WC, WO = 5, (-9, 13.6), (CX, CY)
CDMX, SL = (-99.13, 19.43), (80.7, 7.8)


def wpt(ll):
    return screen(ll, WK, WC, WO)


def s8_cinnamon(D):
    L = []
    mx, sl = wpt(CDMX), wpt(SL)
    r0, b0, back = 1.4, 6.0, 12.0
    L.append(disc("CDMX Dot", list(mx), 24, MX, back + 1.2, D, sh=0, scale=grow(back + 1.2)))
    L.append(text("Verum", "Cinnamomum verum", [sl[0], sl[1] + 60], 28, INK, r0 + 2.0, D - 0.6, font=SCI))
    L.append(tag("Before", "CINNAMON, BEFORE COFFEE", [sl[0], sl[1] + 100], b0, D - 0.6, size=13))
    L.append(tag("Share", "≈ 38 % (2024), LARGEST BUYER", [1700, 830], b0 + 1.6, D - 0.6, size=13))
    L.append(caps("Bar Title", "SRI LANKA'S CINNAMON EXPORTS", [1700, 470], b0 + 0.8, D - 0.6, size=11, color=INK))
    L.append(shape("Mexico Share", [G("B", rect([60, 300 * 0.38], [0, -150 * 0.38]), fill(MX))], [1700, 790], b0 + 1.2, D - 0.6,
                   scale=A(K(b0 + 1.2, [100, 0]), K(b0 + 1.8, [100, 100]))))
    L.append(shape("Share Outline", [G("O", rect([60, 300], [0, -150]), stroke(INK, 2))], [1700, 790], b0 + 0.8, D - 0.6))
    L.append(src("Src Index", "SOURCE: INDEXBOX 2024; SRI LANKA EDB", b0 + 0.8, D - 0.6))
    L.append(disc("Island", list(sl), 30, TEA, r0 + 1.6, D - 0.6, sh=0, scale=grow(r0 + 1.6)))
    L.append(shape("Route Back", [G("R", arc(sl, mx, 0.2), trim(0, A(K(back, 0), K(back + 1.2, 100))), stroke(MX, 4))], [0, 0], back, D - 0.6))
    L.append(shape("Route", [G("R", path([mx, sl]), trim(A(K(0.2, 28.4), K(r0, 0)), A(K(0.2, 72.9), K(r0, 100))), stroke(CIN, 8))], [0, 0], 0.2, D - 0.6))
    L.append(shape("Stick", STICK, list(C), 0, 0.4))
    land = land_layer("World", WK, 0.2, D - 0.6, position=[WO[0] - WC[0] * WK, WO[1] + WC[1] * WK])
    L.append(land)
    for l in L:
        if l["name"] != "CDMX Dot":
            l["out"] = min(l["out"], D - 0.6)
    return finish(L, D)


# =====================================================================
# SCENE 9 - COFFEE STAYING HOME (28 s)
# =====================================================================
def pin(name, pos, t0, t1):
    return shape(name, [G("Tag", rect([14, 10], [16, -14]), fill(MX)), G("Cup", ell([28, 28]), stroke(INK, 3), fill(WHITE))], list(pos), t0, t1, scale=grow(t0, 100, 0.25))


def s9_specialty(D):
    L = []
    mx = wpt(CDMX)
    b0, c0, d0 = 8.0, 15.0, 23.0
    rnd = random.Random(9)
    for j in range(14):
        t = 1.0 + j * 0.4
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.15, 0.95)
        L.append(pin(f"Pin {j + 2}", (CX + 420 * r * math.cos(a), CY + 270 * r * math.sin(a)), t, c0))
    L.append(pin("Pin 1", mx, 0, c0))
    grid = [path([(x, 140), (x, 940)]) for x in range(300, 1700, 80)] + [path([(240, y), (1680, y)]) for y in range(160, 940, 80)]
    L.append(shape("Ring Road", [G("R", ell([1000, 660], [CX, CY])), stroke(GREY, 5)], [0, 0], 0.2, c0))
    L[-1]["shapes"] = [G("R", ell([1000, 660], [CX, CY]), stroke(GREY, 5))]
    L.append(shape("Streets", [G("S", *grid, stroke(LINE, 2))], [0, 0], 0.2, c0))
    # B: the coyote leaves, a roaster arrives
    ins = (1640, 820)
    L.append(caps("Inset Label", "CHIAPAS", [ins[0], ins[1] - 90], b0, c0, size=12, color=INK))
    L.append(truck("Coyote", [ins[0] - 40, ins[1] + 20], b0, b0 + 2.0, s=60, position=A(K(b0 + 0.4, [ins[0] - 40, ins[1] + 20]), K(b0 + 2.0, [ins[0] + 300, ins[1] + 20]))))
    L.append(tag("Roaster Label", "ROASTS AT THE FARM", [ins[0], ins[1] + 75], b0 + 2.4, c0, size=11))
    L.append(disc("Roaster", [ins[0], ins[1] + 10], 50, WHITE, b0 + 2.2, c0, sh=0, line=INK, scale=grow(b0 + 2.2)))
    L.append(shape("Farm Line", [G("L", path([(ins[0] - 60, ins[1]), (1280, 640)]), trim(0, A(K(b0 + 3.0, 0), K(b0 + 4.0, 100))), stroke(MX, 3, dashes=(10, 8)))],
                   [0, 0], b0 + 3.0, c0))
    L.append(shape("Inset", [G("I", rect([240, 180], list(ins), 8), stroke(INK, 3), fill(WHITE))], [0, 0], b0 - 0.2, c0))
    for l in L:
        add_out(l, min(l["out"], c0))
    # C: the cup row again; the empty four fill green
    L.append(tag("RG", "≈ 1.34 M BAGS ROASTED AND GROUND, OF ≈ 3.16 M DRUNK", [CX, 650], c0 + 2.4, d0, size=14))
    L.append(src("Src USDA RG", "SOURCE: USDA FAS MX2026-0026", c0 + 2.4, d0))
    row = cups_row(c0, d0, green_t=c0 + 1.2)
    for l in row:
        l["transform"]["scale"] = grow(c0 + 0.05 * row.index(l))
    L += row
    for l in L:
        add_out(l, min(l["out"], d0))
    L.insert(0, bag10(d0, D, position=A(K(d0, list(ROW[9])), K(d0 + 1.6, list(BAG10))), scale=A(K(d0, [30, 30]), K(d0 + 1.6, [100, 100]))))
    return finish(L, D)


def bag10(t0, t1, **tr):
    return shape("Bag", [G("Tag", rect([60, 30], [100, -60]), stroke(INK, 2), fill(MX)),
                         G("Crimp", rect([180, 22], [0, -119]), stroke(INK, 4)),
                         G("B", rect([180, 260], None, 8), stroke(INK, 4), fill(WHITE))], list(BAG10), t0, t1, **tr)


# =====================================================================
# SCENE 10 - CLOSE (17 s)
# =====================================================================
def s10_close(D):
    L = []
    e0 = 7.0
    L += wipe_text("End Title", "Café de Olla and the Instant Nation", [CX, 960], 60, INK, e0, D)
    L.append(word_marker("End Swipe", "Café de Olla and the Instant Nation", "Instant", CX, 960, 60, e0 + 0.8, D))
    L.append(caps("Stencil 1", "COATEPEC", [BAG10[0], BAG10[1] - 10], 1.6, D, size=16, color=INK))
    L.append(caps("Stencil 2", "ESTRICTAMENTE", [BAG10[0], BAG10[1] + 24], 2.0, D, size=11, color=INK))
    L.append(caps("Stencil 3", "ALTURA", [BAG10[0], BAG10[1] + 44], 2.2, D, size=11, color=INK))
    L.append(bag10(0, D))
    L.append(jar("Jar", list(JAR), 0, D))
    L += kitchen(0, D, picked=3.6)
    for l in L:
        if l["name"] in ("Table", "Hill"):
            l["shapes"][0]["items"] = [i for i in l["shapes"][0]["items"] if i["type"] != "trim"]
        if l["name"].startswith("Tree"):
            l["transform"]["scale"] = [100, 100]
            l["in"] = 0
    return finish(L, D)


SCENES = [("S1_Jar", 21.0, s1_jar), ("S2_Cups", 14.0, s2_cups), ("S3_Export", 26.0, s3_export), ("S4_Nescafe", 23.0, s4_nescafe),
          ("S5_Soluble", 45.0, s5_soluble), ("S6_Imports", 30.0, s6_imports), ("S7_Olla", 36.0, s7_olla), ("S8_Cinnamon", 17.0, s8_cinnamon),
          ("S9_Specialty", 28.0, s9_specialty), ("S10_Close", 17.0, s10_close)]

if __name__ == "__main__":
    write(SCENES, "Cafe_de_Olla", "10_cafe_de_olla", beats=True)
