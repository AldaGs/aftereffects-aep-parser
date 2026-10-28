package main

import (
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	aep "github.com/boltframe/aftereffects-aep-parser"
)

// JSON export model

type exportProject struct {
	File             string       `json:"file"`
	ExpressionEngine string       `json:"expressionEngine"`
	BitDepth         string       `json:"bitDepth"`
	TotalItems       int          `json:"totalItems"`
	Root             *exportItem  `json:"root"`
	Texts            []exportText `json:"texts"`
}

type exportItem struct {
	ID          uint32           `json:"id"`
	Name        string           `json:"name"`
	Type        string           `json:"type"`
	Width       uint16           `json:"width,omitempty"`
	Height      uint16           `json:"height,omitempty"`
	Framerate   float64          `json:"framerate,omitempty"`
	Seconds     float64          `json:"seconds,omitempty"`
	Background  string           `json:"backgroundColor,omitempty"`
	Footage     string           `json:"footageType,omitempty"`
	File        string           `json:"file,omitempty"`
	SolidColor  []float64        `json:"solidColor,omitempty"`
	SourceLayer *aep.SourceLayer `json:"sourceLayer,omitempty"`
	Layers      []exportLayer    `json:"layers,omitempty"`
	Children    []*exportItem    `json:"children,omitempty"`
}

type exportLayer struct {
	Index      uint32  `json:"index"`
	Name       string  `json:"name"`
	SourceID   uint32  `json:"sourceId"`
	ID         uint32  `json:"layerId"`
	Kind       string  `json:"kind"`
	ParentID   uint32  `json:"parent,omitempty"`
	BlendMode  string  `json:"blendMode,omitempty"`
	TrackMatte string  `json:"trackMatte,omitempty"`
	MatteLayer uint32  `json:"matteLayer,omitempty"`
	SourceName string  `json:"sourceName,omitempty"`
	StartTime  float64 `json:"startTime,omitempty"`
	InPoint    float64 `json:"inPoint,omitempty"`
	Duration   float64 `json:"duration,omitempty"`
	// ParentIndex / MatteLayerIndex resolve parent / matteLayer (ldta ids) to the
	// 1-based layer index in the same comp, which is what ExtendScript uses.
	ParentIndex     uint32 `json:"parentIndex,omitempty"`
	MatteLayerIndex uint32 `json:"matteLayerIndex,omitempty"`
	// CompInPoint / CompOutPoint are in comp time. CompOutPoint assumes the ldta
	// duration runs from the in point: UNVERIFIED, see docs/IMPLEMENTATION_PLAN.md.
	CompInPoint  float64          `json:"compInPoint"`
	CompOutPoint float64          `json:"compOutPoint"`
	Text         string           `json:"text,omitempty"`
	TextStyle    *aep.TextStyle   `json:"textStyle,omitempty"`
	Flags        map[string]bool  `json:"flags"`
	Transform    []exportProperty `json:"transform,omitempty"`
	Effects      []exportProperty `json:"effects,omitempty"`
	Markers      []float64        `json:"markers,omitempty"`
	Masks        []exportProperty `json:"masks,omitempty"`
	Contents     []exportProperty `json:"contents,omitempty"`
	Audio        []exportProperty `json:"audio,omitempty"`
	TextProps    *exportProperty  `json:"textProperties,omitempty"`
}

type exportProperty struct {
	Name       string           `json:"name"`
	MatchName  string           `json:"matchName"`
	Label      string           `json:"label,omitempty"`
	Type       string           `json:"type"`
	ValueType  string           `json:"valueType,omitempty"`
	Dimensions int              `json:"dimensions,omitempty"`
	Value      []float64        `json:"value,omitempty"`
	Animated   bool             `json:"animated,omitempty"`
	Keyframes  []exportKeyframe `json:"keyframes,omitempty"`
	Expression string           `json:"expression,omitempty"`
	Options    []string         `json:"selectOptions,omitempty"`
	Path       *exportPath      `json:"path,omitempty"`
	MaskMode   string           `json:"maskMode,omitempty"`
	Inverted   bool             `json:"inverted,omitempty"`
	// Arb is an arbitrary-data parameter's raw bytes (e.g. Colorama's
	// palette), hex-encoded; its layout belongs to the effect.
	Arb        string           `json:"arb,omitempty"`
	Properties []exportProperty `json:"properties,omitempty"`
}

type exportKeyframe struct {
	Time             float64     `json:"time"`
	CompTime         float64     `json:"compTime"`
	Value            []float64   `json:"value,omitempty"`
	InInterpolation  string      `json:"inInterpolation"`
	OutInterpolation string      `json:"outInterpolation"`
	InSpeed          []float64   `json:"inSpeed,omitempty"`
	InInfluence      []float64   `json:"inInfluence,omitempty"`
	OutSpeed         []float64   `json:"outSpeed,omitempty"`
	OutInfluence     []float64   `json:"outInfluence,omitempty"`
	InTangent        []float64   `json:"inTangent,omitempty"`
	OutTangent       []float64   `json:"outTangent,omitempty"`
	Path             *exportPath `json:"path,omitempty"`
}

// exportPath is a bezier path value, tangents relative to their vertex.
type exportPath struct {
	Closed      bool         `json:"closed"`
	Vertices    [][2]float64 `json:"vertices"`
	InTangents  [][2]float64 `json:"inTangents"`
	OutTangents [][2]float64 `json:"outTangents"`
}

func toExportPath(s *aep.PathShape) *exportPath {
	return &exportPath{s.Closed, s.Vertices, s.InTangents, s.OutTangents}
}

// exportText is a flat list of all text layers for convenience.
type exportText struct {
	Composition string `json:"composition"`
	Layer       int    `json:"layer"`
	Text        string `json:"text"`
}

func main() {
	in := flag.String("i", "", "input After Effects project (.aep)")
	out := flag.String("o", "", "output JSON file (.json)")
	tree := flag.Bool("tree", false, "also print a human-readable tree to stdout")
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage:\n  %[1]s -i <input.aep> -o <output.json> [-tree]\n  %[1]s <input.aep> <output.json> [-tree]\n\nOptions:\n", filepath.Base(os.Args[0]))
		flag.PrintDefaults()
	}
	flag.Parse()

	// Allow positional arguments: <input> [output]
	if *in == "" && flag.NArg() > 0 {
		*in = flag.Arg(0)
	}
	if *out == "" && flag.NArg() > 1 {
		*out = flag.Arg(1)
	}
	if *in == "" || *out == "" {
		fmt.Fprintln(os.Stderr, "error: both an input .aep and an output .json are required")
		flag.Usage()
		os.Exit(2)
	}
	path := *in

	project, err := aep.Open(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}

	exp := &exportProject{
		File:             filepath.Base(path),
		ExpressionEngine: project.ExpressionEngine,
		BitDepth:         depthName(project.Depth),
		TotalItems:       len(project.Items),
		Texts:            []exportText{},
	}
	exp.Root = convertItem(project, project.RootFolder, exp)

	data, err := json.MarshalIndent(exp, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	if err := os.WriteFile(*out, data, 0644); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	fmt.Printf("Exported %d items, %d text layers -> %s\n", exp.TotalItems, len(exp.Texts), *out)

	if *tree {
		printTree(exp.Root, 0)
	}
}

func depthName(b aep.BPC) string {
	switch b {
	case aep.BPC8:
		return "8 bpc"
	case aep.BPC16:
		return "16 bpc"
	case aep.BPC32:
		return "32 bpc"
	}
	return fmt.Sprintf("unknown (%d)", b)
}

func convertItem(project *aep.Project, item *aep.Item, exp *exportProject) *exportItem {
	e := &exportItem{ID: item.ID, Name: item.Name, Type: string(item.ItemType)}
	switch item.ItemType {
	case aep.ItemTypeFolder:
		for _, c := range item.FolderContents {
			e.Children = append(e.Children, convertItem(project, c, exp))
		}
	case aep.ItemTypeComposition, aep.ItemTypeFootage:
		e.Width, e.Height = item.FootageDimensions[0], item.FootageDimensions[1]
		e.Framerate, e.Seconds = item.FootageFramerate, item.FootageSeconds
		if item.ItemType == aep.ItemTypeFootage {
			switch {
			case item.FootageType == aep.FootageTypeSolid:
				e.Footage, e.SolidColor = "solid", item.SolidColor[:]
			case item.FootagePath != "":
				e.Footage, e.File = "file", item.FootagePath
				e.SourceLayer = item.SourceLayer
			default:
				e.Footage = "placeholder"
			}
		}
		if item.ItemType == aep.ItemTypeComposition {
			bg := item.BackgroundColor
			e.Background = fmt.Sprintf("#%02x%02x%02x", bg[0], bg[1], bg[2])
		}
		indexByID := make(map[uint32]uint32, len(item.CompositionLayers))
		for _, l := range item.CompositionLayers {
			indexByID[l.ID] = l.Index
		}
		for _, l := range item.CompositionLayers {
			el := exportLayer{
				ParentIndex:     indexByID[l.ParentID],
				MatteLayerIndex: indexByID[l.MatteLayerID],
				CompInPoint:     l.StartTime + l.InPoint,
				CompOutPoint:    l.StartTime + l.InPoint + l.Duration,
				Index:           l.Index,
				Name:            l.Name,
				SourceID:        l.SourceID,
				ID:              l.ID,
				Kind:            layerKind(l),
				ParentID:        l.ParentID,
				BlendMode:       blendModeNames[l.BlendingMode],
				TrackMatte:      trackMatteNames[l.TrackMatteType],
				MatteLayer:      l.MatteLayerID,
				StartTime:       l.StartTime,
				InPoint:         l.InPoint,
				Duration:        l.Duration,
				Text:            l.TextContent,
				TextStyle:       l.TextStyle,
				Flags: map[string]bool{
					"3D":         l.ThreeDEnabled,
					"adjustment": l.AdjustmentLayerEnabled,
					"collapse":   l.CollapseTransformEnabled,
					"shy":        l.ShyEnabled,
					"locked":     l.LockEnabled,
					"solo":       l.SoloEnabled,
					"guide":      l.GuideEnabled,
					"motionBlur": l.MotionBlurEnabled,
					"effects":    l.EffectsEnabled,
					"audio":      l.AudioEnabled,
					"video":      l.VideoEnabled,
				},
			}
			if src, ok := project.Items[l.SourceID]; ok && l.SourceID != 0 {
				el.SourceName = src.Name
			}
			for _, tr := range l.Transform {
				el.Transform = append(el.Transform, convertProperty(tr))
			}
			el.Markers = l.Markers
			for _, fx := range l.Effects {
				el.Effects = append(el.Effects, convertProperty(fx))
			}
			for _, m := range l.Masks {
				el.Masks = append(el.Masks, convertProperty(m))
			}
			for _, c := range l.Contents {
				el.Contents = append(el.Contents, convertProperty(c))
			}
			for _, a := range l.Audio {
				el.Audio = append(el.Audio, convertProperty(a))
			}
			if l.Text != nil && hasAnimationOrExpression(l.Text) {
				tp := convertProperty(l.Text)
				el.TextProps = &tp
			}
			if l.TextContent != "" {
				exp.Texts = append(exp.Texts, exportText{Composition: item.Name, Layer: int(l.Index), Text: l.TextContent})
			}
			e.Layers = append(e.Layers, el)
		}
	}
	return e
}

func hasAnimationOrExpression(p *aep.Property) bool {
	if p == nil {
		return false
	}
	if p.Animated || p.Expression != "" {
		return true
	}
	for _, sub := range p.Properties {
		if hasAnimationOrExpression(sub) {
			return true
		}
	}
	return false
}

func convertProperty(p *aep.Property) exportProperty {
	ep := exportProperty{
		Name:       p.Name,
		MatchName:  p.MatchName,
		Label:      p.Label,
		Type:       p.PropertyType.String(),
		ValueType:  string(p.ValueType),
		Dimensions: p.Dimensions,
		Value:      p.Value,
		Animated:   p.Animated,
		Expression: p.Expression,
		Arb:        hex.EncodeToString(p.Arb),
		Options:    p.SelectOptions,
		MaskMode:   p.MaskMode,
		Inverted:   p.MaskInverted,
	}
	if len(p.Paths) > 0 {
		ep.Path = toExportPath(p.Paths[0])
	}
	for i, kf := range p.Keyframes {
		var path *exportPath
		if i < len(p.Paths) {
			path = toExportPath(p.Paths[i])
		}
		ep.Keyframes = append(ep.Keyframes, exportKeyframe{
			Time:             kf.Time,
			CompTime:         kf.CompTime,
			Value:            kf.Value,
			InInterpolation:  kf.InInterpolation.String(),
			OutInterpolation: kf.OutInterpolation.String(),
			InSpeed:          kf.InSpeed,
			InInfluence:      kf.InInfluence,
			OutSpeed:         kf.OutSpeed,
			OutInfluence:     kf.OutInfluence,
			InTangent:        kf.InTangent,
			OutTangent:       kf.OutTangent,
			Path:             path,
		})
	}
	for _, sub := range p.Properties {
		ep.Properties = append(ep.Properties, convertProperty(sub))
	}
	return ep
}

func printTree(item *exportItem, depth int) {
	indent := strings.Repeat("  ", depth)
	switch item.Type {
	case "Folder":
		fmt.Printf("%s[Folder] %s (%d items)\n", indent, item.Name, len(item.Children))
		for _, c := range item.Children {
			printTree(c, depth+1)
		}
	case "Composition":
		fmt.Printf("%s[Comp] %s %dx%d @ %.3f fps, %.2fs, %d layers\n", indent, item.Name,
			item.Width, item.Height, item.Framerate, item.Seconds, len(item.Layers))
		for _, l := range item.Layers {
			if l.Text != "" {
				fmt.Printf("%s  #%d %s: %q\n", indent, l.Index, l.Name, l.Text)
			} else {
				fmt.Printf("%s  #%d %s\n", indent, l.Index, l.Name)
			}
		}
	default:
		fmt.Printf("%s[%s] %s %dx%d\n", indent, item.Type, item.Name, item.Width, item.Height)
	}
}

// layerKind names what a layer is. Solids and footage are both "av"; the
// item behind sourceId tells them apart.
func layerKind(l *aep.Layer) string {
	if l.NullLayer {
		return "null"
	}
	return [...]string{"av", "light", "camera", "text", "shape", "model", "av", "mesh"}[l.LayerType&7]
}

// blendModeNames maps the AE SDK PF_Xfer values stored in ldta. Normal (0/2)
// is left out so it is omitted from the JSON.
var blendModeNames = map[byte]string{
	3: "dissolve", 4: "add", 5: "multiply", 6: "screen", 7: "overlay",
	8: "softLight", 9: "hardLight", 10: "darken", 11: "lighten",
	12: "classicDifference", 13: "hue", 14: "saturation", 15: "color",
	16: "luminosity", 17: "stencilAlpha", 18: "stencilLuma",
	19: "silhouetteAlpha", 20: "silhouetteLuma", 21: "luminescentPremul",
	22: "alphaAdd", 23: "classicColorDodge", 24: "classicColorBurn",
	25: "exclusion", 26: "difference", 27: "colorDodge", 28: "colorBurn",
	29: "linearDodge", 30: "linearBurn", 31: "linearLight", 32: "vividLight",
	33: "pinLight", 34: "hardMix", 35: "lighterColor", 36: "darkerColor",
	37: "subtract", 38: "divide",
}

var trackMatteNames = map[byte]string{1: "alpha", 2: "alphaInverted", 3: "luma", 4: "lumaInverted"}
