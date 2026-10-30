# aftereffects-aep-parser & Motion Authoring Pipeline

A bidirectional toolkit for **parsing binary Adobe After Effects (`.aep`) project files** and **authoring new native `.aep` projects from a clean, agent-friendly JSON schema**.

It bridges static binary `.aep` analysis (via RIFX/Egg! chunk parsing in Go) with automated ExtendScript (`.jsx`) code generation so both humans and AI agents can inspect, modify, and generate complete After Effects motion graphics projects without manual keyframing.

---

## Architecture & Pipeline

```
  ┌─────────────────┐       aep-parser        ┌──────────────────────┐
  │   Native .AEP   │ ──────────────────────► │   Raw Parser JSON    │
  │  (RIFX Binary)  │                         │ (Full Property Tree) │
  └────────▲────────┘                         └──────────┬───────────┘
           │                                             │
   AfterFX.com -r                                 export2author
   (Saves & Opens)                                       │
           │                                             ▼
  ┌────────┴────────┐        json2jsx         ┌──────────────────────┐
  │  ExtendScript   │ ◄────────────────────── │   Authoring JSON     │
  │   (.jsx ES3)    │                         │ (motion.schema.json) │
  └─────────────────┘                         └──────────────────────┘
```

### Why `JSON -> JSX -> AEP`?
1. **Single-Shot Declarative Authoring**: Instead of executing 100+ sequential imperative tool calls to create layers, shapes, and keyframes, an agent or developer writes a single declarative JSON file (`schema/motion.schema.json`) and compiles the entire timeline in milliseconds.
2. **Offline Binary Inspection**: `aep-parser` reads `.aep` files directly from disk in `<50ms` without launching After Effects.
3. **Shields Against ExtendScript Pitfalls**: `json2jsx` automatically handles ES3 compatibility, reverse layer creation order (`addShape`/`addText` prepending at index 1), 1D/2D/3D `KeyframeEase` array dimensionality, two-pass parenting/track mattes, and safe undo-group/save/open lifecycle management.

---

## Repository Structure

| Path | Description |
| :--- | :--- |
| [`cmd/aep-parser/main.go`](cmd/aep-parser/main.go) | CLI that parses a binary `.aep` file into a comprehensive raw JSON tree (compositions, layers, transforms, shapes, text, masks, effects, keyframes, expressions). |
| [`cmd/export2author/main.go`](cmd/export2author/main.go) | CLI that converts a raw `aep-parser` JSON export into the concise, human/agent-editable authoring JSON format. |
| [`cmd/json2jsx/main.go`](cmd/json2jsx/main.go) | CLI that compiles an authoring JSON file into an ES3-compatible `.jsx` ExtendScript, and optionally executes After Effects to build, save, and open the `.aep`. |
| [`schema/motion.schema.json`](schema/motion.schema.json) | JSON Schema (Draft-07) defining the authoring format. |
| [`schema/examples/`](schema/examples/) | Ready-to-run authoring JSON examples (`explainer_video.json`, `espresso_explainer.json`, `agent_showcase.json`, `title_card.json`, `lower_third.json`, `shape_loop.json`) and their generated `.jsx` scripts. |
| [`scripts/fig2json.js`](scripts/fig2json.js) | Node script that converts a Figma `.fig` file into authoring JSON (one file per comp), ready for `json2jsx`. |
| [`scripts/roundtrip.ps1`](scripts/roundtrip.ps1) | Automated PowerShell test harness that compiles JSON -> JSX -> AEP, parses the resulting `.aep` back with `aep-parser`, and verifies layer/keyframe fidelity. |
| [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) | Complete reference guide and coordinate rules for AI agents authoring or modifying motion graphics. |
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | Detailed architectural specification of the binary parser and authoring pipeline. |

---

## Building the CLI Tools

Requires **Go 1.17+**:

```powershell
# Build all three CLI binaries
go build -o aep-parser.exe ./cmd/aep-parser
go build -o export2author.exe ./cmd/export2author
go build -o json2jsx.exe ./cmd/json2jsx

# Run Go unit tests
go test -v ./...
```

---

## Usage Guide (For Humans & AI Agents)

> **For AI Agents**: Always read [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) before authoring or editing motion JSON files.

### Workflow 1: Create a New After Effects Project from JSON

1. **Write an authoring JSON file** following [`schema/motion.schema.json`](schema/motion.schema.json) (see [`schema/examples/explainer_video.json`](schema/examples/explainer_video.json) for a full 3-scene example).
2. **Compile to `.jsx` (and optionally build & open the `.aep` in After Effects)**:

```powershell
# Generate only the ExtendScript (.jsx)
.\json2jsx.exe -i schema/examples/explainer_video.json

# Generate .jsx, run After Effects to build the .aep, and open the .aep in After Effects GUI
.\json2jsx.exe -i schema/examples/explainer_video.json -run

# Build the .aep headlessly and close After Effects when finished (for batch/CI pipelines)
.\json2jsx.exe -i schema/examples/explainer_video.json -aep schema/examples/explainer_video.aep -run -close
```

You can also run any generated `.jsx` manually inside After Effects via **File -> Scripts -> Run Script File...**. When the script finishes, it automatically saves the `.aep` file and opens the main composition in the viewer.

---

### Workflow 2: Inspect or Modify an Existing `.aep` File

1. **Parse the binary `.aep` to raw JSON** (does not require After Effects to be installed):
   ```powershell
   .\aep-parser.exe -i aep/TOP5.aep -o aep/out/TOP5.json
   ```
2. **Convert the raw JSON into the clean Authoring JSON format**:
   ```powershell
   .\export2author.exe -i aep/out/TOP5.json -o temp/TOP5_authoring.json
   ```
3. **Edit `temp/TOP5_authoring.json`** (change text strings, colors, layer timing, or keyframes).
4. **Rebuild and open the modified `.aep` in After Effects**:
   ```powershell
   .\json2jsx.exe -i temp/TOP5_authoring.json -aep temp/TOP5_rebuilt.aep -run
   ```

---

### Workflow 3: Automated Round-Trip Verification

To verify that authoring JSONs compile cleanly into `.aep` files and parse back with matching compositions, layers, text, and keyframes:

```powershell
# Run full round-trip verification on all examples (requires After Effects installed)
powershell -ExecutionPolicy Bypass -File scripts\roundtrip.ps1 -All

# Verify using existing pre-built .aep files without launching After Effects
powershell -ExecutionPolicy Bypass -File scripts\roundtrip.ps1 -All -SkipBuild
```

---

### Workflow 4: Import a Figma File

`scripts/fig2json.js` reads a local `.fig` file (a zip archive) and turns every top-level frame at least 1000px wide into a composition. It needs Node 22+ and a one-time `npm install`.

```powershell
npm install
Expand-Archive design.fig -DestinationPath figdir   # or: unzip design.fig -d figdir
node scripts/fig2json.js figdir out "^Page Name$"   # page filter is a regex; omit it for every page
```

This writes `out/project.json`, `out/images/*` and `out/comps/NN.json`, one comp per file. ExtendScript handles very large scripts poorly, so compile and run the comps one at a time. They all save into the same `.aep`:

```powershell
Get-ChildItem out\comps\*.json | ForEach-Object { .\json2jsx.exe -i $_.FullName -aep out\project.aep }
# then in After Effects: File > Scripts > Run Script File, on each out\comps\NN.jsx in order
```

| Figma | After Effects |
| :--- | :--- |
| Rectangles, ellipses, vectors, booleans, frame fills, strokes | Shape layers built from Figma's own path geometry |
| Text | Paragraph (box) text with font, size, color, tracking, line height, paragraph spacing, alignment, upper/lower case and per-character style runs |
| Image fills (fill, fit, crop) | Footage layers with a mask in the shape's own outline |
| Frames that clip their content | A hidden shape layer used as an alpha track matte for everything inside |
| Component instances | The main component's contents |

**Not converted yet:** drop shadows and blurs, blend modes, Figma masks, underline and title case, edits made to one copy of a component, and clipping by more than one nested frame (only the innermost frame clips). Gradients become their first color. Fonts must be installed locally.

---

## Critical Rules for Authoring Motion JSON (Agent Checklist)

When generating or modifying authoring JSON files, follow these rules to prevent visual misalignment or After Effects errors:

1. **Shape Layer Positioning (Avoid Double-Offset!)**:
   - In After Effects, `comp.layers.addShape()` creates a Shape Layer whose `transform.position` defaults to the center of the composition (`[width/2, height/2]`, e.g., `[960, 540]`) and whose `anchorPoint` is `[0, 0]`.
   - **Rule**: Always leave internal vector shape positions (`rect.position`, `ellipse.position`) at `[0, 0]` (omit `"position"` on the shape item) and place the shape on screen using the layer's `"transform": { "position": [X, Y] }`.
   - Setting both `layer.transform.position` and `rect.position` will double-offset the shape into the bottom-right corner outside the composition bounds.
2. **Text Baseline vs. Shape Center Alignment**:
   - Point text (`addText`) has its vertical origin (`Y`) at the **typographic baseline** (the bottom of capital letters), whereas a centered shape layer has its origin at its **geometric center**.
   - To visually center point text inside a pill/box shape at `Y_box`, place the text layer's `Y` at approximately `Y_box + (fontSize * 0.32)`.
   - Paragraph text (`"text": { "boxSize": [w, h] }`) instead has its origin at the **top-left of the box**, like a design tool. It also supports `leading`, `spaceAfter` and per-character `runs` (`{ "start", "end", "font", "fontSize", "fillColor", "tracking", "leading" }`; runs need AE 24.3+).
3. **Layer Ordering**:
   - List `compositions[].layers` from **top (foreground, index 0)** to **bottom (background, last index)**.
   - Place background solids last in the `layers` array, and place text layers *before* (above) their background highlight pills/cards.
4. **Colors & Timing**:
   - Colors can be hex strings (`"#7C3AED"`, `"#38BDF8"`) or normalized RGB arrays (`[0.22, 0.74, 0.97]`).
   - All layer times (`in`, `out`, `startTime`) and keyframe `time` values are in **seconds** (floating-point).
   - Ensure `out > in` for every layer.
5. **Supported Easing Presets**:
   - Keyframes support `"ease": "linear" | "easeIn" | "easeOut" | "easeInOut"` (`"interp": "hold"` for hold keys), or custom handles: `"ease": { "inInfluence": 85, "outInfluence": 10, "inSpeed": 0, "outSpeed": 0 }`. A low out-influence and a high in-influence give the snappy fast-out, slow-in motion-graphics feel.
   - AE's default auto-bezier makes a layer drift in a loop while "holding" between two equal position keys. Give such keys `"inTangent": [0, 0], "outTangent": [0, 0]` for straight motion paths.
6. **Styling & Structure**:
   - Strokes take `"lineCap": "butt" | "round" | "projecting"` and `"lineJoin": "miter" | "round" | "bevel"`.
   - Groups take a `"transform"` (`anchorPoint`, `position`, `scale`, `rotation`, `opacity`), so one shape layer can animate many parts.
   - `"enabled": false` hides a layer (guides, track matte sources).
   - Non-ASCII text such as `"93 °C"` is written as `\uXXXX` escapes, so it survives ExtendScript's file encoding.

---

## Minimal Authoring JSON Example

```json
{
  "$schema": "../motion.schema.json",
  "afterEffectsVersion": "24.0",
  "expressionEngine": "javascript-1.0",
  "bitDepth": "8bpc",
  "compositions": [
    {
      "name": "MainComp",
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "duration": 5.0,
      "backgroundColor": "#0B0F19",
      "layers": [
        {
          "name": "Headline",
          "type": "text",
          "in": 0,
          "out": 5,
          "text": {
            "string": "HELLO AFTER EFFECTS",
            "font": "Arial-BoldMT",
            "fontSize": 72,
            "fillColor": "#F8FAFC",
            "justification": "center"
          },
          "transform": {
            "position": [960, 563],
            "opacity": {
              "keyframes": [
                { "time": 0.0, "value": 0, "ease": "easeOut" },
                { "time": 0.6, "value": 100, "ease": "easeOut" }
              ]
            }
          }
        },
        {
          "name": "Highlight Pill",
          "type": "shape",
          "in": 0,
          "out": 5,
          "shapes": [
            {
              "type": "group",
              "name": "Pill",
              "items": [
                { "type": "rect", "size": [1000, 120], "roundness": 24 },
                { "type": "fill", "color": "#7C3AED", "opacity": 100 }
              ]
            }
          ],
          "transform": {
            "position": [960, 540],
            "scale": {
              "keyframes": [
                { "time": 0.0, "value": [0, 100], "ease": "easeOut" },
                { "time": 0.5, "value": [100, 100], "ease": "easeOut" }
              ]
            }
          }
        }
      ]
    }
  ]
}
```

---

## Go Library Usage (Binary `.aep` Parser)

You can also use the root package directly in Go to inspect `.aep` files programmatically:

```go
package main

import (
	"fmt"
	aep "github.com/boltframe/aftereffects-aep-parser"
)

func main() {
	project, err := aep.Open("./my-project.aep")
	if err != nil {
		panic(err)
	}
	fmt.Printf("Expression Engine: %s, Items: %d\n", project.ExpressionEngine, len(project.Items))
}
```

---

## RIFX Binary Format Notes

After Effects Project (`.aep`) files are encoded using the Resource Interchange File Format in Big-Endian byte-ordering (`RIFX....Egg!`). Key parsed chunks include:
- `cdta`: Composition metadata (resolution, framerate, duration, background color)
- `idta` / `fdta`: Item and folder descriptors (`ItemType`, IDs, solids, footage)
- `ldta`: Layer descriptors (layer type, 3D/adjustment/motion-blur flags, blend modes, track mattes, parent index, in/out/start times)
- `tdgp` / `tdmn` / `tdbs` / `tdb4`: Property groups, match names (`ADBE Transform Group`, `ADBE Vector Shape - Rect`, etc.), static values, and expression strings (`Utf8`)
- `LIST:list` (`ldat` / `lhd3`): Keyframe tables (frame offsets, values, interpolation types, spatial tangents, and temporal ease speed/influence)
- ` btdk`: Embedded binary Font/TextDocument descriptors
