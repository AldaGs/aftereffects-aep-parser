#!/usr/bin/env python3
"""Experimental: authoring JSON -> .aep directly, with py-aep, no After Effects needed.

    pip install py-aep==0.19.0
    python scripts/json2aep.py schema/examples/title_card.json out.aep [--seed some.aep]

It mirrors cmd/json2jsx, but writes the binary project instead of an ExtendScript build.
py-aep cannot do everything our schema needs; every feature it skips is printed as a
warning, and the JSX path stays the reference build. Known gaps (py-aep 0.19.0):

- Effects: only effects whose definition is already in the project can be added. Pass
  --seed with an .aep saved by AE that uses them (save a tiny project in AE with Noise,
  Ramp, Gaussian Blur, ... applied once); the build starts from that project, so its
  items come along too.
- Stroke dashes cannot be created.
- Tested without AE: all schema/examples build (espresso, 450 layers, in ~7 s) and read
  back through py-aep with every key, expression and shape item intact (custom ease and
  zero tangents exact). Our Go parser reads them too. The writer is reverse-engineered, so
  open a file in AE before relying on it.
"""
import argparse
import json
import os
import sys

import py_aep
from py_aep import KeyframeEase, KeyframeInterpolationType as KIT

warnings = []


def warn(msg):
    warnings.append(msg)


def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def to_ae(value, rgba=False):
    if isinstance(value, str) and value.startswith("#"):
        c = hex_rgb(value)
        return c + [1] if rgba else c
    return value


def fit_dims(prop, value):
    """Pad/trim vectors to the property's dimension count (2D positions are 3D in AE)."""
    if not isinstance(value, list):
        return value
    try:
        cur = prop.value
    except Exception:
        return value
    if isinstance(cur, (list, tuple)) and len(cur) != len(value):
        if len(value) < len(cur):
            return list(value) + list(cur[len(value):])
        return list(value[:len(cur)])
    return value


def ease_pair(ease):
    """(in, out) KeyframeEase for a key, matching json2jsx's makeEase and custom objects."""
    if isinstance(ease, str):
        infl = 0.1 if ease == "linear" else 75 if ease in ("easeIn", "easeOut", "easeInOut") else 33.33
        e = KeyframeEase(0, infl)
        return e, e
    if isinstance(ease, dict):
        clamp = lambda v: max(0.1, min(100, v))
        return (KeyframeEase(ease.get("inSpeed", 0), clamp(ease.get("inInfluence", 33.33))),
                KeyframeEase(ease.get("outSpeed", 0), clamp(ease.get("outInfluence", 33.33))))
    return None


def n_ease_dims(prop):
    t = str(prop.property_value_type)
    if "SPATIAL" in t:
        return 1
    if "TwoD" in t:
        return 2
    if "ThreeD" in t:
        return 3
    return 1


def set_prop(prop, data, where, rgba=False):
    if data is None:
        return
    if prop is None:
        warn(f"{where}: property missing")
        return
    try:
        if not isinstance(data, dict):
            prop.value = fit_dims(prop, to_ae(data, rgba))
            return
        kfs = data.get("keyframes") or []
        if "value" in data and not kfs:
            prop.value = fit_dims(prop, to_ae(data["value"], rgba))
        if kfs:
            prop.set_values_at_times([k["time"] for k in kfs],
                                     [fit_dims(prop, to_ae(k["value"], rgba)) for k in kfs])
            keys = prop.keyframes
            for k, key in zip(kfs, keys):
                interp = k.get("interp")
                if interp in ("hold", "linear"):
                    t = KIT.HOLD if interp == "hold" else KIT.LINEAR
                    key.in_interpolation_type = t
                    key.out_interpolation_type = t
                elif k.get("ease") is not None:
                    pair = ease_pair(k["ease"])
                    if pair:
                        for n in (n_ease_dims(prop), 1, 2, 3):  # py-aep checks the count
                            try:
                                key.in_temporal_ease = [pair[0]] * n
                                key.out_temporal_ease = [pair[1]] * n
                                break
                            except ValueError:
                                continue
                if "inTangent" in k or "outTangent" in k:
                    for attr, kk in (("in_spatial_tangent", "inTangent"), ("out_spatial_tangent", "outTangent")):
                        if kk in k:
                            setattr(key, attr, fit_dims(prop, list(k[kk])) if len(k[kk]) < 3 else k[kk])
        if data.get("expression"):
            prop.expression = data["expression"]
    except Exception as e:
        warn(f"{where}: {type(e).__name__}: {e}")


SHAPE_PROPS = {
    "rect": ("ADBE Vector Shape - Rect", {"size": "ADBE Vector Rect Size", "position": "ADBE Vector Rect Position",
                                          "roundness": "ADBE Vector Rect Roundness"}),
    "ellipse": ("ADBE Vector Shape - Ellipse", {"size": "ADBE Vector Ellipse Size",
                                                "position": "ADBE Vector Ellipse Position"}),
    "fill": ("ADBE Vector Graphic - Fill", {"color": "ADBE Vector Fill Color", "opacity": "ADBE Vector Fill Opacity"}),
    "stroke": ("ADBE Vector Graphic - Stroke", {"color": "ADBE Vector Stroke Color",
                                                "strokeWidth": "ADBE Vector Stroke Width",
                                                "opacity": "ADBE Vector Stroke Opacity"}),
    "trim": ("ADBE Vector Filter - Trim", {"start": "ADBE Vector Trim Start", "end": "ADBE Vector Trim End",
                                           "offset": "ADBE Vector Trim Offset"}),
}
GROUP_XF = {"anchorPoint": "ADBE Vector Anchor", "position": "ADBE Vector Position", "scale": "ADBE Vector Scale",
            "rotation": "ADBE Vector Rotation", "opacity": "ADBE Vector Group Opacity"}


def make_shape(sh):
    s = py_aep.Shape()
    s.vertices = sh.get("vertices", [])
    n = len(s.vertices)
    s.in_tangents = sh.get("inTangents") or [[0, 0]] * n
    s.out_tangents = sh.get("outTangents") or [[0, 0]] * n
    s.closed = bool(sh.get("closed"))
    return s


def add_shape_item(contents, item, where):
    t = item.get("type")
    where = f"{where}/{item.get('name', t)}"
    try:
        if t in SHAPE_PROPS:
            match, props = SHAPE_PROPS[t]
            p = contents.add_property(match)
            if item.get("name"):
                p.name = item["name"]
            for key, mn in props.items():
                set_prop(p.property(mn), item.get(key), f"{where}.{key}", rgba=key == "color")
            if t == "stroke":
                caps = {"butt": 1, "round": 2, "projecting": 3}
                joins = {"miter": 1, "round": 2, "bevel": 3}
                if item.get("lineCap") in caps:
                    set_prop(p.property("ADBE Vector Stroke Line Cap"), caps[item["lineCap"]], where)
                if item.get("lineJoin") in joins:
                    set_prop(p.property("ADBE Vector Stroke Line Join"), joins[item["lineJoin"]], where)
                if item.get("dashes"):
                    warn(f"{where}: stroke dashes not supported by py-aep (drawn solid)")
        elif t == "path":
            p = contents.add_property("ADBE Vector Shape - Group")
            if item.get("name"):
                p.name = item["name"]
            if item.get("path"):
                p.property("ADBE Vector Shape").value = make_shape(item["path"])
        elif t == "group":
            g = contents.add_property("ADBE Vector Group")
            if item.get("name"):
                g.name = item["name"]
            xf = g.property("ADBE Vector Transform Group")
            for key, mn in GROUP_XF.items():
                if key in (item.get("transform") or {}):
                    set_prop(xf.property(mn), item["transform"][key], f"{where}.{key}")
            inner = g.property("ADBE Vectors Group")
            for child in item.get("items", []):
                add_shape_item(inner, child, where)
        else:
            warn(f"{where}: shape type {t!r} not handled")
    except Exception as e:
        warn(f"{where}: {type(e).__name__}: {e}")


XF = {"position": "ADBE Position", "xPosition": "ADBE Position_0", "yPosition": "ADBE Position_1",
      "zPosition": "ADBE Position_2", "anchorPoint": "ADBE Anchor Point", "scale": "ADBE Scale",
      "rotation": "ADBE Rotate Z", "xRotation": "ADBE Rotate X", "yRotation": "ADBE Rotate Y",
      "zRotation": "ADBE Rotate Z", "orientation": "ADBE Orientation", "opacity": "ADBE Opacity"}
JUST = {"left": "LEFT_JUSTIFY", "center": "CENTER_JUSTIFY", "right": "RIGHT_JUSTIFY"}


def style_text(layer, t, where):
    prop = layer.property("ADBE Text Properties").property("ADBE Text Document")
    td = prop.value
    try:
        td.text = t.get("string", "")
        if t.get("font"):
            td.font = t["font"]
        if t.get("fontSize"):
            td.font_size = t["fontSize"]
        if t.get("fillColor"):
            td.fill_color = hex_rgb(t["fillColor"]) if isinstance(t["fillColor"], str) else t["fillColor"]
        if t.get("strokeColor"):
            td.stroke_color = hex_rgb(t["strokeColor"])
        for k, a in (("applyFill", "apply_fill"), ("applyStroke", "apply_stroke"), ("strokeWidth", "stroke_width"),
                     ("tracking", "tracking")):
            if t.get(k) is not None:
                setattr(td, a, t[k])
        if t.get("justification") in JUST:
            td.justification = getattr(py_aep.ParagraphJustification, JUST[t["justification"]])
        if t.get("leading"):
            td.auto_leading = False
            td.leading = t["leading"]
        if t.get("runs"):
            warn(f"{where}: text runs not applied")
        prop.value = td
    except Exception as e:
        warn(f"{where}: text: {type(e).__name__}: {e}")


def build(doc, out, seed=None):
    app = py_aep.parse(seed) if seed else py_aep.new()
    proj = app.project
    comps = {}
    for c in doc.get("compositions", []):
        comp = proj.root_folder.add_comp(c["name"], c["width"], c["height"], 1.0,
                                         c.get("duration") or 5.0, c.get("fps") or 24.0)
        if c.get("backgroundColor"):
            comp.bg_color = hex_rgb(c["backgroundColor"])
        comps[c["name"]] = comp

    for c in doc.get("compositions", []):
        comp = comps[c["name"]]
        made = {}
        for l in reversed(c.get("layers", [])):
            where = f"{c['name']}/{l.get('name')}"
            t = l.get("type")
            try:
                if t == "text":
                    tx = l.get("text") or {}
                    if len(tx.get("boxSize") or []) == 2:
                        L = comp.add_box_text(tx["boxSize"], tx.get("string", ""))
                    else:
                        L = comp.add_text(tx.get("string", ""))
                    style_text(L, tx, where)
                elif t == "shape":
                    L = comp.add_shape()
                    root = L.property("ADBE Root Vectors Group")
                    for item in l.get("shapes", []):
                        add_shape_item(root, item, where)
                elif t == "precomp" and l.get("source") in comps:
                    L = comp.add(comps[l["source"]])
                elif t in ("solid", "adjustment"):
                    L = comp.add_solid([1, 1, 1] if t == "adjustment" else [.5, .5, .5], l.get("name"),
                                       c["width"], c["height"], 1.0)
                    if t == "adjustment":
                        L.adjustment_layer = True
                elif t == "camera":
                    L = comp.add_camera(l.get("name"), [c["width"] / 2, c["height"] / 2])
                elif t == "light":
                    L = comp.add_light(l.get("name"), [c["width"] / 2, c["height"] / 2])
                else:
                    if t != "null":
                        warn(f"{where}: layer type {t!r} built as a null")
                    L = comp.add_null()
            except Exception as e:
                warn(f"{where}: create failed: {type(e).__name__}: {e}")
                continue
            L.name = l.get("name", L.name)
            made[l.get("name")] = L
            for flag, attr in (("threeD", "three_d_layer"), ("collapse", "collapse_transformation"),
                               ("motionBlur", "motion_blur"), ("adjustment", "adjustment_layer")):
                if l.get(flag):
                    try:
                        setattr(L, attr, True)
                    except Exception as e:
                        warn(f"{where}: {flag}: {e}")
            if l.get("enabled") is False:
                L.enabled = False
            for k, a in (("stretch", "stretch"), ("startTime", "start_time"), ("in", "in_point")):
                if l.get(k) is not None:
                    try:
                        setattr(L, a, l[k])
                    except Exception as e:
                        warn(f"{where}: {k}: {e}")
            if l.get("out") and l["out"] > L.in_point:
                L.out_point = l["out"]
            if l.get("blendMode"):
                warn(f"{where}: blendMode not applied")
            for m in l.get("masks", []):
                try:
                    mk = L.property("ADBE Mask Parade").add_property("ADBE Mask Atom")
                    if m.get("path"):
                        mk.property("ADBE Mask Shape").value = make_shape(m["path"])
                    set_prop(mk.property("ADBE Mask Opacity"), m.get("opacity"), where + ".mask")
                    set_prop(mk.property("ADBE Mask Feather"), m.get("feather"), where + ".mask")
                    mk.inverted = bool(m.get("inverted"))
                except Exception as e:
                    warn(f"{where}: mask: {e}")
            for fx in l.get("effects", []):
                try:
                    e = L.property("ADBE Effect Parade").add_property(fx["matchName"])
                    if fx.get("name"):
                        e.name = fx["name"]
                    for pn, pv in (fx.get("props") or {}).items():
                        set_prop(e.property(pn), pv, f"{where}.fx.{pn}")
                except Exception as e:
                    warn(f"{where}: effect {fx.get('matchName')} skipped ({e})")
            xf = L.property("ADBE Transform Group")
            for key, val in (l.get("transform") or {}).items():
                mn = XF.get(key)
                if key == "rotation" and l.get("threeD"):
                    mn = "ADBE Rotate Z"
                if not mn:
                    continue
                set_prop(xf.property(mn), val, f"{where}.{key}")
            if l.get("jsx"):
                warn(f"{where}: raw jsx escape hatch ignored")
            if l.get("trackMatte"):
                warn(f"{where}: track matte not applied")
        for l in c.get("layers", []):
            if l.get("parent"):
                ch, par = made.get(l.get("name")), made.get(l["parent"])
                if ch and par:
                    try:
                        ch.set_parent_with_jump(par)
                    except Exception as e:
                        warn(f"{c['name']}/{l['name']}: parent: {e}")
    if os.path.exists(out):
        os.remove(out)
    proj.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--seed", help="start from this .aep (for effect definitions)")
    a = ap.parse_args()
    build(json.load(open(a.input, encoding="utf-8")), a.output, a.seed)
    for w in warnings:
        print("WARN", w, file=sys.stderr)
    print(f"wrote {a.output} ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
