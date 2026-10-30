package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Motion Design Authoring Model Definitions (aligned with motion.schema.json)

type ProjectDoc struct {
	File             string           `json:"file,omitempty"`
	ExpressionEngine string           `json:"expressionEngine,omitempty"`
	BitDepth         string           `json:"bitDepth,omitempty"`
	Assets           []AssetDoc       `json:"assets,omitempty"`
	Compositions     []CompositionDoc `json:"compositions"`
}

type AssetDoc struct {
	ID         string      `json:"id"`
	Name       string      `json:"name,omitempty"`
	Type       string      `json:"type"` // "file", "solid", "placeholder"
	File       string      `json:"file,omitempty"`
	Width      int         `json:"width,omitempty"`
	Height     int         `json:"height,omitempty"`
	SolidColor interface{} `json:"solidColor,omitempty"` // hex or [r,g,b]
}

type CompositionDoc struct {
	Name            string     `json:"name"`
	Width           int        `json:"width"`
	Height          int        `json:"height"`
	FPS             float64    `json:"fps,omitempty"`
	Duration        float64    `json:"duration"`
	BackgroundColor string     `json:"backgroundColor,omitempty"`
	Layers          []LayerDoc `json:"layers,omitempty"`
}

type LayerDoc struct {
	Name       string                 `json:"name"`
	Type       string                 `json:"type"` // "solid", "text", "shape", "null", "precomp", "footage", etc.
	Source     string                 `json:"source,omitempty"`
	Parent     string                 `json:"parent,omitempty"`
	ThreeD     bool                   `json:"threeD,omitempty"`
	Collapse   bool                   `json:"collapse,omitempty"`
	MotionBlur bool                   `json:"motionBlur,omitempty"`
	Adjustment bool                   `json:"adjustment,omitempty"`
	In         *float64               `json:"in,omitempty"`
	Out        *float64               `json:"out,omitempty"`
	StartTime  *float64               `json:"startTime,omitempty"`
	BlendMode  string                 `json:"blendMode,omitempty"`
	TrackMatte *TrackMatteDoc         `json:"trackMatte,omitempty"`
	Transform  map[string]interface{} `json:"transform,omitempty"`
	Text       *TextDoc               `json:"text,omitempty"`
	Shapes     []ShapeItemDoc         `json:"shapes,omitempty"`
	Masks      []MaskDoc              `json:"masks,omitempty"`
	Effects    []EffectDoc            `json:"effects,omitempty"`
	JSX        string                 `json:"jsx,omitempty"`
	Enabled    *bool                  `json:"enabled,omitempty"` // false hides the layer (guides, track mattes)
}

type TrackMatteDoc struct {
	Target string `json:"target"`
	Type   string `json:"type"` // "Alpha", "Alpha Inverted", "Luma", "Luma Inverted"
}

type TextDoc struct {
	String        string      `json:"string"`
	Font          string      `json:"font,omitempty"`
	FontSize      float64     `json:"fontSize,omitempty"`
	FillColor     interface{} `json:"fillColor,omitempty"`
	StrokeColor   interface{} `json:"strokeColor,omitempty"`
	StrokeWidth   float64     `json:"strokeWidth,omitempty"`
	ApplyFill     *bool       `json:"applyFill,omitempty"`
	ApplyStroke   *bool       `json:"applyStroke,omitempty"`
	Tracking      float64     `json:"tracking,omitempty"`
	Justification string      `json:"justification,omitempty"`
	BoxSize       []float64   `json:"boxSize,omitempty"`    // [w, h] -> paragraph (box) text, origin at box top-left
	Leading       float64     `json:"leading,omitempty"`    // line height in px; 0 = auto
	SpaceAfter    float64     `json:"spaceAfter,omitempty"` // paragraph spacing in px
	Runs          []TextRun   `json:"runs,omitempty"`       // per-character style overrides
}

type TextRun struct {
	Start     int         `json:"start"`
	End       int         `json:"end"` // exclusive
	Font      string      `json:"font,omitempty"`
	FontSize  float64     `json:"fontSize,omitempty"`
	FillColor interface{} `json:"fillColor,omitempty"`
	Tracking  *float64    `json:"tracking,omitempty"`
	Leading   float64     `json:"leading,omitempty"`
}

type ShapeItemDoc struct {
	Name        string                 `json:"name,omitempty"`
	Type        string                 `json:"type"` // "rect", "ellipse", "path", "fill", "stroke", "trim", "group"
	Size        interface{}            `json:"size,omitempty"`
	Position    interface{}            `json:"position,omitempty"`
	Roundness   interface{}            `json:"roundness,omitempty"`
	Color       interface{}            `json:"color,omitempty"`
	Opacity     interface{}            `json:"opacity,omitempty"`
	StrokeWidth interface{}            `json:"strokeWidth,omitempty"`
	LineCap     string                 `json:"lineCap,omitempty"`  // "butt", "round", "projecting"
	LineJoin    string                 `json:"lineJoin,omitempty"` // "miter", "round", "bevel"
	Start       interface{}            `json:"start,omitempty"`
	End         interface{}            `json:"end,omitempty"`
	Offset      interface{}            `json:"offset,omitempty"`
	Path        *BezierPathDoc         `json:"path,omitempty"`
	Items       []ShapeItemDoc         `json:"items,omitempty"`
	Transform   map[string]interface{} `json:"transform,omitempty"`
}

type MaskDoc struct {
	Name      string         `json:"name,omitempty"`
	Mode      string         `json:"mode,omitempty"` // "Add", "Subtract", etc.
	Inverted  bool           `json:"inverted,omitempty"`
	Path      *BezierPathDoc `json:"path,omitempty"`
	Opacity   interface{}    `json:"opacity,omitempty"`
	Feather   interface{}    `json:"feather,omitempty"`
	Expansion interface{}    `json:"expansion,omitempty"`
}

type BezierPathDoc struct {
	Closed      bool         `json:"closed"`
	Vertices    [][2]float64 `json:"vertices"`
	InTangents  [][2]float64 `json:"inTangents,omitempty"`
	OutTangents [][2]float64 `json:"outTangents,omitempty"`
}

type EffectDoc struct {
	Name      string                 `json:"name,omitempty"`
	MatchName string                 `json:"matchName"`
	Props     map[string]interface{} `json:"props,omitempty"`
}

type AnimValueDoc struct {
	Value      interface{}   `json:"value,omitempty"`
	Expression string        `json:"expression,omitempty"`
	Keyframes  []KeyframeDoc `json:"keyframes,omitempty"`
}

type KeyframeDoc struct {
	Time       float64     `json:"time"`
	Value      interface{} `json:"value"`
	Interp     string      `json:"interp,omitempty"` // "linear", "bezier", "hold"
	Ease       interface{} `json:"ease,omitempty"`   // string preset or custom object
	InTangent  []float64   `json:"inTangent,omitempty"`
	OutTangent []float64   `json:"outTangent,omitempty"`
}

// Code generation state
type Generator struct {
	sb strings.Builder
}

func (g *Generator) write(format string, a ...interface{}) {
	g.sb.WriteString(fmt.Sprintf(format, a...))
	g.sb.WriteString("\n")
}

func main() {
	inPath := flag.String("i", "", "input authoring JSON file")
	outPath := flag.String("o", "", "output ExtendScript (.jsx) file")
	aepPath := flag.String("aep", "", "target .aep file path to save")
	runAE := flag.Bool("run", false, "execute AfterFX.com to build and open the .aep")
	closeOnComplete := flag.Bool("close", false, "close After Effects after running the script")
	timeout := flag.Duration("timeout", 5*time.Minute, "max time to wait for After Effects to save the .aep")
	flag.Parse()

	if *inPath == "" {
		fmt.Fprintln(os.Stderr, "Usage: json2jsx -i <design.json> [-o <build.jsx>] [-aep <out.aep>] [-run] [-close]")
		flag.PrintDefaults()
		os.Exit(1)
	}

	data, err := os.ReadFile(*inPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", *inPath, err)
		os.Exit(1)
	}

	var proj ProjectDoc
	if err := json.Unmarshal(data, &proj); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	targetAEP := *aepPath
	if targetAEP == "" && proj.File != "" {
		targetAEP = filepath.Join(filepath.Dir(*inPath), filepath.Base(proj.File))
	}
	if targetAEP == "" {
		base := strings.TrimSuffix(filepath.Base(*inPath), filepath.Ext(*inPath))
		targetAEP = filepath.Join(filepath.Dir(*inPath), base+".aep")
	}
	if targetAEP != "" {
		absAEP, err := filepath.Abs(targetAEP)
		if err == nil {
			targetAEP = absAEP
		}
	}

	shouldClose := *closeOnComplete
	jsxCode, err := GenerateJSX(&proj, targetAEP, shouldClose)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error generating JSX: %v\n", err)
		os.Exit(1)
	}

	targetJSX := *outPath
	if targetJSX == "" {
		base := strings.TrimSuffix(filepath.Base(*inPath), filepath.Ext(*inPath))
		targetJSX = filepath.Join(filepath.Dir(*inPath), base+".jsx")
	}

	if err := os.WriteFile(targetJSX, []byte(jsxCode), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing JSX to %s: %v\n", targetJSX, err)
		os.Exit(1)
	}
	fmt.Printf("Generated ExtendScript: %s\n", targetJSX)

	if *runAE {
		aePath, err := findAfterEffectsCLI()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Cannot run After Effects: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Running After Effects CLI: %s\n", aePath)
		absJSX, _ := filepath.Abs(targetJSX)
		cmd := exec.Command(aePath, "-r", absJSX)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		start := time.Now().Add(-2 * time.Second) // allow for coarse filesystem mtimes
		var errLog string
		if targetAEP != "" {
			errLog = filepath.Join(filepath.Dir(targetAEP), "ae_error.log")
			_ = os.Remove(errLog)
		}
		if err := cmd.Start(); err != nil {
			fmt.Fprintf(os.Stderr, "After Effects execution failed: %v\n", err)
			os.Exit(1)
		}
		done := make(chan error, 1)
		go func() { done <- cmd.Wait() }()
		if targetAEP == "" {
			if err := <-done; err != nil {
				fmt.Fprintf(os.Stderr, "After Effects execution failed: %v\n", err)
				os.Exit(1)
			}
			fmt.Println("After Effects script executed successfully.")
			return
		}
		// AfterFX.com returns early when it hands the script to an already-running
		// After Effects, and can hang after app.quit(), so poll for the saved .aep
		// instead of trusting the process exit.
		if err := waitForAEP(targetAEP, errLog, start, *timeout); err != nil {
			_ = cmd.Process.Kill()
			fmt.Fprintf(os.Stderr, "%v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Successfully created AEP: %s\n", targetAEP)
		if shouldClose {
			select {
			case <-done:
			case <-time.After(30 * time.Second):
				_ = cmd.Process.Kill() // only the process we started
			}
		} else {
			aeGui := strings.TrimSuffix(aePath, ".com") + ".exe"
			if _, err := os.Stat(aeGui); err == nil {
				fmt.Printf("Opening AEP in After Effects: %s\n", targetAEP)
				_ = exec.Command(aeGui, targetAEP).Start()
			}
		}
	}
}

// waitForAEP blocks until aepPath is written after start and its size settles,
// the script reports an error in errLog, or timeout elapses.
func waitForAEP(aepPath, errLog string, start time.Time, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	lastSize := int64(-1)
	for time.Now().Before(deadline) {
		if data, err := os.ReadFile(errLog); err == nil {
			return fmt.Errorf("After Effects script failed: %s", strings.TrimSpace(string(data)))
		}
		if fi, err := os.Stat(aepPath); err == nil && !fi.ModTime().Before(start) {
			if fi.Size() > 0 && fi.Size() == lastSize {
				return nil
			}
			lastSize = fi.Size()
		}
		time.Sleep(500 * time.Millisecond)
	}
	return fmt.Errorf("timed out after %v waiting for After Effects to save %s", timeout, aepPath)
}

func findAfterEffectsCLI() (string, error) {
	// Look under Program Files
	patterns := []string{
		`C:\Program Files\Adobe\Adobe After Effects *\Support Files\AfterFX.com`,
		`C:\Program Files\Adobe\After Effects *\Support Files\AfterFX.com`,
	}
	for _, p := range patterns {
		matches, err := filepath.Glob(p)
		if err == nil && len(matches) > 0 {
			// Pick latest
			return matches[len(matches)-1], nil
		}
	}
	return "", fmt.Errorf("AfterFX.com not found in default Adobe installation directories")
}

// GenerateJSX converts an authoring project structure into ES3 ExtendScript code
func GenerateJSX(proj *ProjectDoc, aepPath string, closeOnComplete bool) (string, error) {
	g := &Generator{}

	g.write("// Auto-generated by json2jsx. ExtendScript (ES3) compatible.")
	g.write("(function() {")
	g.write("  if (!app.project) { app.newProject(); }")
	g.write("  app.beginUndoGroup('Build Motion Project');")
	g.write("  var undoOpen = true;")
	g.write("  try {")

	if proj.ExpressionEngine != "" {
		if strings.Contains(strings.ToLower(proj.ExpressionEngine), "java") {
			g.write("    try { app.project.expressionEngine = 'javascript-1.0'; } catch(e) {}")
		} else {
			g.write("    try { app.project.expressionEngine = 'extendscript'; } catch(e) {}")
		}
	}

	if proj.BitDepth != "" {
		depthVal := 8
		if strings.Contains(proj.BitDepth, "16") {
			depthVal = 16
		} else if strings.Contains(proj.BitDepth, "32") {
			depthVal = 32
		}
		g.write("    try { app.project.bitsPerChannel = %d; } catch(e) {}", depthVal)
	}

	g.write("    var assets = {};")
	g.write("    var comps = {};")
	g.write("    var layers = {};")

	// Helper JS functions for color conversion, ease, and paths
	writeJSHelpers(g)

	// Step 1: Create Assets (Footage / Solids)
	for i, asset := range proj.Assets {
		assetVar := fmt.Sprintf("asset_%d", i)
		switch asset.Type {
		case "solid":
			r, gr, b := parseColor(asset.SolidColor)
			w := asset.Width
			if w <= 0 {
				w = 1920
			}
			h := asset.Height
			if h <= 0 {
				h = 1080
			}
			g.write("    var %s = app.project.importSolid([%g, %g, %g], %q, %d, %d, 1);",
				assetVar, r, gr, b, asset.Name, w, h)
			g.write("    assets[%q] = %s;", asset.ID, assetVar)
		case "file":
			escapedFile := escapePath(asset.File)
			g.write("    try {")
			g.write("      var f_%d = new File(%q);", i, escapedFile)
			g.write("      if (f_%d.exists) {", i)
			g.write("        var %s = app.project.importFile(new ImportOptions(f_%d));", assetVar, i)
			g.write("        assets[%q] = %s;", asset.ID, assetVar)
			g.write("      } else {")
			g.write("        $.writeln('Asset file missing on disk: ' + %q);", escapedFile)
			g.write("      }")
			g.write("    } catch(e) {")
			g.write("      $.writeln('Asset import error: ' + e.toString());")
			g.write("    }")
		}
	}

	// Step 2: Create all Compositions first (allows precomp layer references)
	for i, c := range proj.Compositions {
		compVar := fmt.Sprintf("comp_%d", i)
		fps := c.FPS
		if fps <= 0 {
			fps = 24.0
		}
		dur := c.Duration
		if dur <= 0 {
			dur = 5.0
		}
		r, gr, b := parseColor(c.BackgroundColor)
		g.write("    var %s = app.project.items.addComp(%q, %d, %d, 1, %g, %g);",
			compVar, c.Name, c.Width, c.Height, dur, fps)
		g.write("    %s.bgColor = [%g, %g, %g];", compVar, r, gr, b)
		g.write("    comps[%q] = %s;", c.Name, compVar)
	}

	// Step 3: Populate Layers in Compositions (reversed: top-to-bottom creation)
	for compIdx, c := range proj.Compositions {
		compVar := fmt.Sprintf("comp_%d", compIdx)
		g.write("    // --- Layers for Comp: %s ---", c.Name)

		// Create layers in reverse order so layer 0 in JSON ends up at the top
		for lIdx := len(c.Layers) - 1; lIdx >= 0; lIdx-- {
			l := c.Layers[lIdx]
			layerVar := fmt.Sprintf("layer_%d_%d", compIdx, lIdx)

			switch l.Type {
			case "solid":
				w, h := c.Width, c.Height
				r, gr, b := 0.5, 0.5, 0.5
				if l.Source != "" {
					g.write("    var %s = (assets[%q]) ? %s.layers.add(assets[%q]) : %s.layers.addSolid([%g, %g, %g], %q, %d, %d, 1);",
						layerVar, l.Source, compVar, l.Source, compVar, r, gr, b, l.Name, w, h)
				} else {
					g.write("    var %s = %s.layers.addSolid([%g, %g, %g], %q, %d, %d, 1);",
						layerVar, compVar, r, gr, b, l.Name, w, h)
				}

			case "text":
				textStr := ""
				if l.Text != nil {
					textStr = l.Text.String
				}
				if l.Text != nil && len(l.Text.BoxSize) == 2 {
					g.write("    var %s = %s.layers.addBoxText([%g, %g], %q);", layerVar, compVar, l.Text.BoxSize[0], l.Text.BoxSize[1], textStr)
				} else {
					g.write("    var %s = %s.layers.addText(%q);", layerVar, compVar, textStr)
				}
				if l.Text != nil {
					writeTextStyling(g, layerVar, l.Text)
				}

			case "shape":
				g.write("    var %s = %s.layers.addShape();", layerVar, compVar)
				for _, shp := range l.Shapes {
					writeShapeItem(g, layerVar, "", shp)
				}

			case "null":
				g.write("    var %s = %s.layers.addNull();", layerVar, compVar)

			case "precomp":
				g.write("    var %s = (comps[%q]) ? %s.layers.add(comps[%q]) : %s.layers.addNull();", layerVar, l.Source, compVar, l.Source, compVar)

			case "footage", "audio":
				g.write("    var %s = (assets[%q]) ? %s.layers.add(assets[%q]) : %s.layers.addSolid([0.5, 0.5, 0.5], %q, %d, %d, 1);",
					layerVar, l.Source, compVar, l.Source, compVar, l.Name, c.Width, c.Height)

			case "camera":
				g.write("    var %s = %s.layers.addCamera(%q, [%d/2, %d/2]);",
					layerVar, compVar, l.Name, c.Width, c.Height)

			case "light":
				g.write("    var %s = %s.layers.addLight(%q, [%d/2, %d/2]);",
					layerVar, compVar, l.Name, c.Width, c.Height)

			case "adjustment":
				w, h := c.Width, c.Height
				g.write("    var %s = %s.layers.addSolid([1,1,1], %q, %d, %d, 1);",
					layerVar, compVar, l.Name, w, h)
				g.write("    %s.adjustmentLayer = true;", layerVar)

			default:
				// Fallback to null
				g.write("    var %s = %s.layers.addNull();", layerVar, compVar)
			}

			// Name and basic flags
			g.write("    %s.name = %q;", layerVar, l.Name)
			g.write("    layers[%q] = %s;", c.Name+"//"+l.Name, layerVar)

			if l.ThreeD {
				g.write("    try { %s.threeDLayer = true; } catch(e) {}", layerVar)
			}
			if l.Collapse {
				g.write("    try { %s.collapseTransformation = true; } catch(e) {}", layerVar)
			}
			if l.MotionBlur {
				g.write("    try { %s.motionBlur = true; } catch(e) {}", layerVar)
			}
			if l.Adjustment {
				g.write("    try { %s.adjustmentLayer = true; } catch(e) {}", layerVar)
			}
			if l.Enabled != nil && !*l.Enabled {
				g.write("    try { %s.enabled = false; } catch(e) {}", layerVar)
			}

			// Timing
			if l.StartTime != nil {
				g.write("    try { %s.startTime = %g; } catch(e) {}", layerVar, *l.StartTime)
			}
			if l.In != nil {
				g.write("    try { %s.inPoint = %g; } catch(e) {}", layerVar, *l.In)
			}
			if l.Out != nil && *l.Out > 0 {
				g.write("    try { if (%g > %s.inPoint) { %s.outPoint = %g; } } catch(e) {}", *l.Out, layerVar, layerVar, *l.Out)
			}

			// Blend mode
			if l.BlendMode != "" {
				bmCode := mapBlendMode(l.BlendMode)
				if bmCode != "" {
					g.write("    try { %s.blendingMode = %s; } catch(e) {}", layerVar, bmCode)
				}
			}

			// Masks
			for mIdx, m := range l.Masks {
				maskVar := fmt.Sprintf("mask_%d_%d_%d", compIdx, lIdx, mIdx)
				g.write("    var %s = %s.Masks.addProperty('ADBE Mask Atom');", maskVar, layerVar)
				if m.Name != "" {
					g.write("    %s.name = %q;", maskVar, m.Name)
				}
				if m.Mode != "" {
					g.write("    try { %s.maskMode = MaskMode.%s; } catch(e) {}", maskVar, strings.ToUpper(m.Mode))
				}
				if m.Inverted {
					g.write("    %s.inverted = true;", maskVar)
				}
				if m.Path != nil {
					writePathAssignment(g, fmt.Sprintf("%s.property('ADBE Mask Shape')", maskVar), m.Path)
				}
				if m.Opacity != nil {
					writePropertyData(g, fmt.Sprintf("%s.property('ADBE Mask Opacity')", maskVar), m.Opacity)
				}
				if m.Feather != nil {
					writePropertyData(g, fmt.Sprintf("%s.property('ADBE Mask Feather')", maskVar), m.Feather)
				}
			}

			// Effects
			for eIdx, fx := range l.Effects {
				fxVar := fmt.Sprintf("fx_%d_%d_%d", compIdx, lIdx, eIdx)
				g.write("    var %s = %s.property('ADBE Effect Parade').addProperty(%q);",
					fxVar, layerVar, fx.MatchName)
				if fx.Name != "" {
					g.write("    %s.name = %q;", fxVar, fx.Name)
				}
				for pName, pVal := range fx.Props {
					propRef := fmt.Sprintf("%s.property(%q)", fxVar, pName)
					writePropertyData(g, propRef, pVal)
				}
			}

			// Transform properties
			if l.Transform != nil {
				for pKey, pVal := range l.Transform {
					matchName := mapTransformMatchName(pKey, l.ThreeD)
					if matchName == "" {
						continue
					}
					propRef := fmt.Sprintf("%s.property('ADBE Transform Group').property(%q)", layerVar, matchName)
					writePropertyData(g, propRef, pVal)
				}
			}

			// Raw JSX escape hatch
			if l.JSX != "" {
				g.write("    // Custom Layer JSX")
				g.write("    (function(layer, comp) {")
				g.write("      %s", l.JSX)
				g.write("    })(%s, %s);", layerVar, compVar)
			}
		}

		// Step 4: Parenting & Track Mattes (must be applied after all layers exist)
		for lIdx, l := range c.Layers {
			layerVar := fmt.Sprintf("layer_%d_%d", compIdx, lIdx)
			if l.Parent != "" {
				parentKey := c.Name + "//" + l.Parent
				g.write("    if (layers[%q]) { try { %s.setParentWithJump(layers[%q]); } catch(e) {} }",
					parentKey, layerVar, parentKey)
			}
			if l.TrackMatte != nil && l.TrackMatte.Target != "" {
				targetKey := c.Name + "//" + l.TrackMatte.Target
				tmType := mapTrackMatteType(l.TrackMatte.Type)
				g.write("    if (layers[%q]) { try { %s.setTrackMatte(layers[%q], %s); } catch(e) {} }",
					targetKey, layerVar, targetKey, tmType)
			}
		}
	}

	g.write("    if (undoOpen) { app.endUndoGroup(); undoOpen = false; }")

	// Step 5: Save and Open Project File
	if aepPath != "" {
		escapedAEP := escapePath(aepPath)
		g.write("    // Save and Open Generated Project File")
		g.write("    var aepFile = new File(%q);", escapedAEP)
		g.write("    try { if (!aepFile.parent.exists) { aepFile.parent.create(); } } catch(e) {}")
		g.write("    app.project.save(aepFile);")
		g.write("    $.writeln('SAVED_AEP: ' + aepFile.fsName);")
		if !closeOnComplete {
			g.write("    if (aepFile.exists && (!app.project.file || app.project.file.fsName !== aepFile.fsName)) {")
			g.write("      app.open(aepFile);")
			g.write("    }")
		}
	}

	if !closeOnComplete && len(proj.Compositions) > 0 {
		g.write("    try {")
		g.write("      if (typeof comp_0 !== 'undefined' && comp_0) { comp_0.openInViewer(); }")
		g.write("      else if (app.project && app.project.numItems > 0) {")
		g.write("        for (var ci = 1; ci <= app.project.numItems; ci++) {")
		g.write("          if (app.project.item(ci) instanceof CompItem) { app.project.item(ci).openInViewer(); break; }")
		g.write("        }")
		g.write("      }")
		g.write("    } catch(e) {}")
	}

	g.write("  } catch(err) {")
	if aepPath != "" {
		g.write("    try {")
		g.write("      var errFile = new File(%q);", escapePath(filepath.Join(filepath.Dir(aepPath), "ae_error.log")))
		g.write("      errFile.open('w');")
		g.write("      errFile.writeln('BUILD_ERROR: ' + err.toString() + ' (line ' + err.line + ')');")
		g.write("      errFile.close();")
		g.write("    } catch(e) {}")
	}
	if !closeOnComplete {
		g.write("    alert('Build Error: ' + err.toString() + ' (line ' + err.line + ')');")
	}
	g.write("    $.writeln('BUILD_ERROR: ' + err.toString() + ' (line ' + err.line + ')');")
	g.write("  } finally {")
	g.write("    if (undoOpen) { try { app.endUndoGroup(); } catch(e) {} }")
	if closeOnComplete {
		g.write("    // Auto-close when executed non-interactively via CLI")
		g.write("    app.quit();")
	}
	g.write("  }")
	g.write("})();")

	return escapeNonASCII(g.sb.String()), nil
}

// escapeNonASCII rewrites non-ASCII runes as \uXXXX escapes. ExtendScript reads a
// BOM-less .jsx in the system code page, so raw UTF-8 text ("93 °C") would be mangled.
// Non-ASCII only occurs inside string literals and comments, where the escape is safe.
func escapeNonASCII(code string) string {
	var sb strings.Builder
	for _, r := range code {
		switch {
		case r < 0x80:
			sb.WriteRune(r)
		case r <= 0xFFFF:
			fmt.Fprintf(&sb, "\\u%04x", r)
		default:
			r -= 0x10000
			fmt.Fprintf(&sb, "\\u%04x\\u%04x", 0xD800+(r>>10), 0xDC00+(r&0x3FF))
		}
	}
	return sb.String()
}

func writeJSHelpers(g *Generator) {
	g.write(`
    function parseHex(h) {
      if (!h || typeof h !== 'string') return [1,1,1];
      h = h.replace('#', '');
      if (h.length === 3) h = h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
      var num = parseInt(h, 16);
      return [(num >> 16 & 255) / 255, (num >> 8 & 255) / 255, (num & 255) / 255];
    }
    function makeEase(preset) {
      if (!preset || preset === 'linear') return new KeyframeEase(0, 0.1);
      if (preset === 'easeOut') return new KeyframeEase(0, 75);
      if (preset === 'easeIn') return new KeyframeEase(0, 75);
      if (preset === 'easeInOut') return new KeyframeEase(0, 75);
      return new KeyframeEase(0, 33.33);
    }
`)
}

func writeTextStyling(g *Generator, layerVar string, t *TextDoc) {
	g.write("    var textProp = %s.property('ADBE Text Properties').property('ADBE Text Document');", layerVar)
	g.write("    var textDoc = textProp.value;")
	g.write("    textDoc.text = %q;", t.String)
	if t.Font != "" {
		g.write("    textDoc.font = %q;", t.Font)
	}
	if t.FontSize > 0 {
		g.write("    textDoc.fontSize = %g;", t.FontSize)
	}
	if t.FillColor != nil {
		r, gr, b := parseColor(t.FillColor)
		g.write("    textDoc.fillColor = [%g, %g, %g];", r, gr, b)
	}
	if t.ApplyFill != nil {
		g.write("    textDoc.applyFill = %t;", *t.ApplyFill)
	}
	if t.StrokeColor != nil {
		r, gr, b := parseColor(t.StrokeColor)
		g.write("    textDoc.strokeColor = [%g, %g, %g];", r, gr, b)
	}
	if t.ApplyStroke != nil {
		g.write("    textDoc.applyStroke = %t;", *t.ApplyStroke)
	}
	if t.StrokeWidth > 0 {
		g.write("    textDoc.strokeWidth = %g;", t.StrokeWidth)
	}
	if t.Tracking != 0 {
		g.write("    textDoc.tracking = %g;", t.Tracking)
	}
	if t.Justification != "" {
		justMap := map[string]string{
			"left":          "ParagraphJustification.LEFT_JUSTIFY",
			"center":        "ParagraphJustification.CENTER_JUSTIFY",
			"right":         "ParagraphJustification.RIGHT_JUSTIFY",
			"justifyLeft":   "ParagraphJustification.FULL_JUSTIFY_LASTLINE_LEFT",
			"justifyRight":  "ParagraphJustification.FULL_JUSTIFY_LASTLINE_RIGHT",
			"justifyCenter": "ParagraphJustification.FULL_JUSTIFY_LASTLINE_CENTER",
			"justifyFull":   "ParagraphJustification.FULL_JUSTIFY_LASTLINE_FULL",
		}
		if aeJust, ok := justMap[t.Justification]; ok {
			g.write("    textDoc.justification = %s;", aeJust)
		}
	}
	if t.Leading > 0 {
		g.write("    try { textDoc.autoLeading = false; textDoc.leading = %g; } catch(e) {}", t.Leading)
	}
	if t.SpaceAfter > 0 {
		g.write("    try { textDoc.spaceAfter = %g; } catch(e) {}", t.SpaceAfter)
	}
	// characterRange needs AE 24.3+; older versions keep the base style
	for _, r := range t.Runs {
		g.write("    try { var cr = textDoc.characterRange(%d, %d);", r.Start, r.End)
		if r.Font != "" {
			g.write("      cr.font = %q;", r.Font)
		}
		if r.FontSize > 0 {
			g.write("      cr.fontSize = %g;", r.FontSize)
		}
		if r.FillColor != nil {
			cr, cg, cb := parseColor(r.FillColor)
			g.write("      cr.applyFill = true; cr.fillColor = [%g, %g, %g];", cr, cg, cb)
		}
		if r.Tracking != nil {
			g.write("      cr.tracking = %g;", *r.Tracking)
		}
		if r.Leading > 0 {
			g.write("      cr.autoLeading = false; cr.leading = %g;", r.Leading)
		}
		g.write("    } catch(e) {}")
	}
	g.write("    textProp.setValue(textDoc);")
	if len(t.BoxSize) == 2 {
		// box text: anchor at the box's top-left, so position = box top-left like design tools
		g.write("    try { var bp = textProp.value.boxTextPos; %s.property('ADBE Transform Group').property('ADBE Anchor Point').setValue([bp[0], bp[1]]); } catch(e) {}", layerVar)
	}
}

func writeShapeItem(g *Generator, layerVar, parentGroup string, shp ShapeItemDoc) {
	baseRef := layerVar + ".property('ADBE Root Vectors Group')"
	if parentGroup != "" {
		baseRef = fmt.Sprintf("(%s.property('ADBE Vectors Group') || %s.property(2) || %s)", parentGroup, parentGroup, parentGroup)
	}

	switch shp.Type {
	case "rect":
		sVar := "sh_rect_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Shape - Rect');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		if shp.Size != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Rect Size')", shp.Size)
		}
		if shp.Position != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Rect Position')", shp.Position)
		}
		if shp.Roundness != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Rect Roundness')", shp.Roundness)
		}

	case "ellipse":
		sVar := "sh_ell_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Shape - Ellipse');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		if shp.Size != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Ellipse Size')", shp.Size)
		}
		if shp.Position != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Ellipse Position')", shp.Position)
		}

	case "fill":
		sVar := "sh_fill_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Graphic - Fill');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		if shp.Color != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Fill Color')", shp.Color)
		}
		if shp.Opacity != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Fill Opacity')", shp.Opacity)
		}

	case "stroke":
		sVar := "sh_strk_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Graphic - Stroke');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		if shp.Color != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Stroke Color')", shp.Color)
		}
		if shp.StrokeWidth != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Stroke Width')", shp.StrokeWidth)
		}
		if shp.Opacity != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Stroke Opacity')", shp.Opacity)
		}
		if v, ok := map[string]int{"butt": 1, "round": 2, "projecting": 3}[shp.LineCap]; ok {
			g.write("    try { %s.property('ADBE Vector Stroke Line Cap').setValue(%d); } catch(e) {}", sVar, v)
		}
		if v, ok := map[string]int{"miter": 1, "round": 2, "bevel": 3}[shp.LineJoin]; ok {
			g.write("    try { %s.property('ADBE Vector Stroke Line Join').setValue(%d); } catch(e) {}", sVar, v)
		}

	case "trim":
		sVar := "sh_trim_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Filter - Trim');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		if shp.Start != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Trim Start')", shp.Start)
		}
		if shp.End != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Trim End')", shp.End)
		}
		if shp.Offset != nil {
			writePropertyData(g, sVar+".property('ADBE Vector Trim Offset')", shp.Offset)
		}

	case "path":
		if shp.Path != nil {
			sVar := "sh_path_" + randomID()
			g.write("    var %s = %s.addProperty('ADBE Vector Shape - Group');", sVar, baseRef)
			if shp.Name != "" {
				g.write("    %s.name = %q;", sVar, shp.Name)
			}
			writePathAssignment(g, sVar+".property('ADBE Vector Shape')", shp.Path)
		}

	case "group":
		sVar := "sh_grp_" + randomID()
		g.write("    var %s = %s.addProperty('ADBE Vector Group');", sVar, baseRef)
		if shp.Name != "" {
			g.write("    %s.name = %q;", sVar, shp.Name)
		}
		groupProps := map[string]string{
			"anchorPoint": "ADBE Vector Anchor",
			"position":    "ADBE Vector Position",
			"scale":       "ADBE Vector Scale",
			"rotation":    "ADBE Vector Rotation",
			"opacity":     "ADBE Vector Group Opacity",
		}
		for _, key := range []string{"anchorPoint", "position", "scale", "rotation", "opacity"} {
			if v, ok := shp.Transform[key]; ok {
				writePropertyData(g, fmt.Sprintf("%s.property('ADBE Vector Transform Group').property(%q)", sVar, groupProps[key]), v)
			}
		}
		for _, child := range shp.Items {
			writeShapeItem(g, layerVar, sVar, child)
		}
	}
}

func writePathAssignment(g *Generator, propRef string, p *BezierPathDoc) {
	vData, _ := json.Marshal(p.Vertices)
	inData, _ := json.Marshal(p.InTangents)
	outData, _ := json.Marshal(p.OutTangents)
	if len(p.InTangents) == 0 {
		inData = []byte("[]")
	}
	if len(p.OutTangents) == 0 {
		outData = []byte("[]")
	}
	g.write("    (function(prop) {")
	g.write("      var sp = new Shape();")
	g.write("      sp.vertices = %s;", string(vData))
	g.write("      sp.inTangents = %s;", string(inData))
	g.write("      sp.outTangents = %s;", string(outData))
	g.write("      sp.closed = %t;", p.Closed)
	g.write("      prop.setValue(sp);")
	g.write("    })(%s);", propRef)
}

func writePropertyData(g *Generator, propRef string, data interface{}) {
	if data == nil {
		return
	}

	// Case 1: Simple scalar or array constant
	switch v := data.(type) {
	case float64:
		g.write("    try { %s.setValue(%g); } catch(e) {}", propRef, v)
		return
	case int:
		g.write("    try { %s.setValue(%d); } catch(e) {}", propRef, v)
		return
	case bool:
		g.write("    try { %s.setValue(%t); } catch(e) {}", propRef, v)
		return
	case string:
		if strings.HasPrefix(v, "#") {
			r, gr, b := parseColor(v)
			g.write("    try { %s.setValue([%g, %g, %g, 1]); } catch(e) {}", propRef, r, gr, b)
		} else {
			g.write("    try { %s.setValue(%q); } catch(e) {}", propRef, v)
		}
		return
	case []interface{}:
		jsonArr, _ := json.Marshal(v)
		g.write("    try { %s.setValue(%s); } catch(e) {}", propRef, string(jsonArr))
		return
	}

	// Case 2: Object representation (static value, expression, or keyframes)
	objBytes, err := json.Marshal(data)
	if err != nil {
		return
	}

	var anim AnimValueDoc
	if err := json.Unmarshal(objBytes, &anim); err != nil {
		return
	}

	// Constant value inside object
	if anim.Value != nil && len(anim.Keyframes) == 0 {
		writePropertyData(g, propRef, anim.Value)
	}

	// Keyframes
	if len(anim.Keyframes) > 0 {
		g.write("    (function(p) {")
		g.write("      if (!p) return;")
		for i, kf := range anim.Keyframes {
			valStr := formatValueForAE(kf.Value)
			g.write("      p.setValueAtTime(%g, %s);", kf.Time, valStr)
			kfIdx := i + 1

			// Interpolation
			switch kf.Interp {
			case "hold":
				g.write("      try { p.setInterpolationTypeAtKey(%d, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD); } catch(e) {}", kfIdx)
			case "linear":
				g.write("      try { p.setInterpolationTypeAtKey(%d, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR); } catch(e) {}", kfIdx)
			default: // bezier
				if kf.Ease != nil {
					if easePreset, ok := kf.Ease.(string); ok {
						g.write("      try {")
						g.write("        var e = makeEase(%q);", easePreset)
						g.write("        if (p.propertyValueType === PropertyValueType.TwoD_SPATIAL || p.propertyValueType === PropertyValueType.ThreeD_SPATIAL) {")
						g.write("          p.setTemporalEaseAtKey(%d, [e], [e]);", kfIdx)
						g.write("        } else if (p.propertyValueType === PropertyValueType.TwoD) {")
						g.write("          p.setTemporalEaseAtKey(%d, [e, e], [e, e]);", kfIdx)
						g.write("        } else if (p.propertyValueType === PropertyValueType.ThreeD) {")
						g.write("          p.setTemporalEaseAtKey(%d, [e, e, e], [e, e, e]);", kfIdx)
						g.write("        } else {")
						g.write("          p.setTemporalEaseAtKey(%d, [e], [e]);", kfIdx)
						g.write("        }")
						g.write("      } catch(e) {}")
					} else if easeObj, ok := kf.Ease.(map[string]interface{}); ok {
						// Custom handles: {"inInfluence", "inSpeed", "outInfluence", "outSpeed"}
						g.write("      try {")
						g.write("        var ei = new KeyframeEase(%g, %g), eo = new KeyframeEase(%g, %g);",
							easeNum(easeObj, "inSpeed", 0), easeInfluence(easeObj, "inInfluence"),
							easeNum(easeObj, "outSpeed", 0), easeInfluence(easeObj, "outInfluence"))
						g.write("        if (p.propertyValueType === PropertyValueType.TwoD) {")
						g.write("          p.setTemporalEaseAtKey(%d, [ei, ei], [eo, eo]);", kfIdx)
						g.write("        } else if (p.propertyValueType === PropertyValueType.ThreeD) {")
						g.write("          p.setTemporalEaseAtKey(%d, [ei, ei, ei], [eo, eo, eo]);", kfIdx)
						g.write("        } else {")
						g.write("          p.setTemporalEaseAtKey(%d, [ei], [eo]);", kfIdx)
						g.write("        }")
						g.write("      } catch(e) {}")
					}
				}
			}

			// Spatial tangents
			if len(kf.InTangent) > 0 || len(kf.OutTangent) > 0 {
				inT, _ := json.Marshal(kf.InTangent)
				outT, _ := json.Marshal(kf.OutTangent)
				// auto-bezier off first, or AE recomputes the tangents when the next key is added
				g.write("      try { p.setSpatialAutoBezierAtKey(%d, false); p.setSpatialContinuousAtKey(%d, false); } catch(e) {}", kfIdx, kfIdx)
				if len(kf.InTangent) == 2 && len(kf.OutTangent) == 2 {
					// 2D layer positions are ThreeD_SPATIAL and want 3-value tangents
					g.write("      try { p.setSpatialTangentsAtKey(%d, %s, %s); } catch(e) { try { p.setSpatialTangentsAtKey(%d, [%g, %g, 0], [%g, %g, 0]); } catch(e2) {} }",
						kfIdx, string(inT), string(outT), kfIdx, kf.InTangent[0], kf.InTangent[1], kf.OutTangent[0], kf.OutTangent[1])
				} else {
					g.write("      try { p.setSpatialTangentsAtKey(%d, %s, %s); } catch(e) {}", kfIdx, string(inT), string(outT))
				}
			}
		}
		g.write("    })(%s);", propRef)
	}

	// Expression
	if anim.Expression != "" {
		g.write("    try { %s.expression = %q; } catch(e) {}", propRef, anim.Expression)
	}
}

func easeNum(m map[string]interface{}, key string, def float64) float64 {
	if v, ok := m[key].(float64); ok {
		return v
	}
	return def
}

// easeInfluence reads an influence percentage, clamped to the 0.1-100 range AE accepts.
func easeInfluence(m map[string]interface{}, key string) float64 {
	v := easeNum(m, key, 33.33)
	if v < 0.1 {
		v = 0.1
	}
	if v > 100 {
		v = 100
	}
	return v
}

func formatValueForAE(val interface{}) string {
	if val == nil {
		return "0"
	}
	if str, ok := val.(string); ok && strings.HasPrefix(str, "#") {
		r, gr, b := parseColor(str)
		return fmt.Sprintf("[%g, %g, %g, 1]", r, gr, b)
	}
	b, _ := json.Marshal(val)
	return string(b)
}

func parseColor(c interface{}) (float64, float64, float64) {
	if c == nil {
		return 0, 0, 0
	}
	switch v := c.(type) {
	case string:
		hexStr := strings.TrimPrefix(v, "#")
		if len(hexStr) == 3 {
			hexStr = string([]byte{hexStr[0], hexStr[0], hexStr[1], hexStr[1], hexStr[2], hexStr[2]})
		}
		if len(hexStr) >= 6 {
			val, _ := strconv.ParseUint(hexStr[:6], 16, 32)
			r := float64((val>>16)&0xFF) / 255.0
			g := float64((val>>8)&0xFF) / 255.0
			b := float64(val&0xFF) / 255.0
			return r, g, b
		}
	case []interface{}:
		if len(v) >= 3 {
			r, _ := v[0].(float64)
			g, _ := v[1].(float64)
			b, _ := v[2].(float64)
			return r, g, b
		}
	case []float64:
		if len(v) >= 3 {
			return v[0], v[1], v[2]
		}
	}
	return 1, 1, 1
}

func mapTransformMatchName(key string, is3D bool) string {
	switch key {
	case "position":
		return "ADBE Position"
	case "xPosition":
		return "ADBE Position_0"
	case "yPosition":
		return "ADBE Position_1"
	case "zPosition":
		return "ADBE Position_2"
	case "anchorPoint":
		return "ADBE Anchor Point"
	case "scale":
		return "ADBE Scale"
	case "rotation":
		if is3D {
			return "ADBE Rotate Z"
		}
		return "ADBE Rotate Z"
	case "xRotation":
		return "ADBE Rotate X"
	case "yRotation":
		return "ADBE Rotate Y"
	case "zRotation":
		return "ADBE Rotate Z"
	case "orientation":
		return "ADBE Orientation"
	case "opacity":
		return "ADBE Opacity"
	default:
		return key
	}
}

func mapBlendMode(b string) string {
	bm := strings.ToUpper(strings.ReplaceAll(b, " ", "_"))
	return fmt.Sprintf("BlendingMode.%s", bm)
}

func mapTrackMatteType(tm string) string {
	switch tm {
	case "Alpha":
		return "TrackMatteType.ALPHA"
	case "Alpha Inverted":
		return "TrackMatteType.ALPHA_INVERTED"
	case "Luma":
		return "TrackMatteType.LUMA"
	case "Luma Inverted":
		return "TrackMatteType.LUMA_INVERTED"
	default:
		return "TrackMatteType.NO_TRACK_MATTE"
	}
}

func escapePath(p string) string {
	return strings.ReplaceAll(filepath.ToSlash(p), "\\", "/")
}

var idCounter int

func randomID() string {
	idCounter++
	return fmt.Sprintf("%d", idCounter)
}
