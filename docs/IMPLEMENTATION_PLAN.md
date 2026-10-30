# Implementation plan: AEP ⇄ JSON ⇄ After Effects

Goal: an agent writes a motion design as JSON, and we turn it into a real
`.aep`. We do this by generating an ExtendScript (`.jsx`) that After Effects runs
to build the project and save it. After Effects writes the binary, not us.

This file is the hand-off document. Each phase lists what is done, what is left,
and how to check the work. Update the status markers as you go.

Status legend: ✅ done · 🟡 partial / needs verification · ⬜ not started

---

## 0. Orientation (read first)

| Path | What it is |
|---|---|
| `project.go`, `item.go`, `layer.go`, `property.go` | Go library: parses the RIFX `.aep` into `Project → Item → Layer → Property` |
| `keyframe.go` | Values, keyframes, ease, spatial tangents, expressions (`tdbs` / `tdb4` / `cdat` / `lhd3` / `ldat`) |
| `path.go` | Bezier path values for shapes and masks (`om-s` blocks) |
| `textdoc.go`, `cos.go` | Text content and style (COS dictionaries in `btdk`) |
| `sourcelayer.go` | Layered PSD / AI footage info |
| `cmd/aep-parser/main.go` | CLI: `.aep` → JSON. The JSON export model is defined here |
| `aep/*.aep` | Real sample projects (inputs) |
| `aep/out/*.json` | Their JSON exports (regenerate, don't hand-edit) |
| `data/*.aep` | Small fixtures used by `go test` |

Build and test:

```powershell
go test ./...
go build -o aep-parser.exe .\cmd\aep-parser
# regenerate every sample:
Get-ChildItem aep\*.aep | % { .\aep-parser.exe $_.FullName (Join-Path aep\out ($_.BaseName + '.json')) }
```

Conventions:
- Binary layouts we rely on are commented at the read site with their source
  (e.g. "from py-aep's LdtaChunk (MIT)"). Keep doing that.
- Anything inferred rather than confirmed gets an `UNVERIFIED` comment and a
  line in §6.
- Files use CRLF. Don't run `gofmt -w` on files you aren't changing.

---

## Phase 1 — Regenerate exports ✅

All `aep/*.aep` are re-exported to `aep/out/` with the current parser.
`aep/out/NDIVEJULIO.json` has no source `.aep` in the repo, so it is stale.
Delete it or add its source.

## Phase 2 — Complete the layer data in the export 🟡

Exported per layer: `layerId`, `kind`, `parent` (ldta id) and `parentIndex`,
`blendMode`, `trackMatte`, `matteLayer` and `matteLayerIndex`, `startTime`,
`inPoint`, `duration`, `compInPoint`, `compOutPoint`, `flags`, `text` and
`textStyle`, `transform`, `effects`, `masks` (with paths), `contents`
(shapes with paths), `audio`, `markers`. Per footage item: `footageType`,
`solidColor`, `file`, `sourceLayer`.

Left to do:
- 🟡 **Out point semantics.** `compOutPoint = startTime + inPoint + duration`
  assumes the ldta "duration" runs from the in point. The sample data doesn't
  settle it (see §6). Confirm with Phase 5's round-trip, or one manual check
  in After Effects.
- ⬜ Time stretch (`stretch`), layer label color, and the `autoOrient` flag are
  not parsed.
- ⬜ Track matte for AE < 23 uses the layer directly above. `matteLayerIndex`
  is only set for AE ≥ 23 files. For older files, use `index - 1`.

## Phase 3 — Authoring schema (what agents write) ✅

The export JSON is faithful but verbose (match names, binary-only fields). It
makes good *examples*, but it's a poor *authoring format*.
- Defined `schema/motion.schema.json` (JSON Schema draft 2020-12) and documentation in `docs/MOTION_SCHEMA.md`.
- Readable property keys (`position`, `anchorPoint`, `scale`, `rotation`, `opacity`, etc.).
- Compositions, Assets, Layers (by type: `solid`, `text`, `shape`, `null`, `precomp`, `footage`, etc.).
- Clean animatable value specifications: constants or keyframe lists with `ease` (`easeIn`, `easeOut`, `easeInOut`, `linear`), interpolation (`bezier`, `linear`, `hold`), spatial tangents, and `expression`.
- Created 3 hand-written authoring examples in `schema/examples/`:
  - `title_card.json` (typography with tracking, stagger fade-in and scale animation)
  - `lower_third.json` (parenting, slide-in/out keyframing, ribbon shape)
  - `shape_loop.json` (trim paths, pulse scale, continuous rotation expression)
- Built `cmd/export2author` tool to convert raw AEP export JSONs into clean authoring JSONs. Verified on `KID - FRANCESCOLI ID - AG.json` -> `schema/examples/kid_authoring.json`. All 4 files validate cleanly.

## Phase 4 — `json2jsx` generator ✅

- Built command `cmd/json2jsx`: `json2jsx -i design.json [-o build.jsx] [-aep out.aep] [-run]`.
- Generates 100% **ES3-compatible** ExtendScript:
  - Supports all comp settings (dimensions, duration, framerate, background color, engine, bit depth).
  - Handles all layer types (`text`, `shape`, `solid`, `null`, `precomp`, `footage`, `camera`, `light`, `adjustment`).
  - Correct layer order (bottom-up creation so layer 0 in authoring JSON lands at top of AE stack).
  - Handles text document styling (`font`, `fontSize`, `fillColor`, `strokeColor`, `tracking`, `justification`).
  - Handles shape contents (rectangles, ellipses, fills, strokes, trim paths, bezier paths, groups).
  - Masks and effects with property bindings.
  - Transforms (2D/3D positions, scale, rotation, orientation, opacity) with static values or keyframe ease curves.
  - Post-creation resolution for layer `parent` references and track mattes (`setTrackMatte`).
  - Optional `jsx` escape hatch per layer.
  - Built-in `-run` flag automatically locates `AfterFX.com` on Windows and executes non-interactively to produce native `.aep` binary files.
- Successfully built `.aep` files for all 3 schema examples (`title_card.aep`, `lower_third.aep`, `shape_loop.aep`). Verified with `aep-parser.exe` round-trip.

## Phase 5 — Round-trip verification ✅ Done

Automated verification pipeline implemented in `scripts/roundtrip.ps1`:
- Supports both authoring JSON validation (`Authoring JSON -> AEP -> aep-parser -> JSON verification`) and native AEP round-tripping (`Native AEP -> aep-parser -> export2author -> JSX -> Rebuilt AEP -> aep-parser -> Diff`).
- Verifies composition dimensions (width, height, FPS, duration), layer counts and order, text styling & strings, parent layer relationships, and transform keyframes (timestamps & values within tolerance).
- Verified on all test suites (`title_card.json`, `lower_third.json`, `shape_loop.json` — 3/3 passed).

## Phase 6 — Agent hand-off docs ✅ Done

Created comprehensive developer & AI agent guide in `docs/AGENT_GUIDE.md`:
- Architecture walkthrough of the declarative motion pipeline.
- Quick start instructions and CLI usage (`json2jsx`, `aep-parser`, `export2author`, `roundtrip.ps1`).
- Complete property specification for comps, layers, transforms, shapes, and text.
- 6 ready-to-use motion recipes (smooth fades, slide-up text with track mattes, elastic bounce expressions, lower thirds with animated trim strokes, looping scale pulses, and parent rig setups).
- Guidance for LLM prompt engineering and motion generation rules.

---

## 6. Open questions / unverified

1. **ldta duration vs out point.** Across 599 layers in `WARM UP 6` that have a
   nonzero start or in point, `duration == comp length` (258) matches far more
   often than `start + in + duration == comp length` (117). This suggests the
   field may be an out point in layer time instead, which would make
   `compOutPoint = startTime + duration`. Not confirmed either way.
2. Interpolation byte values (1 linear, 2 bezier, 3 hold) are inferred from
   samples, not from a spec.
3. Scale and opacity are stored as 0–1 and scaled to 0–100 on export. Other
   percentage properties (shape fill opacity, etc.) were seen stored as 0–100
   already. Check each new property type before assuming.

