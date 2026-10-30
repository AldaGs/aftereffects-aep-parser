# CLAUDE.md

Guide for agents building After Effects projects with this repo. The schema reference and copy-paste recipes are in [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) and [`docs/MOTION_SCHEMA.md`](docs/MOTION_SCHEMA.md). This file covers the workflow and the pitfalls that are not obvious from the schema.

## Repo map

- `cmd/json2jsx`: authoring JSON → ES3 `.jsx` (and, on Windows with AE installed, `-run` builds the `.aep`).
- `cmd/aep-parser`, `cmd/export2author`: binary `.aep` → raw JSON → authoring JSON. Real projects to study are in `aep/` (parsed exports in `aep/out/`).
- `schema/motion.schema.json`: the authoring format. Keep it in sync when `json2jsx` gains a field.
- `schema/examples/`: examples. `espresso_explainer.py` is the reference for a large, generated piece.

```bash
go build ./... && go test ./...
go run ./cmd/json2jsx -i schema/examples/<name>.json        # writes <name>.jsx next to it
python schema/examples/espresso_explainer.py                 # regenerate the espresso JSON
```

## Workflow for a video

1. **Get a brief before building.** You need purpose and audience, length, aspect ratio, fps, VO or not, style references (palette, fonts the user has installed), must-include content, how much on-screen text, the AE version and the save folder. Ask for whatever is missing. A vague brief gets a generic slideshow.
2. **Script and storyboard first.** Write timecoded beats (VO line + visual), and get approval for anything longer than a few seconds. Keep the script next to the example (`<name>_script.md`).
3. **Generate; don't hand-write.** Anything past a few dozen layers should be a Python generator committed as `schema/examples/<name>.py`. It should hold the palette, keyframe/shape helpers, one function per scene and a `build()`. Never hand-edit the generated JSON; change the generator and regenerate.
4. **One precomp per scene.** The master comp holds the scene precomps (`startTime`/`in`/`out`), transitions and grain. This lets the user retime to the VO by dragging layers.
5. **Compile and check** (see Verification), then commit generator, JSON, JSX and script together.

## Pitfalls (each one has broken a build or a frame)

**Coordinates and stacking**
- `layers[0]` is the top layer. Inside a shape group, items listed first draw on top, and a `fill`/`stroke` applies to every path *above* it in the same group. Write groups as `[paths..., stroke, fill]` for an outlined shape.
- Shape layers default to position = comp centre with anchor `[0, 0]`. Either keep shape items at `[0, 0]` and place the layer, or set the layer to `[0, 0]` and draw in comp coordinates (good for pipes and paths). Don't mix the two.
- Point text `position` is the baseline. `"\r"` separates lines and `leading` sets line height. Box text (`boxSize`) is positioned by its top-left corner.
- Null layers default to anchor `[50, 50]`. Always set `anchorPoint` on nulls. A camera rig is a null with `anchorPoint` = `position` = comp centre, so children keep their comp coordinates and scale pivots on the centre.
- Parenting uses `setParentWithJump`, so a child's values are in the parent's space (relative to the parent's anchor), and it happens after all layers exist. Parent names must match exactly (no error if they don't; the layer just isn't parented).
- **Opacity is not inherited through parenting.** To fade a group, fade its precomp layer or each layer.
- Precomps have transparent backgrounds. Give each scene a full-frame background *shape layer* (a `rect` larger than the frame). `"type": "solid"` layers are always 50 % grey unless sourced from a solid asset.

**Keyframes and expressions**
- `"easeIn"`, `"easeOut"` and `"easeInOut"` all produce the **same** 75 % ease, applied to **both sides** of that key. For real ease-out motion use a custom object, e.g. `{"inInfluence": 85, "outInfluence": 10, "inSpeed": 0, "outSpeed": 0}` (leaves fast, lands soft). Keys with no `ease` stay linear. Hold keys use `"interp": "hold"`, not `ease`.
- Position keys default to AE's **auto-bezier spatial** interpolation. Three or more keys that aren't collinear curve, and a hold between two equal keys makes the layer drift in a little loop. Add `"inTangent": [0, 0], "outTangent": [0, 0]` to position keys for straight paths (the espresso generator's `zero_tangents()` does it for all of them).
- An `expression` without a `value` leaves the property at AE's default. For a shape or text layer `position` that is the comp centre, so `value[0]` in the expression points there. Give `"value"` alongside `"expression"`.
- Use the JavaScript expression engine (`"expressionEngine": "javascript-1.0"`) and write vector maths per component (`[value[0] + x, value[1]]`), not `value + [x, 0]`.
- Loops belong in expressions (`time % period`), not in hundreds of keyframes. They keep the JSX small.

**Build and environment**
- An effect `matchName` that AE doesn't know **aborts the whole build** (`addProperty` isn't wrapped in `try`). Property values are set inside `try` and fail silently, so double-check effect names (`"ADBE Noise"`, `"ADBE Gaussian Blur 2"`, `"ADBE Drop Shadow"`).
- Text is escaped to `\uXXXX` by `json2jsx`, so `°`, `₂` and accents are fine. Fonts are PostScript names and must be installed on the user's machine. `ArialMT`, `Arial-BoldMT`, `Georgia` and `Georgia-Bold` are safe on Windows and macOS.
- `json2jsx` bakes an **absolute `.aep` save path** into the `.jsx`. Built in the cloud, that path is Linux; the user should regenerate on their machine, or pass `-aep` with their path.
- ExtendScript gets slow on very large scripts (the espresso JSX is ~2.7 MB, 450 layers). If a build stalls, split into one JSON/JSX per scene.
- There is no After Effects in the cloud container, so `-run` and `scripts/roundtrip.ps1` only work on the user's Windows machine. Ask the user to run the build and paste `ae_error.log` (written next to the `.aep`) if it fails.

## Verification without After Effects

- Generator self-checks: unique layer names per comp, and every `parent` resolves (see `build()` in `espresso_explainer.py`).
- Every layer has `out > in`, and comp names referenced by precomp layers exist.
- The JSX at least parses: `node -e "new Function(require('fs').readFileSync('x.jsx','utf8'))"`.
- For anything visual, render frames and look at them before handing off. Overlaps, wrong stacking and lost positions only show up on screen.
